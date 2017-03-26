Quickstart
==========

This document walks through the creation of a simple flask based REST API using
SQLAlchemy and Kim. Don't worry if you're not using this exact stack, you should
still be able to follow along.

We're going to define two APIs - a user list API on ``/users`` which will support
GET to list all users, and POST to create a new user. And a user detail API on
``/users/:id`` which will support GET to get a full user object, PUT/PATCH to
update a user and DELETE to remove a user.

Models
------

Our application has two models - Users and Companies. Users belong to a company.

.. code-block:: python

    class User(db.Model):

        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        name = Column(String)
        is_admin = Column(Boolean, default=False)
        company_id = Column(String, db.ForeignKey('company.id'))

        company = db.relationship('Company')


    class Company(db.Model):

        __tablename__ = 'company'
        id = Column(String, primary_key=True)
        name = Column(String)

Mappers
-------

Every object you want to use with Kim needs a ``Mapper``. A Mapper tells Kim how you
want your data structured when serialising (outputting - GET) and marshaling
(inputting - POST/PUT/PATCH). The same Mapper is used in both processes.

Let's define a mapper for a User:

.. code-block:: python

    from kim.mapper import Mapper
    from kim import field

    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()
        is_admin = field.Boolean(required=False, default=False)


Mappers define a ``Field`` for each key in the data they should output. Fields
define the data type of each field and know how to validate their data and coerce
it to and from JSON.

When marshaling, all fields are required by default unless the ``required=False``
flag is passed. If a required field is missing, an error will be raised. If a
field is not required and has not been passed, a ``default`` can be set. These
parameters are used with the ``is_admin`` field.

The ``id`` field is marked as ``read_only=True``. This means that it cannot
be changed when marshaling and will be ignored if it is passed to an API.

We'll add more fields to our User mapper later.

Serializing
-----------

Let's define a flask view to get a user object:

.. code-block:: python

    import json

    @app.route('/users/<string:user_id>')
    def user_detail(user_id):
        # Retrieve user from DB
        user = db.session.query(User).get(user_id)

        # Create an instance of UserMapper
        mapper = UserMapper(obj=user)

        # Get a python dict representing the user
        serialised = mapper.serialize()

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200


Once we've retrieved the right User object from the database, we instatinate an
instance of ``UserMapper`` and pass it the user object. Then simply call
``serialize()`` on it to return a ``dict`` representation of this object. Finally,
convert this dict to JSON and return it.

This API outputs:

.. code-block:: rest

    GET /users/1

    {
        "id": 1,
        "name": "Bob Smith",
        "is_admin": false
    }

Marshaling
----------

Now, let's edit our detail API to accept PUT requests allowing users to be updated.

.. code-block:: python

    from kim.exception import MappingInvalid
    from flask import request

    @app.route('/users/<string:user_id>', methods=['GET', 'PUT'])
    def user_detail(user_id):
        # Retrieve user from DB
        user = db.session.query(User).get(user_id)

        if request.method == 'PUT':

            # Instatiate the mapper and pass the request data
            mapper = UserMapper(obj=user, data=request.json)

            try:
                # Validate the data and get a new User object back
                user = mapper.marshal()
            except MappingInvalid as e:
                # If data did not validate, return a 400
                return json.dumps(e.errors), 400

            # Save the updated User object
            db.session.add(user)
            db.session.commit()

        # Create an instance of UserMapper
        mapper = UserMapper(obj=user)

        # Get a python dict representing the user
        serialised = mapper.serialize()

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200


If a PUT request is given to the API, we create an instance of ``UserMapper``
and, in addition to passing the user object, we now pass the JSON-decoded request
data as well.

Then we call ``.marshal()`` to validate the data and set the fields on a ``User``
model object. The return value is the new ``User`` object.

If the mapper does not validate, for example because a field is missing, a
``MappingInvalid`` exception will be raised. This exception has an ``.errors``
attribute, which can be used to construct an error response. In this example,
we simply return errors as a string.

Once the object has been saved, we follow the same steps as for a GET request
so that a JSON representation of the new state of the object is returned.

.. code-block:: rest

    PUT /users/36
    {
        "name": "Bob Smith",
        "is_admin": true
    }

    {
        "id": 36,
        "name": "Bob Smith",
        "is_admin": true
    }

.. code-block:: rest

    PUT /users/36
    {
        "is_admin": true
    }

    {
        "name": This field is required
    }


Partial Updates
---------------

We can easily convert this API to accept PATCH requests as well as PUT requests.
This means that it can be used to pass just the fields that have changed,
rather than having to pass all fields.

This is achieved by passing the ``partial=True`` flag to the Mapper.

.. code-block:: python

    from kim.exception import MappingInvalid

    @app.route('/users/<string:user_id>', methods=['GET', 'PUT', 'PATCH'])
    def user_detail(user_id):
        # Retrieve user from DB
        user = db.session.query(User).get(user_id)

        if request.method in ['PUT', 'PATCH']:

            # If this is a PATCH, pass partial
            partial = request.method == 'PATCH'

            # Instatiate the mapper and pass the request data
            mapper = UserMapper(obj=user, data=request.json,
                                partial=partial)

            try:
                # Validate the data and get a new User object back
                user = mapper.marshal()
            except MappingInvalid as e:
                # If data did not validate, return a 400
                return json.dumps(e.errors), 400

            # Save the updated User object
            db.session.add(user)
            db.session.commit()

        # Create an instance of UserMapper
        mapper = UserMapper(obj=user)

        # Get a python dict representing the user
        serialised = mapper.serialize()

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200


This works exactly the same as a PUT but if ``partial==True``, an
exception will not be raised if fields are missing.

.. code-block:: rest

    PUT /users/36
    {
        "is_admin": true
    }

    {
        "id": 36,
        "name": "Bob Smith",
        "is_admin": true
    }


Nested objects
--------------

Let's add a nested company object to our user object, so it's easy to see
which company a user belongs to. We can do this using a ``Nested`` field and
pointing it at another mapper.

.. code-block:: python

    from kim.mapper import Mapper
    from kim import field

    class CompanyMapper(Mapper):
        __type__ = Company

        id = field.Integer(read_only=True)
        name = field.String()


    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()
        is_admin = field.Boolean(required=False, default=False)
        company = field.Nested(CompanyMapper)


You can pass any other mapper to a Nested field, and have as many levels of
nesting as you want.

Now when output a user, it's company will be automatically nested within it:

.. code-block:: rest

    GET /users/36

    {
        "id": 36,
        "name": "Bob Smith",
        "is_admin": false,
        "company": {
            "id": 5,
            "name": "Acme Corp"
        }
    }



Marshaling nested objects
-------------------------

Now we've got a nested Company object, we need to be able to validate this field
when marshaling to ensure we a valid company is being set.

For example, if a PUT request was made like this:

.. code-block:: rest

    PUT /users/36
    {
        "name": "Bob Smith",
        "is_admin": true,
        "company": {
            "id": 43
        }
    }

We need to ensure that a company with ID 43 exists and in many cases applications
will want to make security checks here to ensure this user is allowed to use this
company.

We make these checks with a ``getter`` function. A getter function is responsible
for taking the data passed into the nested object and returning a database
object. If the object is not found or not permitted to be accessed, it should
return None, which will cause a validation error to be raised.

.. code-block:: python

    from kim.mapper import Mapper
    from kim import field

    class CompanyMapper(Mapper):
        __type__ = Company

        id = field.Integer(read_only=True)
        name = field.String()


    def company_getter(session):
        if 'id' in session.data:
            return db.session.query(Company).get(session.data['id'])


    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()
        is_admin = field.Boolean(required=False, default=False)
        company = field.Nested(CompanyMapper, getter=company_getter)


We have defined a ``company_getter`` function and passed it to the Nested field.
This function extracts the id field from the data and returns a Company object
if it exists. If it doesn't exist or ``id`` was not passed, it will return None.

This is all you need to work with nested objects when marshaling:

.. code-block:: rest

    PUT /users/36
    {
        "name": "Bob Smith",
        "is_admin": true,
        "company": {
            "id": 43
        }
    }

    {
        "id": 36,
        "name": "Bob Smith",
        "is_admin": true,
        "company": {
            "id": 43,
            "name": "Acme Corp"
        }
    }

But we can't send a company ID that does not exist:

.. code-block:: rest

    PUT /users/36
    {
        "name": "Bob Smith",
        "is_admin": true,
        "company": {
            "id": 999
        }
    }

    {
        "company": "company not found"
    }


Nested objects are very powerful. With additional options, it is also possible
to update the nested object (eg change the company name), create a new object
(create a new company on demand) and use collections of nested objects (allow
Users to have multiple Companies.) See the receipes section for more details.


Serializing collections of objects
----------------------------------

For the users index api on ``/users`` we need to return all the users in the
system - serializing many at once. You can do this using the ``Mapper.many()``
method:

.. code-block:: python

    import json

    @app.route('/users')
    def user_list():
        # Retrieve all users from DB
        users = db.session.query(User).all()

        # Create a many-instance of UserMapper
        mapper = UserMapper.many()

        # Get a list of dicts representing each user
        serialised = mapper.serialize(users)

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200


Instead of instantiating a single UserMapper, we instead call the class method
``UserMapper.many()``. The returned many-instance has the methods ``serialise``
and ``marshal``, which work the same as their single counterparts, but deal
with lists of objects instead of single objects.

Calling ``mapper.serialize(users)`` gives us a list to return.

.. code-block:: rest

    GET /users

    [
        {
            "id": 36,
            "name": "Bob Smith",
            "is_admin": false,
            "company": {
                "id": 43,
                "name": "Acme Corp"
            }
        },
        {
            "id": 54,
            "name": "Dave Jones",
            "is_admin": false,
            "company": {
                "id": 43,
                "name": "Acme Corp"
            }
        },
        {
            "id": 32,
            "name": "Fred Harris",
            "is_admin": false,
            "company": {
                "id": 23,
                "name": "Harris and Son"
            }
        }
    ]

Roles
-----

Our users index API is working well, but we don't need the ``is_admin`` and
``company`` fields as this API should just be an overview.

By using a role, we can restrict the output to just the fields we need, without
creating a new mapper.

First, add the role to the mapper:


.. code-block:: python

    from kim.mapper import Mapper
    from kim import field
    from kim.role import whitelist

    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()
        is_admin = field.Boolean(required=False, default=False)
        company = field.Nested(CompanyMapper, getter=company_getter)

        __roles__ = {
            'overview': whitelist('id', 'name')
        }

A ``whitelist`` role restricts output to just the named fields. Conversely, a
``blacklist`` can be used, which restricts output to all fields except those
named. Roles can be used both when serializing and when marshaling.

Now we can use the role in our view:

.. code-block:: python

    import json

    @app.route('/users')
    def user_list():
        # Retrieve all users from DB
        users = db.session.query(User).all()

        # Create a many-instance of UserMapper
        mapper = UserMapper.many()

        # Get a list of dicts representing each user in overview role
        serialised = mapper.serialize(users, role='overview')

        # Convert it to json and return it as the response
        return json.dumps(serialised), 200

The only change is to pass the role argument to ``serialize()``.  This results
in a list with fewer fields:

.. code-block:: rest

    GET /users

    [
        {
            "id": 36,
            "name": "Bob Smith"
        },
        {
            "id": 54,
            "name": "Dave Jones"
        },
        {
            "id": 32,
            "name": "Fred Harris"
        }
    ]

Creating Objects
----------------

To complete our rest API, we need to allow new users to be created by a POST
to ``/users``. We can do this by editing our list API:

.. code-block:: python

    import json

    @app.route('/users', methods=['GET', 'POST'])
    def user_list():
        if request.method == 'POST':
            # Instatiate the mapper and pass the request data.
            # Do not pass an obj - causes a new User to be created
            mapper = UserMapper(data=request.json)

            try:
                # Validate the data and get a new User object back
                user = mapper.marshal()
            except MappingInvalid as e:
                # If data did not validate, return a 400
                return json.dumps(e.errors), 400

            # Save the updated User object
            db.session.add(user)
            db.session.commit()

            # Now serialise it and return it
            mapper = UserMapper(obj=user)
            serialised = mapper.serialize()

            # Convert it to json and return it as the response
            return json.dumps(serialised), 200

        else:
            # Retrieve all users from DB
            users = db.session.query(User).all()

            # Create a many-instance of UserMapper
            mapper = UserMapper.many()

            # Get a list of dicts representing each user in overview role
            serialised = mapper.serialize(users, role='overview')

            # Convert it to json and return it as the response
            return json.dumps(serialised), 200


The new POST logic is virtually identical to the PUT/PATCH logic, except no
existing ``obj`` is passed to ``UserMapper()``. This causes a new object of
type ``UserMapper.__type__`` (ie ``User``) to be returned with fields set from
the JSON data.


.. code-block:: rest

    POST /users
    {
        "name": "Jane Doe",
        "is_admin": true,
        "company": {
            "id": 43
        }
    }

    {
        "id": 99,
        "name": "Jane Doe",
        "is_admin": true,
        "company": {
            "id": 43,
            "name": "Acme Corp"
        }
    }


Further Reading
---------------
receipes, reference, point out arrested etc

