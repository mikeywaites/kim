=======
Mapper
=======

Mappers are the building blocks of Kim - they define how JSON output
should look and how input JSON should be expected to look.

Mappers consist of Fields. Fields define the shape and nature of the data
both when being serialised(output) and marshaled(input).

Mappers must define a __type__. This is the type that will be
instantiated if a new object is marshaled through the mapper. __type__
maybe be any object that supports setter and getter functionality.


Declaring mappers
------------------

A new ``Mapper`` is defined by creating a subclass of the base ``Mapper`` provided by kim.  Fields are then added to a ``Mapper`` as class
attributes to define the shape of the data when using the ``Mapper``.

.. code-block:: python

    from kim import Mapper

    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('myapp.mappers.CompanyMapper')


Mapper __type__
^^^^^^^^^^^^^^^^^

A ``Mapper`` must define a ``__type__`` property.  A python type that supports the getter and setter protocol maybe used.

.. code-block:: python

    from kim import Mapper

    class MyUser(object):

        def __init__(self, id=None, name=None, company=None):
            self.id = id
            self.name = name
            self.company = company

    class UserMapper(Mapper):
        __type__ = MyUser

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('myapp.mappers.CompanyMapper')


Mapper __roles__
^^^^^^^^^^^^^^^^^

A ``Mapper`` may also define a ``__roles__`` property.  Usage of roles is covered extensively in the :ref:`Roles section<roles>` of the documentation.

.. code-block:: python

    from kim import Mapper

    class UserMapper(Mapper):
        __type__ = MyUser

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('myapp.mappers.CompanyMapper')

        __roles__ = {
            'public' whitelist('name'),
        }
