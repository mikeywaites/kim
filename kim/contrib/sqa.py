# encoding: utf-8
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound

from ..serializers import Serializer
from ..mapping import MarshalVisitor, SerializeVisitor

from ..types import Nested, NumericType
from ..exceptions import ValidationError


def nested_foreign_key_validator(type_, source_value):

    if type(source_value) != dict:
        raise ValidationError('invalid type')

    id = source_value.get(type_.id_field_name)
    if not id:
        raise ValidationError('no id passed')
    id = int(id)
    if self.valid_id(id):
        try:
            obj = self.getter(id)
        except NoResultFound:
            obj = None
        if not obj:
            raise ValidationError('invalid id')
    return obj


class NestedForeignKey(Nested):
    """Field which can function as a normal Nested field, but can also take an
    integer foreign key in an 'id' field when marshalled. In which case, it
    will look up the required object via self.getter."""

    validators = [nested_foreign_key_validator, ]

    __visit_name__ = "nested_foreign_key"

    def __init__(self, *args, **kwargs):
        self.getter = kwargs.pop('getter', None)
        self.id_field_name = kwargs.pop('id_field_name', 'id')
        super(NestedForeignKey, self).__init__(*args, **kwargs)

    def valid_id(self, val):

        return any([isinstance(val, int),
                    isinstance(val, basestring) and val.isdigit()])

    def get_object(self, source_value):
        if type(source_value) != dict:
            raise ValidationError('invalid type')
        id = source_value.get(self.id_field_name)
        if not id:
            raise ValidationError('no id passed')
        id = int(id)
        if self.valid_id(id):
            try:
                obj = self.getter(id)
            except NoResultFound:
                obj = None
            if not obj:
                raise ValidationError('invalid id')
        return obj

    def validate(self, source_value):
        super(Nested, self).validate(source_value) # HACK: bypassing Nested.validate
        if source_value:
            return self.get_object(source_value)

    def marshal_value(self, source_value):
        return self.get_object(source_value)


def find_by_id(type_, source):
    if source is not None:
        try:
            obj = type_.getter(source)
        except NoResultFound:
            obj = None
        if not obj:
            raise ValidationError('invalid id')
    return True


class IntegerForeignKey(NumericType):
    """Field representing an Integer ForeignKey. Behaves as NumericType, but will
    look up the required object via self.getter to ensure it exists/is valid"""

    validators = [find_by_id, ]

    def __init__(self, *args, **kwargs):
        self.getter = kwargs.pop('getter', None)
        super(IntegerForeignKey, self).__init__(*args, **kwargs)

    def validate(self, source_value):
        super(IntegerForeignKey, self).validate(source_value)
        if source_value is not None:
            try:
                obj = self.getter(source_value)
            except NoResultFound:
                obj = None
            if not obj:
                raise ValidationError('invalid id')
        return True


# def marshal_sqa(instance, result):
#     for k, v in result.iteritems():
#         if type(v) == dict:
#             # This is a nested serializer

#             # First check if the relationship already exists
#             existing = getattr(instance, k)
#             if existing:
#                 # Exists, just update it
#                 marshal_sqa(existing, v)
#             else:
#                 # If it doesn't exist, we need to create it

#                 # Find what sort of model we require by introspection of
#                 # the relationship
#                 inspection = inspect(instance)
#                 relationship = inspection.mapper.relationships[k]
#                 RemoteClass = relationship.mapper.class_

#                 # Now create a new instance of that model and set the relationship
#                 remote_instance = RemoteClass()
#                 setattr(instance, k, remote_instance)
#                 marshal_sqa(remote_instance, v)
#         else:
#             # This is a normal field, just update it on the model instance
#             setattr(instance, k, v)


class SQASerializeVisitor(SerializeVisitor):
    def visit_type_nested_foreign_key(self, type, data):
        return self.visit_type_default(type, data)



class SQAMarshalVisitor(MarshalVisitor):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        self.instance = kwargs.pop('instance', None)
        super(SQAMarshalVisitor, self).__init__(*args, **kwargs)

    def update_output(self, field, value):
        if not field.read_only:
            setattr(self.output, field.source, value)

    def initialise_output(self):
        if not self.instance:
            self.output = self.model()
        else:
            self.output = self.instance

    def visit_type_nested(self, type, data, instance=None):
        return SQAMarshalVisitor(type.mapping, data, instance=instance)._run()

    def visit_field_nested(self, field, data):
        existing = getattr(self.output, field.source)
        if existing:
            # Exists, just update it
            return self.visit_type_nested(field.field_type, data, instance=existing)
        else:
            # If it doesn't exist, we need to create it
            # Find what sort of model we require by introspection of
            # the relationship
            inspection = inspect(self.output)
            relationship = inspection.mapper.relationships[field.source]
            RemoteClass = relationship.mapper.class_

            # Now create a new instance of that model and set the relationship
            remote_instance = RemoteClass()
            setattr(self.output, field.source, remote_instance)
            return self.visit_type_nested(field.field_type, data, instance=remote_instance)

    def visit_type_nested_foreign_key(self, type, data):
        return self.visit_type_default(type, data)


class SQASerializer(Serializer):

    def marshal(self, data, instance=None, **kwargs):
        return SQAMarshalVisitor.run(self.get_mapping(), data, model=self.__model__, instance=instance, **kwargs)

    def serialize(self, data, **kwargs):
        return SQASerializeVisitor.run(self.get_mapping(), data, **kwargs)
