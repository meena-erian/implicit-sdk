<?php

class ServerEndpoint
{
    /**
     * @var array $_functions List of server functions.
     */
    private $_functions = array();

    /**
     * @var array $PHP_Type_To_JSType used to convert PHP 
     * data type names to their alternative JavaScript types.
     */
    private static $PHP_Type_To_JSType = array(
        "string"        =>      "string",
        "int"           =>      "number",
        "integer"       =>      "number",
        "double"        =>      "number",
        "float"         =>      "number",
        "array"         =>      "object",
        "object"        =>      "object",
        "bool"          =>      "boolean"
    );

    /**
     * Validate a function object. Used before adding it to a ServerEndpoint.
     * 
     * @param 
     * @param string $f The name of the function to be validated.
     * @return bool True on success, false on failure.
     */
    private static function validate_function($f)
    {
        return function_exists($f);
    }

    /**
     * A function that generates JavaScript JSDoc comment from 
     *  a documentation array of parsed PHPDoc comment.
     * 
     * @param array $docArray DocComment array as returned from 
     * the parse_DocComment() function.
     * @return string Generated JSDoc comment string.
     */
    private static function JSDoc($docArray)
    {
        $return = "/**\n";
        
        $commentBlock = function ($blockStr){
            $commentLines = function ($line) {
                return " * " . $line;
            };
            return implode(
                "\n", 
                array_map(
                    $commentLines,
                    explode("\n", $blockStr)
                )
            );
        };
        $return .= $commentBlock($docArray["summary"]) . "\n";
        foreach($docArray["params"] as $param){
            $paramStr = "@param {" . 
                self::$PHP_Type_To_JSType[strtolower($param["type"])] .
            "} " . $param["name"] . " " . $param["summary"];
            $return .= $commentBlock($paramStr) . "\n";
        }
        if(isset($docArray["return"])){
            $returnStr = "@return {" .
                self::$PHP_Type_To_JSType[strtolower($docArray["return"]["type"])] .
            "} " . $docArray["return"]["summary"];
            $return .= $commentBlock($returnStr) . "\n";
        }
        $return  .= " */";
        return $return;
    }

    /**
     * A function that parses a PHPDocComment string into a structured array
     * 
     * @param string $comment The DocComment string.
     * @return array The structured information found in the DocComment.
     */
    private static function parse_DocComment($comment)
    {

        // Remove the "/**" and "*/"
        $comment = trim(substr($comment, 3, -2), "\r\n");

        // Function to remove the " * " at the beginning of each line
        $trimDocLine = function ($line) {
            return ltrim($line, " *");
        };

        // Remove the all " * " at the beginning of every line
        $comment = implode(
            "\n",
            array_map($trimDocLine, explode("\n", $comment))
        );

        // Split the comment based on Doc tags
        $comment = array_map("trim", explode("\n@", $comment));

        // The summary is the first part
        $summary = array_shift($comment);

        $params = array();
        $return = null;

        // Function to convert the string of a @param or @return doc tag
        //  into a structured array of param info
        $parse_param = function ($str) {
            $ret = preg_split("/[\s,]+/", $str, 3);
            $result = array("type" => $ret[0]);
            if (substr($ret[1], 0, 1) === "$") {
                $result["name"] = ltrim($ret[1], "$");
                if (isset($ret[2])) $result["summary"] = $ret[2];
            } else {
                if (isset($ret[2])) $ret[1] = $ret[1] . " " . $ret[2];
                $result["summary"] = $ret[1];
            }
            return $result;
        };

        // Find all params and the return
        for ($i = 0; $i < count($comment); $i++) {
            if (strncmp($comment[$i], "param", 5) === 0) {
                $params[] = $parse_param(trim(substr($comment[$i], 5)));
            } elseif (strncmp($comment[$i], "return", 6) === 0) {
                $return = $parse_param(trim(substr($comment[$i], 6)));
            }
        }

        return array(
            "summary" => $summary,
            "params" => $params,
            "return" => $return
        );
    }

    /**
     * This funciton finds a user function and its PHPDoc comment 
     * and analizes them to generate a function info object.
     * 
     * @param string $f Function name.
     * @return mixed Function info array of false on failure. 
     */
    private static function analize_function($f)
    {
        $rf = new ReflectionFunction($f);
        return array(
            "name" => $rf->getName(),
            "DocComment" => self::parse_DocComment($rf->getDocComment()),
            "params" => $rf->getParameters()
        );
    }

    /**
     * Define a new server function.
     * 
     * @param string $f Name of a user function to be defined in the ServerEndpoint.
     * @return bool True on success, false on failure.
     */
    public function add_function($f)
    {
        if (!self::validate_function($f)) return false;
        $this->_functions[$f] = self::analize_function($f);
    }

    /**
     * Listens to requests containing server commands, 
     * performs the commands, respond to them and closes the connection.
     */
    public function listen()
    {
        $data = file_get_contents('php://input');
        if(strlen($data)){
            $data = json_decode($data, false, 10);
            if(is_array($data)){
                header("Content-Type: application/json");
                $response = array();
                foreach($data as $call){
                    if(isset($call->name) && isset($this->_functions[$call->name])){
                        $response[] = 
                            call_user_func_array($call->name,$call->params);
                    }
                    else $response[] = "Fuck";
                }
                die(json_encode($response));
            }
        }
    }

    /**
     * This function generates a JavaScript file that represents the client-side
     *  module interface of the api.
     * 
     * @param string $file The path/name of the output file to which the JS module 
     * will be printed.
     * @return mixed True on sccess, null if the file is already printed, 
     * and false on error
     */
    public function reflectJS($file = "api.js")
    {
        $output = file_get_contents("module-header.js");
        foreach ($this->_functions as $ServerFunction) {
            $output .= self::JSDoc($ServerFunction["DocComment"]) . "\n";

            $argList = 
            implode(", ",
                array_map(
                    function($ReflectionParameter)
                    {return $ReflectionParameter->name;},
                    $ServerFunction["params"]
                )
            );

            $output .= 
            str_replace(
                "argList",
                $argList,
                str_replace(
                    "functionName", 
                    $ServerFunction["name"],
                    file_get_contents("function-template.js")
                )
            );

            $output .= "\nexport {" . $ServerFunction["name"] . "};\n\n";
        }
        file_put_contents($file, $output);
    }

    public function print_functions()
    {
        var_dump($this->_functions);
    }
}
