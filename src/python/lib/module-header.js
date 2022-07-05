/**
 * @file Reflection API Auto generated JS module.
 * @see https://github.com/meena-erian/reflection-api
 * @author Menas Erian
 * @copyright (C) 2020 Menas Erian
 */


 function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');



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
      xhttp.setRequestHeader("X-CSRFToken", csrftoken);
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


