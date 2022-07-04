# reflection-api

With reflection API you don't have to code any Client-Server communication APIs (RESTful, SOAP, GraphQL, RPC)

Just use any supported server-side programming language to define the API methods and a client-side SDK is automatically generated so that all you need to do on the client-side is to import a JavaScript module file. Save your time coding the actual logic of your app rather than writing redundant code just to establish client-server communication.


<!--
## Supported Server-Side Languages

- PHP (Old version of the API)
- JavaScript (Under development)
- Python (Under development)

## Server side coding patterns

When writing any server side code, regardless of what kind of application or what is it for, usually it's meant just meant to provide a way for the client-side of an application to perform CRUD operations on one or more data models in a database.

The reflection api provides out-of-the-box classes for such use case and much more.

- Model Gateway: A model gateway in the reflcetion api is a class that allowes you to expose a database entity to the client-side so that clients can interact with data in that model and perform CRUD operations. it also allowes you to manage permissions and define who can do what to what.

## Challenges

| Challenge      | Description      | Suggested Solution|
|----------------|------------------|-------------------|
| Multilinuality | In order to complete the Model Gateway, a user authentication system is required. And that's only available in Python Django. | Start with Python Django only for now |
| Datatype translation | Python datatypes mentioned in docComments need to be traslated into juavascript. | Use a dictionary translation for now |
| Permission Managment | Even with django permission managment we can hardly control what actions each user or group of users is allowed to perform on a particular model and the rule applies to the entire model with all records on it. For exaple, if you want to allow a user to edit only the posts created by them and not anybody else's posts, this is beyond what django's built in permission managment system can do. | Create a patch for Django framework as a custom Permissions model which still depends on the same User and Groups built-in tables | 
| Permission Managment / Record groups | It can be challenging to create a permissions model that allowes us to set permission per a specific set of records, mainly |

-->