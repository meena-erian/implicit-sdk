class ReflectionAPI {
    _functions = []
    _location = ""

    /**
     * A function that generates JavaScript JSDoc comment from 
     *  a documentation array of parsed PHPDoc comment.
     * 
     * @param array $docArray DocComment array as returned from 
     * the parse_DocComment() function.
     * @return string Generated JSDoc comment string.
     */
    JSDoc(docArray) {
        // TODO: Add function implementation 
    }
    /**
     * A function that generates HTML description from
     *  a documentation array of parsed PHPDoc comment.
     * 
     * @param array $docArray DocComment array as returned from 
     * the parse_DocComment() function.
     * @return string Generated HTML string.
     */
    HTMLDoc(docArray){
        // TODO: Add function implementation 
    }

    /**
     * A function that parses a PHPDocComment string into a structured array
     * 
     * @param string $comment The DocComment string.
     * @return array The structured information found in the DocComment.
     */
    parse_DocComment(comment){
        // TODO: Add function implementation 
    }

    /**
     * This funciton finds a child method and its PHPDoc comment 
     * and analizes them to generate a function info object.
     * 
     * @param string $m Method name.
     * @return mixed Function info array of false on failure. 
     */
    analize_function(m){
        console.log(m)
        // TODO: Add function implementation 
        return {
            name: m,
            DocComment: this[m].toString(),
            params: null,
            ref: this[m]
        }
    }

    /**
     * This function generates a JavaScript file that represents the client-side
     *  module interface of the api.
     * 
     * @return string The generated JavaScript module.
     */
    reflectJS(){
        // TODO: Add function implementation 
    }

    /**
     * This function generates an HTML documentation page for the API endpoint
     * 
     * @return string The generated HTML documentation
     */
    reflectHTML(){
        // TODO: Add function implementation 
    }

    constructor() {
        var methods = Object.getOwnPropertyNames(Object.getPrototypeOf(this));
        methods.shift();
        for(var i=0; i<methods.length; i++){
            this._functions.push(
                this.analize_function(methods[i])
            );
        }
    }
}

export default ReflectionAPI;

/**
 * - [] Retrive DocComment of each function
 * - [] List arguments list of each function
 * - [] Parse DocComments of each function 
 */