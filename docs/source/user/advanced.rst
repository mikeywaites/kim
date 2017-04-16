.. _advanced:

Advanced Topics
================

.. module:: kim.mapper

This section gives a more detailed explanation of the features of Kim.  If you're looking for a quick overview
or if this is your first time using Kim, please check out the :ref:`quickstart guide <quickstart>`.

.. _mappers_advanced:

Mappers
-----------

.. _mappers_advanced_polymorphic:

Polymorphic Mappers
^^^^^^^^^^^^^^^^^^^^^

It's not uncommon to have collections of objects that are not all the same.  Perhaps you have an ``Activity`` type that has two sub types ``Task`` and ``Event``.  Their serialization
requirements differ slightly meaning you'd typically serialize two lists and manually munge them together.

Kim provides support for Polymorphic Mapper to solve this problem.

Polymorphic Mappers are defined like a normal mapper with a few small differences.  Firstly we define our base "type".  This is the Mapper
all of our Polymorphic types extend from.  Our base type should inherit from :class:`kim.mapper.PolymorphicMapper` instead of :class:`kim.mapper.Mapper`.

.. code-block:: python

    from kim import PolymorphicMapper, field

    class ActivityMapper(PolymorphicMapper):

        __type__ = Activity

        id = field.String()
        name = field.String()
        object_type = field.String(choices=['event', 'task'])
        created_at = field.DateTime(read_only=True)

        __mapper_args__ = {
            'polymorphic_on': object_type,
        }


For users of SQLAlchemy, this API will feel very familiar.  We've specified our base mapper with the ``__mapper_args__``
property.  The ``polymorphic_on`` key is given a referrence to the field used to indentify our polymorphic types.  This
can also be passed as a string.

.. code-block:: python

    __mapper_args__ = {
        'polymorphic_on': 'object_type'
    }


Now we need to define our types.

.. code-block:: python

    class TaskMapper(ActivityMapper):

        __type__ = Task

        status = field.String(read_only=True)
        is_complete = field.Boolean()

        __mapper_args__ = {
            'polymorphic_name': 'task'
        }


    class EventMapper(ActivityMapper):

        __type__ = Event

        location = field.String(read_only=True)

        __mapper_args__ = {
            'polymorphic_name': 'event'
        }


Our types inherit from our base ``ActivityMapper`` and also specify the ``__mapper_args__`` property.  Our types provide
the ``polymorphic_name`` key which indentifies the type to the base mapper.


.. _mappers_advanced_polymorphic_serialize:

Serializing Polymorphic Mappers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Serializing Polymorphic Mappers works in the same way as serializing a normal Mapper.  When we want to serialize a collection of mixed types
we serialzie using the base mapper.

.. code-block:: python

    >>> activities = Activity.query.all()
    >>> ActivityMapper.many(obj=activities).serialize()
    [
        {'name': 'My Test Event', 'id': 1, 'object_type': 'event', 'created_at': '2017-03-11T05:14:43+00:00', 'location': 'London'},
        {'name': 'My Test Task', 'id': 1, 'object_type': 'task', 'created_at': '2016-03-11T05:14:43+00:00', 'status': 'overdue', 'is_complete': False},
    ]

As you would expect, serializing using one of the child types directly will only serialize its own type.

.. code-block:: python

    >>> activities = Event.query.all()
    >>> EventMapper.many(obj=activities).serialize()
    [
        {'name': 'My Test Event', 'id': 1, 'object_type': 'event', 'created_at': '2017-03-11T05:14:43+00:00', 'location': 'London'},
    ]


.. _mappers_advanced_polymorphic_marshal:

Marshaling Polymorphic Mappers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Marshaling Polymorphic Mappers is also supported but is disabled by default.  It is currently considered an experimental feature.

To enable marshaling for Polymorphic Mappers we pass ``allow_polymorphic_marshal: True`` to the ``__mapper_args__`` property on the
base Polymorphic Mapper.

.. code-block:: python

    class ActivityMapper(PolymorphicMapper):

        __type__ = Activity

        id = field.String()
        name = field.String()
        object_type = field.String(choices=['event', 'task'])
        created_at = field.DateTime(read_only=True)

        __mapper_args__ = {
            'polymorphic_on': object_type,
            'allow_polymorphic_marshal': True,
        }

We can now marshal a collection of mixed object types using the base ActivityMapper.

.. code-block:: python

    data = [
        {'name': 'My Test Event', 'object_type': 'event', 'created_at': '2017-03-11T05:14:43+00:00', 'location': 'London'},
        {'name': 'My Test Task', 'object_type': 'task', 'created_at': '2016-03-11T05:14:43+00:00', 'status': 'overdue', 'is_complete': False},
    ]
    >>> ActivityMapper.many(obj=activities).marshal()
    [Event(name='My Test Event'), Task(name='My Test Task')]


.. _mappers_advanced_exceptions:

Exception Handling
^^^^^^^^^^^^^^^^^^^^^

Kim uses custom exceptions when marshaling to allow you to get at all the errors that ocurred as a result of processing the fields
in your mappers marshaling pipeline.

Each pipe in a field`s pipeline can raise a :class:`kim.exception.FieldInvalid`.  As the pipeline is processed the errors for the field will be stored
against the mapper.  Once all the fields have been processed the mapper checks to see if any errors occurred.  If there are any errors the mapper will
raise a :class:`kim.exception.MappingInvalid`.

You should typically only worry about handling the :class:`kim.exception.MappingInvalid` when marshaling.


.. code-block:: python

    from kim import MappingInvalid

    try:
        data = mapper.marshal()
    except MappingInvalid as e:
        print(e.errors)

The :class:`kim.exception.MappingInvalid` exception raised will have an attribute called errors.  Errors is a dictionary containing ``field_name: error message``.  The errors object can
also contain nested error objects when marshaling a :class:`kim.field.Nested` field fails.

.. _roles_advanced:

Roles
-----------

As described in the quickstart, the Roles system provides users with a system for controlling what fields are available
during marshaling and serialization.


Role Inheritance
^^^^^^^^^^^^^^^^^^^^

Mappers inherit Roles from their parents automatically.  Consider the following example.

.. code-block:: python


    class MapperA(Mapper):

        __type__ = dict

        field_a = field.String()
        field_b = field.String()

        __roles__ = {
            'ab': whitelist('field_a', 'field_b')
        }


    class MapperB(MapperA):

        field_c = field.String()

        __roles__ = {
            'abc': blacklist()
        }


MapperB inherits from MapperA and therefore will have access to all the roles defined on
MapperA.  Equally, MapperB can define the role ``ab`` to override the fields available for that role.


Combining Roles
^^^^^^^^^^^^^^^^^^^^

Under the hood :class:`kim.role.Role` is a set object.  This allows us to combine roles in the ways that sets can be combined.
This is useful when you have a role defined on a base type that you need to extend.

When combining whitelist and blacklist roles the order is not important.  The blacklist always takes priority.  The following examples are equal.

.. code-block:: python

    >>> role = blacklist('name', 'id') | whitelist('name', 'email')
    >>> assert 'email' in role
    >>> assert 'name' not in role
    >>> assert 'id' not in role
    >>> assert role.whitelist

    >>> role = whitelist('name', 'id') | blacklist('name', 'email')
    >>> assert 'id' in role
    >>> assert 'name' not in role
    >>> assert 'email' not in role
    >>> assert role.whitelist


Default Roles
^^^^^^^^^^^^^^^^^^^^

Every mapper has a special hidden role called ``__default__``.  By default the ``__default__`` role contains every field defined on your Mapper.

You can override the ``__default___`` role by specifying it in the ``__roles__`` property on your Mapper.


.. code-block:: python

    class MapperA(Mapper):

        __type__ = dict

        field_a = field.String()
        field_b = field.String()

        __roles__ = {
            '__default__': whitelist('field_a')
        }

Now whenever we call :meth:`kim.mapper.Mapper.marshal` or :meth:`kim.mapper.Mapper.serialize` on MapperA without a role,
the default role will be used which now only includes field_a.

.. note::

    The __default__ role does not currently inherit from it's parent and must be defined explitly on the all Mappers in the
    class heirarchy.


.. _fields_advanced:

Fields
-----------

Name and Source
^^^^^^^^^^^^^^^^^^

If you'd like the field in your JSON data to have a different name to the field
on the object, pass the ``source`` attribute to ``Field``.

.. code-block:: python

    from kim import Mapper, field

    class CompanyMapper(Mapper):
        __type__ = Company
        title = field.String(source='name')

    >>> company = Company(name='Wayne Enterprises')
    >>> mapper = CompanyMapper(company)
    >>> mapper.serialize()
    {'title': 'Wayne Enterprises'}

.. note:: When marshaling, Kim will look for data in the field named in source

Similarly, if you'd like the JSON data to have a different name to the attribute
name on the mapper class, pass the ``name`` attribute to ``Field``. This is useful
if you have multiple fields in different roles which should serialize to the
same field.

.. code-block:: python

    from kim import Mapper, field, role

    class CompanyMapper(Mapper):
        __type__ = Company
        short_title = field.String(name='title')
        long_title = field.String(name='title')

        __roles__ = {
            'simple': role.whitelist('short_title'),
            'full': role.whitelist('long_title')
        }


    >>> company = Company(short_title='Wayne', long_title='Wayne Enterprises')
    >>> mapper = CompanyMapper(company)
    >>> mapper.serialize(role='simple')
    {'title': 'Wayne'}
    >>> mapper.serialize(role='full')
    {'title': 'Wayne Enterprises'}


.. _fields_nested:

Nested ``__self__``
^^^^^^^^^^^^^^^^^^

Sometimes your object model may contain flat data but you'd like the JSON output
to be nested. You can do this by setting ``source='__self__'`` on a Nested field.


.. code-block:: python

    from kim import Mapper, field, role

    class AddressMapper(Mapper):
        __type__ = dict

        street = field.String()
        city = field.String()
        zip = field.String()

    class CompanyMapper(Mapper):
        __type__ = Company

        name = field.String()
        address = field.Nested(AddressMapper, source='__self__')

    >>> company = Company(
        title='Wayne Enterprises',
        street='4 Maple Road',
        city='Sunview',
        zip='90210')
    >>> mapper = CompanyMapper(company)
    >>> mapper.serialize()
    {'name': 'Wayne Enterprises',
     'address': {'street': '4 Maple Road', 'city': 'Sunview', 'zip': '90210'}}


In this example, the address appears as a nested object in the JSON, but it's
fields are all sourced from company.

.. note:: ``__self__`` can also be used to marshal nested objects into flat structures

Marshaling Nested Fields
^^^^^^^^^^^^^^^^^^^^^^^^

Nested fields can be marshaled in a similar manner to serializing, but there
are several security concerns you should take into account when using them.
Kim's settings default to the most secure and must be overridden to use the full
functionality.

.. note:: This section, and Kim's defaults, assume you are using nested fields
    to refer to foreign keys (or similar NoSQL relationships) on ORM objects. If you
    are not using Kim with an ORM, you probably want to enable the ``allow_create``
    and ``allow_updates_in_place`` options for seamless operation.

In general, there are four things you may want to happen when marshaling a nested
field. The following sections describe them, and the input data they expect.

For all examples, assume the Mapper looks like this:

.. code-block:: python

    from kim import Mapper

    class UserMapper(Mapper):
        __type__ = MyUser

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('CompanyMapper')  # Set options on this field


1. Retrieve by ID only (default)
++++++++++++++++++++++++++++++++

.. code-block:: python

    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'id': 5,  # Will be used to look up Company
        # Any other data here will be ignored
     }}

This is the most secure option and the most common thing you will want to do.
This means that only the ID of the target object will be used, a ``getter``
function which you define will be used to retrieve the object with this ID from
your database (taking into account security such as ensuring the user has access
to the object), and the object returned from the ``getter`` function will be set
on the target attribute.

2. ``allow_updates`` - Retrieve by ID, allowing updates
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'id': 5,  # Will be used to look up Company
        'name': 'New name',  # Will be set on the Company
     }}

This option retrieves the related object via it's ID using a ``getter`` function
as in scenario 1. However, any other fields passed along with the ID will be
updated on the related object, according to the role passed. You are strongly
encouraged to only use this option with a restrictive role, in order to avoid
introducing security holes where users can change fields on objects they should
not be able to do, (for example, change the ``user`` field on an object to
change it's ownership).

Use this option like this (``role`` is not required):

.. code-block:: python

    company = field.Nested('CompanyMapper', allow_updates=True, role='restrictive_role')

3. ``allow_create`` - Retrieve by ID, or create object if no ID passed
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    # No ID passed - create new
    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'name': 'My new company',  # Will be set on the new company
     }}
     # ID passed - works as scenario 1
     {'id': 1,
      'name': 'Bob Jones',
      'company': {
         'id': 5,  # Will be used to look up company
         # Any other data here will be ignored
      }}


This option uses your ``getter`` function to look up the related object by ID,
but if it is not found (ie. your getter function returns ``None``) then a new
instance of the object will be created, using the fields passed according to the role.

This option may be combined with ``allow_updates`` in order to provide a field
which will accept an existing object, allow it to be updated and allow a new one
to be created.

Once again, you should consider carefully the role you use with this option to
avoid unexpected consequences (for example, it being possible to set the ``user``
field on an object to someone other than the logged-in user.)

Use this option like this (``role`` is not required):

.. code-block:: python

    company = field.Nested('CompanyMapper', allow_create=True, role='restrictive_role')

4. ``allow_updates_in_place`` - Do not use ID, update existing related object
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    # No ID passed - update the existing object if it exists
    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        # No ID is required here
        'name': 'New name',  # Will be updated on existing company
     }}

In this scenario, no ID field is required and no ``getter`` function is used.
Instead, the fields are simply updated on the existing value of ``user.company``,
if it exists.


.. _fields_collection:

Collections
^^^^^^^^^^^^^^^^^^

Collections are used to produce arrays of similar fields in the JSON output.
They can be scalar fields or nested fields and work when serializing or marshaling.

To create a collection, wrap any field in ``Collection``:

.. code-block:: python

    from kim import Mapper, field, role


    class CompanyMapper(Mapper):
        __type__ = Company

        name = field.String()
        offices = field.Collection(field.String())

    >>> mapper = CompanyMapper(company)
    >>> mapper.serialize()
    {'name': 'Wayne Enterprises',
     'offices': ['London', 'Berlin', 'New York']}


You can also wrap nested fields:

.. code-block:: python

    from kim import Mapper, field, role

    class EmployeeMapper(Mapper):
        __type__ = Employee

        name = field.String()
        job = field.String()


    class CompanyMapper(Mapper):
        __type__ = Company

        name = field.String()
        employees = field.Collection(field.Nested(EmployeeMapper))

    >>> mapper = CompanyMapper(company)
    >>> mapper.serialize()
    {'name': 'Wayne Enterprises',
     'employees': [
        {'name': 'Jim', 'job': 'Developer'},
        {'name': 'Bob', 'job': 'Manager'},
    ]}

When marshaling, Nested fields can be forced to be unique on a key to avoid duplicates:


.. code-block:: python

    from kim import Mapper, field, role

    class EmployeeMapper(Mapper):
        __type__ = Employee

        id = field.Integer()
        name = field.String()


    class CompanyMapper(Mapper):
        __type__ = Company

        name = field.String()
        employees = field.Collection(
            field.Nested(EmployeeMapper), unique_on='id')

    >>> data = {'employees': [{'id': 1, 'name': 'Jim'}, {'id': 1, 'name': 'Bob'}]}
    >>> mapper = CompanyMapper(data=data)
    >>> mapper.marshal()
    MappingInvalid

.. _pipelines:

Pipelines
-----------------------

Fields process their data through a series of pipes, called a pipeline. A pipe
is passed some data, performs one operation on it and returns the new data. This
is then passed to the next pipe in the chain. This concept is similar to Unix
pipes.

There are separate pipelines for serializing and marshaling.

For example, here is the marhal pipeline for the ``String`` field. Pipes are
grouped into four stages - input, validation, process and output.

.. code-block:: python

    input_pipes = [read_only, get_data_from_name]
    validation_pipes = [is_valid_string, is_valid_choice, ]
    process_pipes = []
    output_pipes = [update_output_to_source]

    # Order of execution is:
    read_only ->                 # Stop execution if field is ready only
    get_data_from_name ->        # Get the data for this field from the JSON
    is_valid_string ->           # Raise exception if data is not a string
    is_valid_choice ->           # If choices=[] set on field, raise exception if not valid choice
    update_output_to_source ->   # Update the object with this data


.. _custom_pipelines:

Custom Fields and Pipelines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To define a custom field, you need to create the Field class and its corresponding
Pipline. It's usually easiest to inherit from an existing Field/Pipeline, rather
than defining an entirely new one.

This example defines a new field with a custom pipeline to convert its output
to uppercase:

.. code-block:: python

    from kim import pipe, String, Mapper
    from kim.pipelines.string import StringSerializePipeline


    @pipe()
    def to_upper(session):
        if session.data is not None:
            session.data = session.data.upper()
        return session.data

    class UpperCaseStringSerializePipeline(StringSerializePipeline):
        process_pipes = StringSerializePipeline.process_pipes + [to_upper]

    class UpperCaseString(String):
        serialize_pipeline = UpperCaseStringSerializePipeline

    class MyMapper(Mapper):
        __type__ = dict

        name = UpperCaseString()


.. note:: This is a contrived example, for simple transforms like this see ``extra_marshal_pipelines`` below

Note that we have only overridden the ``process_pipes`` stage of StringSerializePipeline.
Everything else remains the same. We have extended the ``process_pipes`` list
from the parent object in order to retain it's functionality, and just added
our new pipe at the end.

Pipes should find and set their data on ``session.data``. The session object
also provides access to the field, the current output object, the parent field
(if nested) and the mapper. See the API docs for details.


.. _pipelines_extra_marshal_pipes:

Custom Validation - extra_marshal_pipes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you just want to change the pipeline used by a particular instance of a Field
on a Mapper, for example to add custom validation logic, you don't need to
define an entirely new field. Instead you can pass ``extra_marshal_pipes``:

``extra_marshal_pipes`` are pushed onto the existing list of pipes defined on the
field at compile time once each time a Field is instantiated.


.. code-block:: python

    from kim import Mapper, String, Integer, pipe


    @pipe()
    def check_age(session):
        if session.data is not None and session.data < 18:
            raise session.field.invalid('not_old_enough')

        return session.data


    class MyMapper(Mapper):
        __type__ = dict

        name = String()
        age = Integer(
            extra_marshal_pipes={
                'validation': [check_age],
            },
            error_msgs={'not_old_enough': 'You must be over 18'}
        )

``extra_marshal_pipes`` takes a dict of the format ``{stage: [pipe, pipe, pipe]}``.
Any pipes pased will be added at the end of their respective stage.
