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



Field pipelines
--------------------

A core concept of Kims design is pipelines.  Pipelines are similar in a way to pipes in unix.
They specify a collection of 'pipes' that pass data along a chain forming a processing pipeline
along which data travels.

Each field implements both an ``Input`` and ``Ouput`` pipeline.  This gives kim a unique level
of flexability when it comes to handling data coming in (marshaling) and data going out (serialization).

.. code-block:: python

    class StringInput(Input):

        input_pipes = [
            get_data_from_source,
        ]
        validation_pipes = [
            is_valid_string,
        ]
        output_pipes = [
            update_output,
        ]

pipelines
^^^^^^^^^^^^^^^^

each :class:`.Pipeline` is broken up into 4 groups, ``input_pipes`` ``validation_pipes``
``processing_pipes`` and ``output_pipes``.

pipes aren't anything special.  They are typically an iterable containing
callables that accept two positional arguments, an instance of :class:`.Field`
and an object containing the data being processed.

Input pipes
"""""""""""""""""
Input pipes are responsible for extracting a particular part of the data relevant to
the field being processed.

During marshaling the entire data object is initially passed to each field and subsequently
to the callables defined in ``input_pipes``.  ``The input_pipes`` typically extract the key from the data
relevant to this field and return where it will then be passed onto the next group of
pipes in the chain.

Here is a simple example of a pipe that validates that data is a valid string.

.. code-block:: python

    def is_valid_string(field, data):
        """pipe used to determine if a value can be coerced to a string

        :param field: instance of :py:class:``~.Field`` being pipelined
        :param data: data being piplined for the instance of the field.
        """

        try:
            return str(data)
        except ValueError:
            raise field.invalid("field is not a valid string")



Field Types
--------------------

.. autoclass:: kim.field.String
  :members:

.. autoclass:: kim.field.Integer
  :members:


Custom fields
--------------------

There are a few approaches to implementing custom :class:`.Field` types in Kim.
Typically Kim will have a field type that provides most of what the user requires
but some additional processing will be required.  In this case users should
