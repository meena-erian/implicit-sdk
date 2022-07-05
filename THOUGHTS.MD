# The following has to be decided for unified interface

1. How to integrate it with a python app regardless of which framework or request handling method is being used?
2. How to integrate it with authentication providers?
3. How to add a layer of encryption for enhanced security?

# The following has already been decided

1. An instance of the class represents one or more function/s under only one endpoint
2.  



# Code requirments per programming languages

This project needs to do the following:

1. Compile the list of server side functions to extract the following information for each function
    - [X]  Function name
    - [X]  Function parameters
    - [X]  Function DocString
2. The code is required to parse the DocString of every function and extract its details for each programming language:
    - [X] PHP
    - [ ] JavaScript
    - [X] Python
3. The code is required to translate the parsed DocString into a JavaScript DocString in the client side. 
    - [X] PHP to JS DocString Translation
    - [X] JavaScript to JavaScript DocString Translation
    - [X] Python to JavaScript DocString Translation 



Givens and Challenges for this project

## Givens

1. The Client side programming language will always be JavaScript no matter what
2. The communication protocol will be either HTTP[S] or websockets

## Challenges

1. Reading DocString from NodeJS server side and parsing it
3. Implementing authentication and authorization in the API