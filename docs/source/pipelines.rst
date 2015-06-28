====================
Pipelines
====================

A core concept of Kims design is pipelines.  Pipelines are similar in a way to pipes in unix.
They specify a collection of 'pipes' that pass data along a chain forming a processing pipeline
along which data travels.

Each field implements both an ``Input`` and ``Ouput`` pipeline.  This gives kim a unique level
of flexability when it comes to handling data coming in (marshaling) and data going out (serialization).


Input Pipelines
----------------------

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

Output Pipelines
----------------------


Pipes
------------------

each :class:`.Pipeline` is broken up into 4 groups, ``input_pipes`` ``validation_pipes``
``processing_pipes`` and ``output_pipes``.

pipes aren't anything special.  They are typically an iterable containing
callables that accept two positional arguments, an instance of :class:`.Field`
and an object containing the data being processed.

Input pipes
^^^^^^^^^^^^^^^^
Input pipes are responsible for extracting a particular part of the data relevant to
the field being processed.

During marshaling the entire data object is initially passed to each field and subsequently
to the callables defined in ``input_pipes``.  ``The input_pipes`` typically extract the key from the data
relevant to this field and return where it will then be passed onto the next group of
pipes in the chain.


Validation pipes
^^^^^^^^^^^^^^^^

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

Processing pipes
^^^^^^^^^^^^^^^^

Output pipes
^^^^^^^^^^^^^^^^
