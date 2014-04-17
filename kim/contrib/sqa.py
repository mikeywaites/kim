from sqlalchemy.inspection import inspect

from ..serializers import Serializer

from ..types import Integer, Nested
from ..exceptions import ValidationError


class NestedForeignKey(Nested):
    def __init__(self, *args, **kwargs):
        self.getter = kwargs.get('getter', None)
        super(NestedForeignKey, self).__init__(*args, **kwargs)

    def get_object(self, source_value):
        return self.getter(source_value)

    def validate_for_marshal(self, source_value):
        return super(NestedForeignKey, self).validate(self.get_object(source_value))

    def marshal_value(self, source_value):
        return self.get_object(source_value)


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
    def __init__(self, instance=None, input=None, **kwargs):
        super(SQASerializer, self).__init__(data=instance, input=input, **kwargs)

    def serialize(self, **kwargs):
        return super(SQASerializer, self).serialize(**kwargs)

    def get_model(self):
        return self.__model__

    def get_model_or_instance(self):
        return self.source_data or self.get_model()()

    def marshal(self, **kwargs):
        result_dict = super(SQASerializer, self).marshal(**kwargs)
        instance = self.get_model_or_instance()
        marshal_sqa(instance, result_dict)
        return instance
