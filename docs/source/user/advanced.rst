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

*source options*
- __self__
- differnt input/output names

TODO (JS)

.. _fields_nested:

Nested
^^^^^^^^^^^^^^^^^^

TODO (JS)

- allow_updates etc

.. _fields_collection:

Collections
^^^^^^^^^^^^^^^^^^

TODO (JS)


Pipelines
-----------------------

.. _pipelines_extra_marshal_pipes:

extra_marshal_pipes
^^^^^^^^^^^^^^^^^^

TODO (JS)

.. _custom_pipelines:

Custom Pipelines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO (JS)

