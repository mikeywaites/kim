.. _roles:

=========
Roles
=========

Roles are a fundamental feature of Kim.  Its very common to need to provide a different view of the data or to require a selection of fields when accepting data.  ``Roles`` in Kim allow users
to shape their data at runtime in a simple yet powerfuly flexible manor.


Defining roles
------------------

``Roles`` are added to your :py:class:`~.Mapper` declarations using the ``__roles__`` attribute.

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
:ref:`blacklists <blacklist>` define a role of fields that should be excluded when marshaling or serializing.

Roles can be defined using any iterable that supports membership tests ie, lists or tuples.  The base implementation of the Role class is recommened as it provides access to more
advanced features such as intuitively merging roles together.

.. note:: :py:class:`.Role` is actually a subclass of set which provides us with the api required to union roles together.


.. _default_role:

Default roles
^^^^^^^^^^^^^^^^
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
^^^^^^^^^^^^^^^^

Whitelists are roles that define a list of fields that are permitted for inclusion when marhsaling or serializing.
For example, a whitelist role called ``id_only`` that contains the field name ``id`` instructs kim that whenever
the ``id_only`` role is used **only** the ``id`` field should be considered in the input/output data.

.. code-block:: python

    from kim import whitelist

    id_only_role = whitelist('id')

    class IdMixin(object):

        id = fields.Integer(read_only=True)

        __roles__ = {
            'id_only': id_only
        }


    class UserMapper(Mapper, IdMixin):
        pass


.. _blacklist:

Blacklists
^^^^^^^^^^^^^^^^

Blacklists are role that act in the opposite manner to whitelists.  They define a list of fields that should not be used when marshaling and serializing data.  A blacklist role named ``id_less``
that contained the field name ``id`` would instruct kim that every field defined on the mapper should be considered except ``id``.


.. code-block:: python

    from kim import whitelist

    class UserMapper(Mapper):

        id_less_role = blacklist('id')

        __roles__ = {
            'id_less': blacklist('id')
        }


.. note:: Internally kim overloads the built-in method __contains__ of set and reverses the statement for a blacklist.

          ``email in blacklist('email')`` would return false in this case as email should be excluded.


.. _parent:

Roles and inheritance.
^^^^^^^^^^^^^^^^^^^^^^^

Mappers automatically inherit all roles defined in parent classes and even from mixins.

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Roles can be combined together using the union bitwise operator similar to producing the union of sets in python.  The key difference with roles is that :ref:`whitelist <whitelist>` and :ref:`blacklist <blacklist>`, when combined, act as you might expect.

.. code-block:: python

    # Combine two whitelist roles together.
    >>> whitelist('id', 'name') | whitelist('id', 'email')
    Role('id', 'name', 'email')

    # Combine a whitelist and blacklist role together
    >>> whitelist('id', 'name') | blacklist('name')
    Role('id')


Consider the following real world example.  We have a set of Mappers used to serialize 3 different types of entity exposed by our rest api.


Using roles
------------------

We have covered how roles are declared against mappers, the following examples explain how roles are used.


Marshalling
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TODO


Serializing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TODO
