from docstring_parser import parse
from inspect import getfullargspec
from flask import request, make_response
from django.http import HttpResponse
from typing import Optional, TypedDict
import os
import json


class FunctionIdentifier(TypedDict):
    name: Optional[str]
    type_name: Optional[str]
    summary: Optional[str]
    default: Optional[str]


class FunctionDocumentation(TypedDict):
    summary: Optional[str]
    params: Optional[list[FunctionIdentifier]]
    returns: Optional[FunctionIdentifier]


class FunctionStructure(TypedDict):
    name: str
    params: list[str]
    DocComment: Optional[FunctionDocumentation]


class EndpointFunction(TypedDict):
    name: str
    params: list[str]
    DocComment: Optional[FunctionDocumentation]
    ref: function


class ImplicitEndpoint:
    JSType = {
        "string":      "string",
        "int":      "number",
        "integer":      "number",
        "double":      "number",
        "float":      "number",
        "array":      "object",
        "object":      "object",
        "bool":      "boolean",
        "mixed":       "any"
    }

    def __init__(self, url: str):
        base_attrs: dict = {}
        self._location: str = url
        for attr in dir(ImplicitEndpoint):
            base_attrs[attr] = type(getattr(ImplicitEndpoint, attr))
        obj_attrs: list[str] = dir(self)
        self._functions: dict[str, EndpointFunction] = {}
        for attr in obj_attrs:
            obj = getattr(self, attr)
            if type(obj).__name__ == 'method' and attr not in base_attrs:
                self._functions[attr] = self.__analize_function(obj)
                self._functions[attr]['ref'] = obj

    @classmethod
    def __Python_Type_To_JSType(cls, pythonType: str) -> str:
        pythonType = pythonType.lower()
        if '|' in pythonType:
            type_list = pythonType.split('|')
        else:
            type_list = [pythonType]
        for i in range(type_list):
            if not type_list[i] in cls.JSType:
                type_list[i] = "UnknownType"
            else:
                type_list[i] = f"{{{cls.JSType[type_list[i]]}}}"
        return ' | '.join(type_list)

    @classmethod
    def __JSDoc(cls, func_doc: FunctionDocumentation) -> str:
        ret = "/**\n"

        def commentBlock(blockStr):
            return "\n".join(
                map(
                    lambda l: f" * {l}",
                    blockStr.split("\n")
                )
            )
        ret += f"{commentBlock(func_doc['summary'])}\n"
        for param in func_doc["params"]:
            paramStr = "@param " + \
                cls.__Python_Type_To_JSType(param["type_name"]) +\
                " " + param["name"] + " " + param["summary"]
            ret += commentBlock(paramStr) + "\n"
        if "returns" in func_doc \
                and type(func_doc['returns']).__name__ == 'dict':
            returnStr = "@return " + \
                cls.__Python_Type_To_JSType(
                    func_doc["returns"]["type_name"]
                ) + \
                " " + func_doc["returns"]["summary"]
            ret += commentBlock(returnStr) + "\n"
        ret += " */"
        return ret

    @classmethod
    def __HTMLDoc(cls, func_doc: FunctionDocumentation) -> str:
        ret = "<p class='indented'>" + \
            func_doc["summary"].replace("\n", "<br />") + "</p>"
        ret += "<h4>Parameters: </h4>"
        if len(func_doc["params"]):
            ret += "<ul>"
            for param in func_doc["params"]:
                paramStr = "<li><b><i>" + \
                    param["type_name"] + \
                    "</i> " + param["name"] + "</b><p class='indented'>" + \
                    param["summary"] + "</p></li>"
                ret += paramStr.replace("\n", "<br />")
            ret += "</ul>"
        else:
            ret += "<p>No parameters</p>"
        ret += "<h4>Return Value: </h4>"

        if "returns" in func_doc \
                and type(func_doc["returns"]).__name__ == 'dict':
            retStr = "<ul><li>"
            if "type" in func_doc["return"]:
                retStr += "<b><i>" + \
                    func_doc["return"]["type"].lower() + \
                    "</i></b>"
            if "summary" in func_doc["return"]:
                "<p>" + \
                    func_doc["return"]["summary"] + \
                    "</p>"
            retStr += "</li></ul>"
            ret += retStr.replace("\n", "<br />")
        else:
            ret += "<p>No Return value</p>"
        return ret

    @classmethod
    def __parse_DocComment(cls, comment: str) -> FunctionDocumentation:
        doc = parse(comment)
        summary = doc.short_description
        if hasattr(doc, 'long_description') and doc.long_description is not None:
            summary += "\n\n" + doc.long_description
        params = list(map(
            lambda param: {
                "type_name": param.type_name,
                "name": param.arg_name,
                "summary": param.description
            },
            doc.params
        ))
        returns = None
        if doc.returns:
            returns = {
                "type_name": doc.returns.type_name,
                "name": doc.returns.return_name,
                "summary": doc.returns.description
            }
        return {
            "summary": summary,
            "params": params,
            "returns": returns
        }

    @classmethod
    def __analize_function(cls, func: function) -> FunctionStructure:
        doc_comment: str = func.__doc__
        name: str = func.__name__
        params: list[str] = getfullargspec(func).args
        params.pop(0)  # Remove 'self' from args
        return {
            "name": name,
            "DocComment": cls.__parse_DocComment(doc_comment),
            "params": params,
        }

    @staticmethod
    def __get_template(file_name: str) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        template_path = os.path.join(dir_path, file_name)
        return open(template_path).read()

    @classmethod
    def __get_html_function_template(cls) -> str:
        return cls.__get_template("function-template.html")

    def __get_js_function_template(cls) -> str:
        return cls.__get_template("function-template.js")

    @classmethod
    def __get_html_doc_template(cls) -> str:
        return cls.__get_template("doc-templete.html")

    @classmethod
    def __get_module_template(cls) -> str:
        return cls.__get_template("module-header.js")

    @staticmethod
    def __use_template(template: str, params: dict[str, str]) -> str:
        for param in params:
            template = template.replace(param, params[param])
        return template

    def reflectJS(self):
        output = self.__use_template(self.__get_module_template(), {
            "pathToEndpoint": self._location + "?type=api"
        })

        for function_name in self._functions:
            ServerFunction = self._functions[function_name]
            output += self.__JSDoc(ServerFunction["DocComment"]) + "\n"
            argList = ", ".join(ServerFunction["params"])
            output += self.__use_template(self.__get_js_function_template(), {
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
            content += self.__use_template(self.__get_html_function_template(), {
                "[[Function-Name]]": ServerFunction["name"],
                "[[Function-Definition]]": definition,
                "[[Function-Description]]": description
            })
        return self.__use_template(self.__get_html_doc_template(), {
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
        self.request = request
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
