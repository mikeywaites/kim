``Kim``
=============

Kim is a serialization and marshaling framework for orchestrating the structure and flow of JSON data into and out of your REST API.


Example
-------
.. code-block:: python

    class UserMapper(Mapper):
        __type__ = User

        id = field.String(read_only=True)
        name = field.String()
        age = field.Integer(min=18)
        is_admin = field.Boolean(required=False, default=False)
        company = field.Nested(CompanyMapper)

        __roles__ = {
            'overview': whitelist('id', 'name', 'is_admin')
        }

To get started, see quickstart_.

Contributing
-------------
Kim comes bundled with two Dockerfiles for py2 and py3.  Running the test suite is expalined briefly below.


Mac OSX
-------

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
