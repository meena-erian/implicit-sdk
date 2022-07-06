/**
 * @file implicit SDK Auto generated JS module.
 * @see https://github.com/meena-erian/implicit-sdk
 * @author Menas (Meena) Erian
 * @copyright (C) 2022 Menas (Meena) Erian
 */


 var call = {
  timeout: -1,
  stack: [],
  send: function () {
    if (call.stack.length) {
      let s = call.stack;
      call.stack = [];
      var xhttp = new XMLHttpRequest();
      xhttp.open("POST", "pathToEndpoint");
      xhttp.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhttp.onload = function (e) {
        call.resolve(s, JSON.parse(e.target.response));
      };
      xhttp.onerror = function () {
        call.reject(s);
      };
      xhttp.send(JSON.stringify(s));
      console.log(JSON.stringify(s, null, 2));
    }
  },
  resolve: function (callStack, serverResponse) {
    serverResponse.forEach((element, i) => {
      callStack[i].promise.resolve(element);
    });
    console.log(
      "Calles resolved:\n--------------\n",
      "Request:\n",
      JSON.stringify(callStack, null, 2),
      "\n--------------\n",
      "Response\n",
      JSON.stringify(serverResponse, null, 2)
    );
  },
  reject: function (callStack) {
    callStack.forEach((c) => {
      c.promise.reject("Connection failed");
    });
  },
};