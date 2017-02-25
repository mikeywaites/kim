.. _quickstart:

Quickstart
==========

.. module:: kim.mapper

Eager to get started? This page gives a good introduction in how to get started
with Kim.

First, make sure that:

* Kim is :ref:`installed <install>`


Defining Mappers
-----------------

Let's get started by defining some mappers.  Mappers are the building blocks of kim - They
define how JSON output should look and how inpit JSON should be expected to look.

Mappers consist of Fields. Fields define the shape and nature of the data
both when being serialised(output) and marshaled(input).

Mappers must define a __type__. This is the type that will be
instantiated if a new object is marshaled through the mapper. __type__
maybe be any object that supports setter and getter functionality.

.. code-block:: python

	from kim import Mapper
	from kim import field

	class CompanyMapper(Mapper):
		__type__ = Company
		id = field.String(read_only=False)
		name = field.String()

	class UserMapper(Mapper):
		__type__ = User
		id = field.String(read_only=False)
		name = field.String()
		company = field.Nested(CompanyMapper, read_only=True)


**Further Reading**:

    * :ref:`Defining Mappers - Advanced <mappers_advanced_defining>`
    * :ref:`Polymorphic Mappers <mappers_advanced_polymorphic>`
    * :ref:`Custom Mapper classes <mappers_advanced_custom>`


Serializing data
---------------------

Now we have a mapper defined we can start serializing some objects.  To serialize an
object we simply it to our mapper using the obj kwarg.

.. code-block:: python

	>>> user = get_user()
	>>> mapper = UserMapper(obj=user)
	>>> mapper.serialize()
	{'name': 'Bruce Wayne', 'id': 1, 'company': {'name': 'Wayne Enterprises', 'id': 1}}


Serializing many objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We can also handle serializing lots of objects at once.  Each mapper represents a single datum. When
serializing more than one object we use the method ``many`` from the mapper.

.. code-block:: python

	>>> user = get_users()
	>>> mapper = UserMapper.many(obj=user).serialize()
	[{'name': 'Bruce Wayne', 'id': 1, 'company': {'name': 'Wayne Enterprises', 'id': 1}}
	{'name': 'Martha Wayne', 'id': 2, 'company': {'name': 'Wayne Enterprises', 'id': 1}}]

**Further Reading**:

    * :ref:`Advanced serialization usage <serialization_advanced>`
    * :ref:`Custom serialization pipelines <custom_serialization_pipelines>`


Marshaling data
---------------------

We've seen how we to serialize our objects back into dicts. Now we want to be able to marshal
incoming data into the ``__type__`` defined on our mappeer.  When using our mapper to marshal data, we pass the data kwarg.

.. code-block:: python

	>>> data = {'name': 'Tony Stark'}
	>>> mapper = UserMapper(data=data)
	>>> mapper.marshal()
	User(name='Tony Stark', id=3)

As you can see the data we passed the mapper has been converted into our User type.

Marshaling many objects
^^^^^^^^^^^^^^^^^^^^^^^

Many objects can be marshaled at once using the ``many`` method from our mapper.

.. code-block:: python

	>>> data = [{'name': 'Tony Stark'}, {'name': 'Obadiah Stane'}]
	>>> mapper = UserMapper.many(data=data).marshal()
	[User(name='Tony Stark', id=3), User(name='Obadiah Stane', id=4)]


Handling validation errors
^^^^^^^^^^^^^^^^^^^^^^^^^^^

When Marshaling, Kim will apply validtion via the fields you have used to define your mapper.  Field validation and
data pipelines are covered in detail in the advanced section but here's a simple example of handling the errors
raised when marshaling.

.. code-block:: python

	from kim.exception import MappingInvalid

	data = {'name': 'Tony Stark'}
	mapper = UserMapper(data=data)

	try:
		mapper.marshal()
	except MappingInvalid as e:
		print(e.errors)

Updating existing objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^

We wont always want to create new objects when marshaling data.  Kim supports updating existing objects
as well.  This is achieved by passing the the existing obj to the mapper along with the new data.  As with normal
marshaling, Kim will raise an error for any missing required fields.

.. code-block:: python

	>>> obj = User.query.get(2)
	>>> data = {'name': 'New Name', 'title': 'New Guy'}
	>>> mapper = UserMapper(obj=obj, data=data)
	>>> mapper.marshal()
	User(name='New Name', id=2, title='New Guy')


Partial Updates
^^^^^^^^^^^^^^^^^^^^

We can also partially update objects.  This means Kim will not raise an error when required fields are missing from
the data passed to the mapper and will instead only process fields that are present in the data provided.  We pass the `partial=True`
kwarg to the Mapper to indicate this is a partial update.

.. code-block:: python

	>>> obj = User.query.get('four')
	>>> data = {'title': 'Super Villain'}
	>>> mapper = UserMapper(obj=obj, data=data, partial=True)
	>>> mapper.marshal()
	User(name='Obadiah Stane', id=4, title='Super Villain')

**Further Reading**:

    * :ref:`Advanced marshaling usage <marshaling_advanced>`
    * :ref:`Custom marshaling pipelines <custom_marshaling_pipelines>`


Nesting Objects
------------------

We have already seen how to define a nested object on one of our mappers.  Nesting allows us to specify other mappers that
represent nested objects within our data structures.  As we can see below, when we serialize our User object Kim also serializes
the users company for us too!

.. code-block:: python

	>>> user = get_user()
	>>> mapper = UserMapper(obj=user)
	>>> mapper.serialize()
	{'name': 'Bruce Wayne', 'id': 1, 'company': {'name': 'Wayne Enterprises', 'id': 1}}


Marshaling nested objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Our Nested company object is specified as `read_only=True`.  This means Kim will ignore any data present for that field
when marshaling.  To demonstrate marshaling with a Nested object lets first add a new field to our UserMapper.

.. code-block:: python

	from kim import Mapper
	from kim import field

	def user_getter(session):
        """Fetch a user by id from user supplied data
        """
        if session.data and 'id' in session.data:
            return User.get_by_id(session.data['id'])

	class CompanyMapper(Mapper):
		__type__ = Company
		id = field.String(read_only=False)
		name = field.String()

	class UserMapper(Mapper):
		__type__ = User
		id = field.String(read_only=False)
		name = field.String()
		company = field.Nested(CompanyMapper, read_only=True)
		sidekick = field.Nested('UserMapper', required=False, getter=user_getter)


.. note:: Nested mappers can be supplied as string class name as well as a a mapper class directly.

So a few things have happened here.  We have added another Nested field but this time we have also specified a getter kwarg.
The getter function will be called when we pass a nested object to the User mapper for the mapper to marshal.

A getter function is responsible for taking the data passed into the nested object and returning another type, typically a database
object. If the object is not found or not permitted to be accessed, it should return None, which will cause a validation error to be raised.

The role of Nested getter functions is to provide a simple point at which you can validate the authenticity of the data before inflating it into
a nested object.  It also means that virtually any datastore can be used to expand nested objects.

.. code-block:: python

	>>> data = {'name': 'Tony Stark', 'sidekick': {'id': 5, 'name': 'Pepper Potts'}}
	>>> mapper = UserMapper(data=data)
	>>> obj = mapper.marshal()
	>>> obj
	User(name='Tony Stark', id=3)
	>>> obj.sidekick
	User(name='Pepper Potts', id=5)


**Further Reading**:

    * :ref:`Nested fields <fields_nested>`


Roles: Changing the shape of the data
---------------------------------------

Kim provides a powerful system for controlling what fields are available during marshaling and serialization called `roles`.
Roles are defined against a :class:`Mapper` and can be provided as a ``whitelist`` set of permitted fields or a ``blacklist`` set of
private fields. (It's also possible to combine the two concepts which is covered in more detail in the advanced section).

To define roles on your mapper user the __roles__ property.

.. code-block:: python

	from kim import Mapper
	from kim import field, role

	class CompanyMapper(Mapper):
		__type__ = Company
		id = field.String(read_only=False)
		name = field.String()

	class UserMapper(Mapper):
		__type__ = User
		id = field.String(read_only=False)
		name = field.String()
		company = field.Nested(CompanyMapper, read_only=True)

        __roles__ = {
            'idonly': role.whitelist('id'),
            'public': role.blackist('id')
        }

We've defined two roles on our UserMapper.  These roles can now be used when marshaling and serializing by passing the ``role`` kwargs
to the :py:meth:`kim.mapper.Mapper.serialize` and :py:meth:`kim.mapper.Mapper.marshal`.

Let's use the ``idonly`` role to serialize a user and only return the id field.

.. code-block:: python

	>>> user = get_user()
	>>> mapper = UserMapper(obj=user)
	>>> mapper.serialize(role='idonly')
	{'id': 1}

.. raw:: html

   <hr />

Next Steps
--------------

The quickstart covers the bare minimum to get users to a basic understanding of how to use Kim.  Kim offers heaps more functionality
so why not head over to the :ref:`Advanced Section <advanced>` to read more about all of Kim's features.
