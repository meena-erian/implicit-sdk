<?php

/**
 * Reflection API is a A lite, high-performance and
 *  super easy-to-use and manage PHP & JavaScript 
 *  Client-Server API
 * @see https://github.com/meena-erian/reflection-api
 * @author Menas Erian
 * @copyright (C) 2020 Menas Erian
 */

class Reflection_API
{
    /**
     * @var array $_functions List of server functions.
     */
    private $_functions = array();

    /**
     * @var string $_location The absolute link to the api.
     */
    private $_location = "";

    /**
     * @var array $JSType used to convert PHP 
     * data type names to their alternative JavaScript types.
     */
    private static $JSType = array(
        "string"        =>      "string",
        "int"           =>      "number",
        "integer"       =>      "number",
        "double"        =>      "number",
        "float"         =>      "number",
        "array"         =>      "object",
        "object"        =>      "object",
        "bool"          =>      "boolean",
        "mixed"            =>        ""
    );

    /**
     * Converts php type names to exuivelant JS type for
     *  the @param keyword
     *
     * @param string @php A php type
     * @return mixed the resulted JS type
     */
    private static function PHP_Type_To_JSType($php)
    {
        $js = self::$JSType[$php];
        if (!isset($js)) return false;
        if (strlen($js)) return "{$js}";
        return "";
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

        $commentBlock = function ($blockStr) {
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
        foreach ($docArray["params"] as $param) {
            $paramStr = "@param " .
                self::PHP_Type_To_JSType(strtolower($param["type"])) .
                " " . $param["name"] . " " . $param["summary"];
            $return .= $commentBlock($paramStr) . "\n";
        }
        if (isset($docArray["return"])) {
            $returnStr = "@return " .
                self::PHP_Type_To_JSType(
                    strtolower($docArray["return"]["type"])
                ) .
                " " . $docArray["return"]["summary"];
            $return .= $commentBlock($returnStr) . "\n";
        }
        $return  .= " */";
        return $return;
    }

    /**
     * A function that generates HTML description from
     *  a documentation array of parsed PHPDoc comment.
     * 
     * @param array $docArray DocComment array as returned from 
     * the parse_DocComment() function.
     * @return string Generated HTML string.
     */
    private static function HTMLDoc($docArray)
    {
        $return = "<p class='indented'>" . str_replace("\n", "<br />", $docArray["summary"]) . "</p>";

        $return .= "<h4>Parameters: </h4>";
        if (count($docArray["params"])) {
            $return .= "<ul>";
            foreach ($docArray["params"] as $param) {
                $paramStr = "<li><b><i>" .
                    strtolower($param["type"]) .
                    "</i> " . $param["name"] . "</b><p class='indented'>" .
                    $param["summary"] . "</p></li>";
                $return .= str_replace("\n", "<br />", $paramStr);
            }
            $return .= "</ul>";
        } else {
            $return .= "<p>No parameters</p>";
        }
        $return .= "<h4>Return Value: </h4>";

        if (isset($docArray["return"])) {
            $returnStr = "<ul><li><b><i>" .
                strtolower($docArray["return"]["type"]) .
                "</i></b><p>" . $docArray["return"]["summary"] .
                "</p></li></ul>";
            $return .= str_replace("\n", "<br />", $returnStr);
        } else {
            $return .= "<p>No Return value</p>";
        }
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
     * This funciton finds a child method and its PHPDoc comment 
     * and analizes them to generate a function info object.
     * 
     * @param string $m Method name.
     * @return mixed Function info array of false on failure. 
     */
    private static function analize_function($m)
    {
        $rm = new ReflectionMethod(get_called_class(), $m);
        return array(
            "name" => $rm->getName(),
            "DocComment" => self::parse_DocComment($rm->getDocComment()),
            "params" => $rm->getParameters()
        );
    }

    /**
     * Listens to requests containing server commands, 
     * performs the commands, respond to them and closes the connection.
     */
    public function listen()
    {
        $data = file_get_contents('php://input');
        if (strlen($data)) {
            $data = json_decode($data, false, 10);
            if (is_array($data)) {
                header("Content-Type: application/json");
                $response = array();
                foreach ($data as $call) {
                    if (isset($call->name) && isset($this->_functions[$call->name])) {
                        $response[] = call_user_method_array($call->name, $this, $call->params);
                    } else $response[] = null;
                }
                die(json_encode($response));
            }
        }
    }

    /**
     * This function generates a JavaScript file that represents the client-side
     *  module interface of the api.
     * 
     * @return string The generated JavaScript module.
     */
    public function reflectJS()
    {
        $output = str_replace(
            "pathToEndpoint",
            $this->_location . "?type=api",
            file_get_contents(__DIR__ . "/module-header.js")
        );

        foreach ($this->_functions as $ServerFunction) {
            $output .= self::JSDoc($ServerFunction["DocComment"]) . "\n";

            $argList =
                implode(
                    ", ",
                    array_map(
                        function ($ReflectionParameter) {
                            return $ReflectionParameter->name;
                        },
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
                        file_get_contents(__DIR__ . "/function-template.js")
                    )
                );

            $output .= "\nexport {" . $ServerFunction["name"] . "};\n\n";
        }
        return $output;
    }

    /**
     * This function generates an HTML documentation page for the API endpoint
     * 
     * @return string The generated HTML documentation
     */
    public function reflectHTML()
    {
        $content = "";
        foreach ($this->_functions as $ServerFunction) {
            //$output .= self::JSDoc($ServerFunction["DocComment"]) . "\n";
            $name = $ServerFunction["name"];
            $definition = "<b>$name</b>(";
            foreach ($ServerFunction["params"] as $key => $param) {
                if ($key) $definition .= ", ";
                $definition .= "<i>$param->name</i>";
            }
            $definition .= ")";

            $description = self::HTMLDoc($ServerFunction["DocComment"]);

            $content .=
                str_replace(
                    "[[Function-Description]]",
                    $description,
                    str_replace(
                        "[[Function-Definition]]",
                        $definition,
                        str_replace(
                            "[[Function-Name]]",
                            $ServerFunction["name"],
                            file_get_contents(__DIR__ . "/function-template.html")
                        )
                    )
                );
        }
        return
            str_replace(
                "[[Module-Link]]",
                $this->_location . "?type=js",
                str_replace(
                    "[[Functions-List]]",
                    $content,
                    str_replace(
                        "[[Endpoint-Name]]",
                        ucfirst(get_called_class()),
                        file_get_contents(__DIR__ . "/doc-templete.html")
                    )
                )
            );
    }

    /**
     * Initialiezs the reflection processes
     */
    function __construct()
    {
        ($this->_location = $_SERVER["REQUEST_SCHEME"] . "://" . $_SERVER["HTTP_HOST"] . explode("?", $_SERVER["REQUEST_URI"])[0]);
        $child_methods = array_diff(
            get_class_methods(get_called_class()),
            get_class_methods(__CLASS__)
        );
        foreach ($child_methods as $m) {
            $this->_functions[$m] = self::analize_function($m);
        }

        define("METHOD", $_SERVER['REQUEST_METHOD']);
        define("TYPE", strtoupper($_GET["type"]));

        if (TYPE == "API" || METHOD == "POST") {
            $this->listen();
        } elseif (TYPE == "JS" && METHOD == "GET") {
            header("Content-Type: text/javascript");
            echo $this->reflectJS();
        } elseif (METHOD == "GET") { //&& (TYPE == "DOC" /* OR */)){
            echo $this->reflectHTML();
        }
        exit();
    }
}
