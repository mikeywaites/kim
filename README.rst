# Kim

Kim is a framework for orchestrating the structure and flow of JSON data in to and out of your REST API.


## Contributing

Kim comes bundled with two Dockerfiles for py2 and py3.  Running the test suite is expalined briefly below.


### Mac OSX

Firstly install docker-toolbox available [here](https://www.docker.com/products/docker-toolbox). Once toolbox is installed we need to create a machine using `docker-machine`.

`$ docker-machine create --driver virtualbox kim2`

Run the following command to make sure the new machine is available and ready for use.

`$ docker-machine ls`

```
docker-machine ls
NAME   ACTIVE   DRIVER       STATE     URL                         SWARM   DOCKER    ERRORS
kim2   -        virtualbox   Running   tcp://192.168.99.100:2376           v1.10.1
```

Now we need to connect our shell to the new machine.  We need to run the following command every time we start a enw shell or restart the docker machine.

`$ eval "$(docker-machine env kim2)"`


Now we can run commands against our docker machine.

`docker-compose run py2`

`docker-compose run py3`


## Quickstart
* simple flask project with user and Blog mappers to display a full working example
of serializing and marshaling data

# Guide

## Introduction
* introduce the project and example repo.
    explain what the end product should produce

## Defining mappers.
* link to api documentation
* define your first mappers.
    basic blog mapper
    basic user mapper


## Nesting data
* link to api documentation for Nested field.
* show example of nesting the user mapper under blog objects
* implement getter for user

## Serializing data (output)
* link to api documentation
* show example of serializing many blog posts
* show example of serializing a single post

## Changing what data is available (Roles)
* link to api documentation
* link to advanced roles usage docs
* define a role on blog
* define a fole on user
* show example of roles when serializing.

## Custom fields
* introduce concept of pipelines
* define customer ArrowDateField
    custom serialize pipeline
    custom marshal pipeline
    custom field opts
    custom error_msgs


## Collections
* link to api docs
* define new post mapper
* define Nested collection field for post readers

## Marshaling (input)
* link to api documentatin
* show example of marshaling data
* limiting available fields
    read_only fields
    roles
* validation
    custom pipes
    validate() method
* create in place
* update in place

## Marshaling partial objects (.partial())
* TBC




