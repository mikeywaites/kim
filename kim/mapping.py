#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import defaultdict

from .exceptions import ValidationError, MappingErrors, FieldError
from .utils import is_valid_field


class BaseMapping(object):
    pass


class Mapping(BaseMapping):
    """:class:`kim.mapping.Mapping` is a factory for generating data
    structures in KIM.

    A mapping consists of a collection of kim `field` types.

    `Mappings` are created by passing `Fields` to the
    contructor of :class:`kim.mapping.Mapping`

     e.g.::

        my_mapping = Mapping(
             String('name'),
             Integer('id'),
        )

    The first argument to the Mapping type is the name of this mapping,
    the following arguments may be any mixture of `Field` types.

    :param fields: contains the `collection` of Field types provided

        Any field inherting from :class:`kim.fields.BaseType` is considered
        to be a valid field passed into a mapping.

    :param collection: Provided as a keyword arg to a `mapping` sets the data
                       structure used to store `fields` in. (default list)

    .. seealso::

        :class:`kim.fields.BaseType`

    """

    def __init__(self, *args, **kwargs):
        """:class:`kim.mapping.Mapping` constructor.

        """
        mapped_types = args[0:]

        self.fields = kwargs.get('collection', list())
        self.validator = kwargs.get('validator', None)

        self._arg_loop(mapped_types)

    def __iter__(self):
        return iter(self.fields)

    def _arg_loop(self, items):
        """Iterates over collection of constructor args and assigns
        accordingly.

        :param items: collection of Field and Role type args.

        :returns: None
        """

        for item in items:
            if is_valid_field(item):
                self.add_field(item)

    def add_field(self, field):
        """Add a `field` type to the `fields` collection.

        :param field: A field type

        .. seealso::
            :class:`kim.fields.BaseType`

        :returns: None
        """
        self.fields.append(field)


def _get_attribute(data, attr):
    if attr == '__self__':
        return data
    elif isinstance(data, dict):
        return data.get(attr)
    else:
        return getattr(data, attr, None)


def get_attribute(data, attr):
    """Attempt to find the value for a `field` from `data`.

    :param data: dict like object containing input data
    :param field: mapped field.

    :returns: the value for `field` from `data`
    """
    # Dot notation can be used to span relationships. To handle this, we need
    # to call _get_attribute recursively until we get down to the level
    # specified
    components = attr.split('.')
    for component in components:
        data = _get_attribute(data, component)
    return data


# class MappingIterator(object):

#     def __init__(self, output=None, errors=None):
#         self.output = output or dict()
#         self.errors = errors or defaultdict(list)

#     def get_attribute(self, data, field_name):
#         """return the value of field_name from data.

#         .. seealso::
#             :func:`kim.mapping.get_attribute`

#         """
#         return get_attribute(data, field_name)

#     @classmethod
#     def run_many(cls, mapping, data, **kwargs):
#         output = []
#         errors = []
#         has_errors = False
#         for d in data:
#             try:
#                 output.append(cls.run(mapping, d, many=False))
#             except MappingErrors as e:
#                 has_errors = True
#                 errors.append(e.message)
#             else:
#                 errors.append({})

#         if has_errors:
#             raise MappingErrors(errors)

#         return output

#     @classmethod
#     def run_one(cls, mapping, data, **kwargs):
#         return cls()._run(mapping, data, **kwargs)

#     @classmethod
#     def run(cls, mapping, data, many=False, **kwargs):
#         if many:
#             return cls.run_many(mapping, data, **kwargs)
#         else:
#             return cls.run_one(mapping, data, **kwargs)

#     def _run(self, mapping, data, **kwargs):
#         """`run` the mapping iteration loop.

#         :param data: dict like data being mapped
#         :param mapping: :class:`kim.mapping.Mapping`
#         :param many: map several instances of `data` to `mapping`

#         :raises: MappingErrors
#         :returns: serializable output
#         """

#         for field in mapping.fields:
#             try:
#                 value = self.process_field(field, data)
#                 self.update_output(field, value)
#             except (ValidationError, FieldError) as e:
#                 self.errors[field.name].append(e.message)
#                 continue

#         self.post_process(mapping)

#         if self.errors:
#             raise MappingErrors(dict(self.errors))

#         return self.output

#     def process_field(self, field, data):
#         """Process a field mapping using `data`.  This method should
#         return both the field.name or field.source value plus the value to
#         map to the field.

#         e.g::
#             value = self.get_attribute(data, field.source)
#             field.validate(value)

#             return field.marshal_value(value or field.default)
#         """

#         raise NotImplementedError("Concrete classes must inplement "
#                                   "process_field method")

#     def update_output(self, field, value):

#         raise NotImplementedError("Concrete classes must inplement "
#                                   "update_output method")

#     def post_process(self, mapping):
#         """Called after all other fields have been processed. Can be used
#         by concrete classes eg. to implement whole-mapping validation."""
#         pass


# class MarshalIterator(MappingIterator):

#     def update_output(self, field, value):
#         if not field.read_only:
#             if field.source == '__self__':
#                 self.output.update(value)
#             else:
#                 # Sources can be specified using dot notation which indicates
#                 # nested dicts should be created.
#                 # To handle this, we need to split off all but the last
#                 # part of the source string (the part after the final dot),
#                 # and create dicts for all the levels below that if they don't
#                 # already exist.
#                 # Finally, now we've resolved the nested level we actually want
#                 # to update, set the key in the last part to the value passed.
#                 components = field.source.split('.')
#                 components_except_last = components[:-1]
#                 last_component = components[-1]
#                 current_component = self.output
#                 for component in components_except_last:
#                     current_component.setdefault(component, {})
#                     current_component = current_component[component]
#                 current_component[last_component] = value

#     def process_field(self, field, data):

#         value = self.get_attribute(data, field.name)
#         #try:
#         #    field.is_valid(value)
#         #except ValidationError as e:
#         #    raise FieldError(field.name, e.message)

#         to_marshal = value if value is not None else field.default
#         if to_marshal is not None:
#             return field.marshal(to_marshal)

#     def post_process(self, mapping):
#         if mapping.validator:
#             try:
#                 mapping.validator(self.output)
#             except MappingErrors as e:
#                 self.errors = e.message


# class SerializeIterator(MappingIterator):

#     def update_output(self, field, value):

#         self.output[field.name] = value

#     def process_field(self, field, data):

#         value = self.get_attribute(data, field.source)

#         to_serialize = value if value is not None else field.default
#         if to_serialize is not None:
#             return field.serialize(to_serialize)



class Visitor(object):
    def __init__(self, mapping, data):
        self.mapping = mapping
        self.data = data

    def visit(self, type, data):
        name = 'visit_%s' % type.__visit_name__
        return getattr(self, name)(type, data)

    def validate(self, field, data):
        return True

    def run(self):
       self.output = {}
       for field in self.mapping:
           data = self.get_data(field)
           if not data:
               data = field.default
           if self.validate(field, data):
               result = self.visit(field.field_type, data)
               self.update_output(field, result)
       return self.output


class SerializeVisitor(Visitor):
    def get_data(self, field):
        return get_attribute(self.data, field.source)

    def update_output(self, field, result):
        self.output[field.name] = result

    def visit_default(self, type, data):
         return type.serialize_value(data)

    def visit_nested(self, type, data):
        return SerializeVisitor(type.mapping, data).run()

    def visit_collection(self, type, data):
        result = []
        for value in type.serialize_members(data):
            value = self.visit(type.inner_type, value)
            result.append(value)
        return result


class MarshalVisitor(Visitor):
    def __init__(self, *args, **kwargs):
        super(MarshalVisitor, self).__init__(*args, **kwargs)
        self.errors = defaultdict(list)

    def get_data(self, field):
        return get_attribute(self.data, field.name)

    def validate(self, field, data):
        if field.read_only:
            return False
        try:
            if field.is_valid(data):
                return data
        except ValidationError as e:
            self.errors[field.name].append(e.message)

    def update_output(self, field, result):
        self.output[field.source] = result

    def visit_default(self, type, data):
         return type.marshal_value(data)

    def visit_nested(self, type, data):
        return MarshalVisitor(type.mapping, data).run()

    def visit_collection(self, type, data):
        result = []
        for value in type.marshal_members(data):
            value = self.visit(type.inner_type, value)
            result.append(value)
        return result

    def run(self):
        output = super(MarshalVisitor, self).run()
        self.post_process()
        if self.errors:
            raise MappingErrors(self.errors)
        else:
            return output

    def post_process(self):
        if self.mapping.validator:
            try:
                self.mapping.validator(self.output)
            except MappingErrors as e:
                self.errors = e.message

def _run(Visitor, mapping, data, many=False):
    if many:
        result = []
        errors = []
        has_errors = False
        for d in data:
            try:
                result.append(Visitor(mapping, d).run())
                errors.append({})
            except MappingErrors as e:
                errors.append(e.message)
                has_errors = True
        if has_errors:
            raise MappingErrors(errors)
        else:
            return result
    else:
        return Visitor(mapping, data).run()

def serialize(mapping, data, many=False):
    return _run(SerializeVisitor, mapping, data, many=many)

def marshal(mapping, data, many=False):
    return _run(MarshalVisitor, mapping, data, many=many)

