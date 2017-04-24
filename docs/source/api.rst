.. _api:

Developer Interface
===================

.. module:: kim

This part of the documentation covers all the interfaces of Kim.


Mappers
------------------

.. autoclass:: kim.mapper.Mapper
   :members:
   :inherited-members:

   .. automethod:: _get_mapper_type
   .. automethod:: _get_obj
   .. automethod:: _get_role
   .. automethod:: _get_fields

.. autoclass:: kim.mapper.PolymorphicMapper
   :members:
   :inherited-members:

.. autoclass:: kim.mapper.MapperIterator
   :members:
   :inherited-members:

.. autoclass:: kim.mapper.MapperSession
   :members:
   :inherited-members:


Fields
------------------

.. autoclass:: kim.field.Field
   :members:
   :inherited-members:

   .. autoattribute:: opts_class
   .. autoattribute:: marshal_pipeline
   .. autoattribute:: serialize_pipeline


.. autoclass:: kim.field.FieldOpts
   :members:
   :inherited-members:


.. autoclass:: kim.field.String
   :members:

.. autoclass:: kim.field.Integer
   :members:

.. autoclass:: kim.field.IntegerFieldOpts
   :members:

.. autoclass:: kim.field.Decimal
   :members:

.. autoclass:: kim.field.DecimalFieldOpts
   :members:

.. autoclass:: kim.field.Boolean
   :members:

.. autoclass:: kim.field.BooleanFieldOpts
   :members:

.. autoclass:: kim.field.Nested
   :members:

.. autoclass:: kim.field.NestedFieldOpts
   :members:

.. autoclass:: kim.field.Collection
   :members:

.. autoclass:: kim.field.CollectionFieldOpts
   :members:

.. autoclass:: kim.field.Static
   :members:

.. autoclass:: kim.field.StaticFieldOpts
   :members:

.. autoclass:: kim.field.DateTime
   :members:

.. autoclass:: kim.field.Date
   :members:

Roles
------------------

.. autoclass:: kim.role.Role
   :members:

   .. automethod:: kim.role.Role.__contains__
   .. automethod:: kim.role.Role.__or__

.. autoclass:: kim.role.whitelist
   :members:

.. autoclass:: kim.role.blacklist
   :members:


Pipelines
------------------

.. autofunction:: kim.pipelines.base.pipe

.. autoclass:: kim.pipelines.base.Pipeline
   :members:

.. autoclass:: kim.pipelines.marshaling.MarshalPipeline
   :members:

.. autoclass:: kim.pipelines.serialization.SerializePipeline
   :members:

.. autoclass:: kim.pipelines.string.StringMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.string.StringSerializePipeline
   :members:

.. autoclass:: kim.pipelines.numeric.IntegerMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.numeric.IntegerSerializePipeline
   :members:

.. autoclass:: kim.pipelines.boolean.BooleanMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.numeric.DecimalMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.numeric.DecimalSerializePipeline
   :members:

.. autoclass:: kim.pipelines.boolean.BooleanSerializePipeline
   :members:

.. autoclass:: kim.pipelines.nested.NestedMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.nested.NestedSerializePipeline
   :members:

.. autoclass:: kim.pipelines.collection.CollectionMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.collection.CollectionSerializePipeline
   :members:

.. autoclass:: kim.pipelines.datetime.DateTimeMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.datetime.DateTimeSerializePipeline
   :members:

.. autoclass:: kim.pipelines.datetime.DateMarshalPipeline
   :members:

.. autoclass:: kim.pipelines.datetime.DateSerializePipeline
   :members:

.. autoclass:: kim.pipelines.static.StaticSerializePipeline
   :members:


Pipes
~~~~~~~~~~~~~

Base
''''''''''''''
.. autofunction:: kim.pipelines.base.get_data_from_name
.. autofunction:: kim.pipelines.base.get_data_from_source
.. autofunction:: kim.pipelines.base.get_field_if_required
.. autofunction:: kim.pipelines.base.read_only
.. autofunction:: kim.pipelines.base.is_valid_choice
.. autofunction:: kim.pipelines.base.update_output_to_name
.. autofunction:: kim.pipelines.base.update_output_to_source

String
''''''''''''''
.. autofunction:: kim.pipelines.string.is_valid_string

Integer
''''''''''''''
.. autofunction:: kim.pipelines.numeric.is_valid_integer
.. autofunction:: kim.pipelines.numeric.bounds_check

Decimal
''''''''''''''
.. autofunction:: kim.pipelines.numeric.is_valid_decimal
.. autofunction:: kim.pipelines.numeric.coerce_to_decimal
.. autofunction:: kim.pipelines.numeric.to_string

Boolean
''''''''''''''
.. autofunction:: kim.pipelines.boolean.coerce_to_boolean

Nested
''''''''''''''
.. autofunction:: kim.pipelines.nested.marshal_nested
.. autofunction:: kim.pipelines.nested.serialize_nested

Collection
''''''''''''''
.. autofunction:: kim.pipelines.collection.marshall_collection
.. autofunction:: kim.pipelines.collection.serialize_collection
.. autofunction:: kim.pipelines.collection.check_duplicates

Datetime
''''''''''''''
.. autofunction:: kim.pipelines.datetime.is_valid_datetime
.. autofunction:: kim.pipelines.datetime.format_datetime

Date
''''''''''''''
.. autofunction:: kim.pipelines.datetime.cast_to_date

Static
''''''''''''''
.. autofunction:: kim.pipelines.static.get_static_value


Exceptions
----------

.. autoexception:: kim.exception.KimException
.. autoexception:: kim.exception.MapperError
.. autoexception:: kim.exception.MappingInvalid
.. autoexception:: kim.exception.RoleError
.. autoexception:: kim.exception.FieldOptsError
.. autoexception:: kim.exception.FieldError
.. autoexception:: kim.exception.FieldInvalid
.. autoexception:: kim.exception.StopPipelineExecution
