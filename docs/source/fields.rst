=====================
Fields
=====================

Field, as it's name suggests, represents a single key or 'field' inside of your mappings.
Much like columns in a database or a csv, they provide a way to represent different data types
when pusing data into and out of your Mappers.

A core concept of Kims architecture is that of Pipelines.  Every Field provides both an Input and Output pipeline
which afford users a great level of flexibility when it comes to handling data.

Kim provides a collection of default Field implementations, for more complex cases extending Field to create new
field types couldn't be easier.


Declaring fields
------------------

As you have probably seen already in the docs for :py:class:`.Mapper`, :py:class:`.Field` types are defind as class
level attributes on ``Mapper`` classes.

.. code-block:: python

    from kim import Mapper
    from kim import field

    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        email = field.Email(required=True)


Field Types
--------------------

Field
^^^^^^^^^^^^
.. autoclass:: kim.field.Field
  :members:

  .. automethod:: __init__

String
^^^^^^^^^^^^
.. autoclass:: kim.field.String
  :members:

  .. automethod:: __init__

Integer
^^^^^^^^^^^^
.. autoclass:: kim.field.Integer
  :members:


Nested
^^^^^^^^^^^^
.. autoclass:: kim.field.Nested
  :members:

.. autoclass:: kim.field.NestedFieldOpts
  :members:
  :special-members:
