.. _roles:

Roles
=========

Roles are a fundamental feature of Kim.  Its very common to need to provide a different view of the data or to require a selection of fields when accepting data.  ``Roles`` in Kim allow users
to shape their data at runtime in in a simple yet powerfuly flexible manor.


Defining roles
~~~~~~~~~~~~~~~

``Roles`` are added to to your :py:class:`~.Mapper` declarations using the ``__roles__`` attribute.

.. code-block:: python

    from kim import Mapper, whitelist

    class UserMapper(Mapper):
        __type__ = User

        id = fields.Integer(read_only=True)
        name = fields.String(required=True)
        company = fields.Nested('myapp.mappers.CompanyMapper')

        __roles__ = {
            'id_only': whitelist('id')
        }


As you can see from the example above, __roles__ is simply defined as a dict of role name and ``Role`` key value pairs.
There are two types of roles available. :ref:`whitelists <whitelist>` define a role that allows any of the fields specified to be inlcuded when marshaling or serializing.
:ref:`blacklists <blacklist>` define a role of fields that should that excluded when marshaling or serializing.

roles can be defined using any iterable that supports membership tests ie, lists or tuples.  The base implementation of the Role class is recommened as it provides access to more
advanced features such as merging roles together.

.. note:: :py:class:`.Role` is actually a subclass of set which provides us with the api required to union roles together.


.. _default_role:

Default roles
~~~~~~~~~~~~~~~~
Mappers also create a special default role that by default generates a :ref:`whitelists <whitelist>` role that contains all the declared fields from the mapper.
The default role will be used when serializing or marshaling and a role has not been explicitly provided.

.. code-block:: python

    from kim import Mapper, whitelist

    class UserMapper(Mapper):
        __type__ = User

        id = fields.Integer(read_only=True)
        name = fields.String(required=True)
        company = fields.Nested('myapp.mappers.CompanyMapper')

        __roles__ = {
            'id_only': whitelist('id')
        }

    mapper = UserMapper()
    mapper.roles
    {'id_only': Role('id'), '__default__': Role('id', 'name', 'company')}



Users may override the __default__ role for a mapper by specifying __default__ in the mappers role def.

.. code-block:: python

    from kim import Mapper, whitelist

    class UserMapper(Mapper):
        __type__ = User

        id = fields.Integer(read_only=True)
        name = fields.String(required=True)
        company = fields.Nested('myapp.mappers.CompanyMapper')

        __roles__ = {
            'id_only': whitelist('id')
            '__default__ ': whitelist('name')
        }

    mapper = UserMapper()
    mapper.roles
    {'id_only': Role('id'), '__default__': Role('name')}



.. _whitelist:

Whitelists
~~~~~~~~~~~~~~~~


.. _blacklist:

Blacklists
~~~~~~~~~~~~~~~~


.. _parent:

Roles and inheritance.
~~~~~~~~~~~~~~~~~~~~~~~

Roles automatically inherit all roles defined in parent classes and even from mixins.

.. code-block:: python

    from kim import Mapper, whitelist

    class IDMApper(Mapper):

        id = fields.Integer(read_only=True)

        __roles__ = {
            'id_only': whitelist('id')
        }

    class UserMapper(IDMapper):
        __type__ = User

        name = fields.String(required=True)
        company = fields.Nested('myapp.mappers.CompanyMapper')

        __roles__ = {
            'public': whitelist('name', 'company')
        }

    mapper = UserMapper()
    mapper.roles
    {'id_only': Role('id'), 'public': Role('name', 'company'), '__default__': Role('name', 'id', 'company')}


Any __default__ role overrides in the inheritance tree will also inherit to the concrete class.  If no __default__ override is provided then the concrete classes __default__ role will be
defined as normal.


.. _merge:

Merging and combining roles.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Roles can be combined together using the union bitwise operator similar to producing the union of sets in python.  The key difference with roles is that :ref:`whitelist <whitelist>` and :ref:`blacklist <blacklist>`, when combined, act as you might expect.

.. code-block:: python

    # Combine two whitelist roles together.
    >>> whitelist('id', 'name') | whitelist('id', 'email')
    Role('id', 'name', 'email')

    # Combine a whitelist and blacklist role together
    >>> whitelist('id', 'name') | blacklist('name')
    Role('id')
