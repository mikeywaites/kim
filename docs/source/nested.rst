.. _nested:

=============
Nested Fields
=============

Nested fields allow :py:class:`~.Mapper`s to include other :py:class:`~.Mapper`s in a reusable and flexible way. This allows you to structure the flow of data through your application in a similar or identical way to your database models. There are several options you can use to control whether data in the Nested field can be updated, whether new instances of it can be created and the facility to load the nested object based on a single field, such as ``id``.


.. _serializing:

Serializing Nested Fields
-------------------------

Use the :py:class:`.Nested` class to define a nested field, passing it the :py:class:`~.Mapper` instance you want to nest.

.. code-block:: python

    from kim import Mapper

    class CompanyMapper(Mapper):
        __type__ = Company

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        sector = field.String()


    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested(CompanyMapper)

    mapper = UserMapper(user)
    mapper.serialize()
    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'id': 5,
        'name': 'Acme Corp',
        'sector': 'Manufacturing'
     }}


If you serialize a user and it has an attribute `user.company`, serializing via `UserMapper` will also include output from the `CompanyMapper`. That is, `company` will be set to the same thing `CompanyMapper(user.company).serialize()` would produce.

.. _marshaling:

Marshaling Nested Fields
------------------------

Nested fields can be marshaled in a similar manner to serialising, but there are several security concerns you should take into account when using them. For security reasons, kim's settings default to the most secure and must be overridden to use the full functionality.

.. note:: This section, and kim's defaults, assume you are using nested fields to refer to foreign keys (or similar NoSQL relationships) on ORM objects. If you are not using Kim with an ORM, you probably want to enable the `allow_create` and `allow_updates_in_place` options for seamless operation.

In general, there are four things you may want to happen when marshaling a nested field. The following sections describe them, and the input data they expect.

1. Retrieve by ID only (default)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'id': 5,
     }}

This is the most secure option and the most common thing you will want to do. This means that only the ID of the target object will be used, a ``getter`` function which you define will be used to retrieve the object with this ID from your database (taking into account security such as ensuring the user has access to the object), and the object returned from the ``getter`` function will be set on the target attribute.

2. ``allow_updates`` - Retrieve by ID, allowing updates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'id': 5,
        'name': 'New name',
     }}

This option retrieves the related object via it's ID using a ``getter`` function as in scenario 1. However, any other fields passed along with the ID will be updated on the related object, according to the role passed. You are strongly encouraged to only use this option with a restrictive role, in order to avoid introducing security holes where users can change fields on objects they should not be able to do, (for example, change the ``user`` field on an object to change it's ownership).

Use this option like this (``marshal_role`` is not required):

.. code-block:: python
    company = field.Nested('CompanyMapper', allow_updates=True, marshal_role='restrictive_role')

3. ``allow_create`` - Retrieve by ID, or create object if no ID passed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # No ID passed - create new
    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'name': 'My new company',
     }}
     # ID passed - works as scenario 1
     {'id': 1,
      'name': 'Bob Jones',
      'company': {
         'id': 5,
      }}


This option uses your ``getter`` function to look up the related object by ID, but if it is not found (ie. your getter function returns ``None``) then a new instance of the object will be created, using the fields passed according to the role.

This option may be combined with ``allow_updates`` in order to provide an field which will accept an existing object, allow it to be updated and allow a new one to be created.

Once again, you should consider carefully the role you use with this option to avoid unexpected consequences (for example, it being possible to set the ``user`` field on an object to someone other than the logged-in user.)

Use this option like this (``marshal_role`` is not required):

.. code-block:: python
    company = field.Nested('CompanyMapper', allow_create=True, marshal_role='restrictive_role')

4. ``allow_updates_in_place`` - Do not use ID, update existing related object
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # No ID passed - update the existing object if it exists
    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'name': 'New name',
     }}

In this scenario, no ID field is required and no ``getter`` function is used. Instead, the fields are simply updated on the existing value of ``user.company``, if it exists.


TODO combinations
TODO getter functions
TODO setter functions
TODO more examples

.. _scope_import_problems:

Scope and import order problems
-------------------------------

If you have a large number of Mappers, you may find circular dependencies develop between the modules they are defined in, which can prevent your code from compiling and make certain topologies impossible. You may also have a Mapper defined further down in the same module which you want to Nest, but can't move it due to other Mappers also requiring it.

To solve these problem, the target Mapper for a Nested field can be passed as a string. This string may refer to a serializer defined anywhere else in the application.

.. code-block:: python

    from kim import Mapper

    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('CompanyMapper')


    class CompanyMapper(Mapper):
        __type__ = Company

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        sector = field.String()


.. note:: This means Mapper class names must be globally unique

.. _using_roles:

Using roles
-----------

You can use :ref:`roles` to control which fields are processed by the target Mapper, both when serialising and marshaling.

.. code-block:: python

    from kim import Mapper, whitelist

    class CompanyMapper(Mapper):
        __type__ = Company

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        sector = field.String()

        __roles__ = {
            'simple': whitelist('id', 'name')
        }


    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested(CompanyMapper, role='simple')

    mapper = UserMapper(user)
    mapper.serialize()
    {'id': 1,
     'name': 'Bob Jones',
     'company': {
        'id': 5,
        'name': 'Acme Corp'
     }}


In this example, the ``sector`` field has been omitted from the nested company, because the ``simple`` role is being used.

.. _seperate_roles:

Seperate roles for serialising and marshaling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you may want a separate role when serialising as opposed to marshaling. This can be particularly useful in the case of marshaling, when you often want to restrict fields that can be updated whilst still showing all fields in the output.

TODO



