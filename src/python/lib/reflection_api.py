from docstring_parser import parse
from inspect import getfullargspec
from flask import request, make_response
from django.http import HttpResponse
import os
import json


class ReflectionAPI:
    JSType = {
        "string":      "string",
        "int":      "number",
        "integer":      "number",
        "double":      "number",
        "float":      "number",
        "array":      "object",
        "object":      "object",
        "bool":      "boolean",
        "mixed":       ""
    }

    def __init__(self, url):
        base_attrs = {}
        self._location = url
        for attr in dir(ReflectionAPI):
            base_attrs[attr] = type(getattr(ReflectionAPI, attr))
        obj_attrs = dir(self)
        self._functions = {}
        for attr in obj_attrs:
            obj = getattr(self, attr)
            if type(obj).__name__ == 'method' and attr not in base_attrs:
                self._functions[attr] = self.analize_function(obj)
                self._functions[attr]['ref'] = obj
        self._location = ""

    @classmethod
    def __Python_Type_To_JSType(cls, pythonType):
        if not pythonType in cls.JSType:
            return ""
        else:
            return f"{{{cls.JSType[pythonType]}}}"

    @classmethod
    def __JSDoc(cls, docArray):
        ret = "/**\n"

        def commentBlock(blockStr):
            return "\n".join(
                map(
                    lambda l: f" * {l}",
                    blockStr.split("\n")
                )
            )
        ret += f"{commentBlock(docArray['summary'])}\n"
        for param in docArray["params"]:
            paramStr = "@param " + \
                cls.__Python_Type_To_JSType(param["type"].lower()) +\
                " " + param["name"] + " " + param["summary"]
            ret += commentBlock(paramStr) + "\n"
        if "return" in docArray \
                and type(docArray['return']).__name__ == 'dict':
            returnStr = "@return " + \
                cls.__Python_Type_To_JSType(
                    docArray["return"]["type"].lower()
                ) + \
                " " + docArray["return"]["summary"]
            ret += commentBlock(returnStr) + "\n"
        ret += " */"
        return ret

    @classmethod
    def __HTMLDoc(cls, docArray):
        if not docArray:
            raise Exception("Warning: docArray is a None object")
        ret = "<p class='indented'>" + \
            docArray["summary"].replace("\n", "<br />") + "</p>"
        ret += "<h4>Parameters: </h4>"
        if len(docArray["params"]):
            ret += "<ul>"
            for param in docArray["params"]:
                paramStr = "<li><b><i>" + \
                    param["type"].lower() + \
                    "</i> " + param["name"] + "</b><p class='indented'>" + \
                    param["summary"] + "</p></li>"
                ret += paramStr.replace("\n", "<br />")
            ret += "</ul>"
        else:
            ret += "<p>No parameters</p>"
        ret += "<h4>Return Value: </h4>"

        if "return" in docArray \
                and type(docArray['return']).__name__ == 'dict':
            retStr = "<ul><li>"
            if "type" in docArray["return"]:
                retStr += "<b><i>" + \
                    docArray["return"]["type"].lower() + \
                    "</i></b>"
            if "summary" in docArray["return"]:
                "<p>" + \
                    docArray["return"]["summary"] + \
                    "</p>"
            retStr += "</li></ul>"
            ret += retStr.replace("\n", "<br />")
        else:
            ret += "<p>No Return value</p>"
        return ret

    @classmethod
    def __parse_DocComment(cls, comment):
        doc = parse(comment)
        summary = doc.short_description
        if hasattr(doc, 'long_description') and doc.long_description is not None:
            summary += "\n\n" + doc.long_description
        params = list(map(
            lambda param: {
                "type": param.type_name,
                "name": param.arg_name,
                "summary": param.description
            },
            doc.params
        ))
        returns = None
        if doc.returns:
            returns = {
                "type": doc.returns.type_name,
                "name": doc.returns.return_name,
                "summary": doc.returns.description
            }
        return {
            "summary": summary,
            "params": params,
            "return": returns
        }

    @classmethod
    def analize_function(cls, func):
        doc_comment = func.__doc__
        name = func.__name__
        params = getfullargspec(func).args
        params.pop(0)  # Remove 'self' from args
        return {
            "name": name,
            "DocComment": cls.__parse_DocComment(doc_comment),
            "params": params,
        }

    @staticmethod
    def get_template(file_name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(dir_path, file_name)
        return open(template_path).read()

    @classmethod
    def get_html_function_template(cls):
        return cls.get_template("function-template.html")

    def get_js_function_template(cls):
        return cls.get_template("function-template.js")

    @classmethod
    def get_html_doc_template(cls):
        return cls.get_template("doc-templete.html")

    @classmethod
    def get_module_template(cls):
        return cls.get_template("module-header.js")

    @staticmethod
    def use_template(template, params):
        for param in params:
            template = template.replace(param, params[param])
        return template

    def reflectJS(self):
        output = self.use_template(self.get_module_template(), {
            "pathToEndpoint": self._location + "?type=api"
        })

        for function_name in self._functions:
            ServerFunction = self._functions[function_name]
            output += self.__JSDoc(ServerFunction["DocComment"]) + "\n"
            argList = ", ".join(ServerFunction["params"])
            output += self.use_template(self.get_js_function_template(), {
                "functionName": ServerFunction["name"],
                "argList": argList
            })
            output += f"\nexport {{{ServerFunction['name']}}};\n\n"
        return output

    def reflectHTML(self):
        content = ""
        for function_name in self._functions:
            ServerFunction = self._functions[function_name]
            definition = f"<b>{ServerFunction['name']}</b>("
            params = ServerFunction["params"]
            definition += f"<i>{', '.join(params)}</i>"
            definition += ")"
            description = self.__HTMLDoc(ServerFunction["DocComment"])
            content += self.use_template(self.get_html_function_template(), {
                "[[Function-Name]]": ServerFunction["name"],
                "[[Function-Definition]]": definition,
                "[[Function-Description]]": description
            })
        return self.use_template(self.get_html_doc_template(), {
            "[[Endpoint-Name]]": self.__class__.__name__,
            "[[Functions-List]]": content,
            "[[Module-Link]]": self._location + '?type=js'
        })

    def flask_view(self):
        view_type = request.args.get('type')
        if not view_type:
            view_type = 'html'
        view_type = view_type.upper()
        if view_type == 'API' and request.method == 'POST':
            data = request.get_json()
            response = []
            for call in data:
                if "name" in call and call['name'] in self._functions:
                    response.append(
                        self._functions[call['name']]['ref'](*call['params']))
                else:
                    response.append(None)
            response_obj = make_response(json.dumps(response))
            response_obj.headers["Content-Type"] = "application/json"
            return response_obj
        elif view_type == 'JS':
            response = make_response(self.reflectJS())
            response.headers["Content-Type"] = "text/javascript"
            return response
        else:
            return self.reflectHTML()

    def django_view(self, request):
        view_type = request.GET.get('type')
        if not view_type:
            view_type = 'html'
        view_type = view_type.upper()
        if view_type == 'API' and request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            response = []
            for call in data:
                if "name" in call and call['name'] in self._functions:
                    response.append(
                        self._functions[call['name']]['ref'](*call['params']))
                else:
                    response.append(None)
            return HttpResponse(
                json.dumps(response),
                content_type='application/json; charset=utf8'
            )
        elif view_type == 'JS':
            return HttpResponse(self.reflectJS(), content_type="text/javascript")
        else:
            return HttpResponse(self.reflectHTML())
