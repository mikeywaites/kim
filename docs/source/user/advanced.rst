.. _advanced:

Advanced Topics
================

.. module:: kim.mapper

This section gives a more detailed explanation of the features of Kim.  If you're looking for a quick overview
or if this is your first time using Kim, please check out the :ref:`quickstart guide <quickstart>`.

.. _mappers_advanced:

Mappers
-----------

Mappers are the building blocks of kim - They
define how JSON output should look and how inpit JSON should be expected to look.

Mappers consist of Fields. Fields define the shape and nature of the data
both when being serialised(output) and marshaled(input).


.. _mappers_advanced_defining:

Defining Mappers
^^^^^^^^^^^^^^^^^^^

TODO

.. _mappers_advanced_polymorphic:

Polymorphic Mappers
^^^^^^^^^^^^^^^^^^^^^

TODO

.. _mappers_advanced_custom:

Custom Mappers
^^^^^^^^^^^^^^^^

TODO


.. _fields_advanced:

Fields
-----------

*source options*
- __self__
- differnt input/output names

TODO

.. _fields_nested:

Nested
^^^^^^^^^^^^^^^^^^

TODO

.. _fields_collection:

Collections
^^^^^^^^^^^^^^^^^^

TODO


.. _serialization_advanced:

Serialization
-----------------

Serialization is the process of outputting data from your Mappers.  It takes things like your database objects and turns them into
data structures that are suitable for converting to JSON.


.. _marshaling_advanced:

Marshaling Advanced
----------------------

TODO


Pipelines
-----------------------

.. _custom_serialization_pipelines:

Custom Serialization Pipelines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO


.. _custom_marshaling_pipelines:

Custom Marshaling Pipelines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO

