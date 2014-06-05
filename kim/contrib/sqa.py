# encoding: utf-8
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound

from ..serializers import Serializer
from ..mapping import MarshalVisitor, SerializeVisitor

from ..types import Nested, NumericType
from ..exceptions import ValidationError, ConfigurationError


class NestedForeignKey(Nested):
    """Field which can function as a normal Nested field, but can also take an
    integer foreign key in an 'id' field when marshalled. In which case, it
    will look up the required object via self.getter."""

    __visit_name__ = "nested_foreign_key"

    def __init__(self, *args, **kwargs):
        self.getter = kwargs.pop('getter', None)
        self.id_field_name = kwargs.pop('id_field_name', 'id')
        self.allow_updates = kwargs.pop('allow_updates', False)
        self.allow_updates_in_place = kwargs.pop('allow_updates_in_place', False)
        self.allow_create = kwargs.pop('allow_create', False)
        if self.allow_updates_in_place and self.allow_create:
            raise ConfigurationError('allow_create and allow_updates_in_place may not be used together')
        super(NestedForeignKey, self).__init__(*args, **kwargs)

    def valid_id(self, val):

        return any([isinstance(val, int),
                    isinstance(val, basestring) and val.isdigit()])

    def get_object(self, source_value):
        if type(source_value) != dict:
            raise ValidationError('invalid type')
        id = source_value.get(self.id_field_name)
        if self.valid_id(id):
            id = int(id)
            try:
                obj = self.getter(id)
            except NoResultFound:
                obj = None
            if not obj:
                raise ValidationError('invalid id')
            return obj

    def validate(self, source_value):
        if source_value is not None:
            if self.get_object(source_value):
                return True
            else:
                super(NestedForeignKey, self).validate(source_value)


class IntegerForeignKey(NumericType):
    """Field representing an Integer ForeignKey. Behaves as NumericType, but will
    look up the required object via self.getter to ensure it exists/is valid"""

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


class SQASerializeVisitor(SerializeVisitor):
    def visit_type_nested_foreign_key(self, type, data):
        return SQASerializeVisitor(type.mapping, data)._run()


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

    def visit_type_nested_foreign_key(self, type, data, instance=None, model=None):
        # 1. User has passed an id and no updates are allowed.
        #    Resolve the id to an object and return immediately
        # 2. User has passed an id and updates are allowed.
        #    Resolve the id to an object and call recursively to update it
        # 3. Object already exists, user has not passed an id and in place
        #    updates are allowed. Call recursively to update existing object.
        # 4. User has not passed an id and creation of new objects is allowed
        #    Call recursively to create a new object
        # 5. User has not passed an id and creation of new objects is not
        #    allowed, nor are in place updates. Raise an exception.

        resolved = type.get_object(data)

        if resolved:
            if type.allow_updates:
                return SQAMarshalVisitor(type.mapping, data, instance=resolved, model=model)._run()
            else:
                return resolved
        else:
            if type.allow_updates_in_place:
                return SQAMarshalVisitor(type.mapping, data, instance=instance, model=model)._run()
            elif type.allow_create:
                return SQAMarshalVisitor(type.mapping, data, model=model)._run()
            else:
                raise ValidationError('No id passed and creation or update in place not allowed')

    def visit_field_nested_foreign_key(self, field, data):
        existing = getattr(self.output, field.source)

        # Find what sort of model we require by introspection of
        # the relationship
        inspection = inspect(self.output)
        relationship = inspection.mapper.relationships[field.source]
        RemoteClass = relationship.mapper.class_

        return self.visit_type_nested_foreign_key(field.field_type, data, instance=existing, model=RemoteClass)


class SQASerializer(Serializer):

    def marshal(self, data, instance=None, **kwargs):
        return SQAMarshalVisitor.run(self.get_mapping(), data, model=self.__model__, instance=instance, **kwargs)

    def serialize(self, data, **kwargs):
        return SQASerializeVisitor.run(self.get_mapping(), data, **kwargs)
