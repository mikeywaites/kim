# encoding: utf-8
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound

from ..serializers import Serializer

from ..types import Nested, NumericType
from ..exceptions import ValidationError


class NestedForeignKey(Nested):
    """Field which can function as a normal Nested field, but can also take an
    integer foreign key in an 'id' field when marshalled. In which case, it
    will look up the required object via self.getter."""

    def __init__(self, *args, **kwargs):
        self.getter = kwargs.get('getter', None)
        self.id_field_name = kwargs.get('id_field_name', 'id')
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


class IntegerForeignKey(NumericType):
    """Field representing an Integer ForeignKey. Behaves as NumericType, but will
    look up the required object via self.getter to ensure it exists/is valid"""

    def __init__(self, *args, **kwargs):
        self.getter = kwargs.get('getter', None)
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


def marshal_sqa(instance, result):
    for k, v in result.iteritems():
        if type(v) == dict:
            # This is a nested serializer

            # First check if the relationship already exists
            existing = getattr(instance, k)
            if existing:
                # Exists, just update it
                marshal_sqa(existing, v)
            else:
                # If it doesn't exist, we need to create it

                # Find what sort of model we require by introspection of
                # the relationship
                inspection = inspect(instance)
                relationship = inspection.mapper.relationships[k]
                RemoteClass = relationship.mapper.class_

                # Now create a new instance of that model and set the relationship
                remote_instance = RemoteClass()
                setattr(instance, k, remote_instance)
                marshal_sqa(remote_instance, v)
        else:
            # This is a normal field, just update it on the model instance
            setattr(instance, k, v)


class SQASerializer(Serializer):

    def serialize(self, data, **kwargs):
        return super(SQASerializer, self).serialize(data, **kwargs)

    def get_model(self):
        return self.__model__()

    def get_new_model(self):
        return self.get_model()

    def marshal(self, data, instance=None, **kwargs):
        result_dict = super(SQASerializer, self).marshal(data, **kwargs)
        model_instance = instance or self.get_model()
        marshal_sqa(model_instance, result_dict)
        return model_instance
