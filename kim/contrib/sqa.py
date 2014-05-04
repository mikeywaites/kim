# encoding: utf-8
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound

from ..serializers import Serializer
from ..mapping import MarshalIterator

from ..types import Nested, NumericType
from ..exceptions import ValidationError


class NestedForeignKey(Nested):
    """Field which can function as a normal Nested field, but can also take an
    integer foreign key when marshalled. In which case, it will look up the
    required object via self.getter."""

    def __init__(self, *args, **kwargs):
        self.getter = kwargs.get('getter', None)
        self.marshal_by_key_only = kwargs.get('marshal_by_key_only', True)
        super(NestedForeignKey, self).__init__(*args, **kwargs)

    def valid_id(self, val):

        return any([isinstance(val, int),
                    isinstance(val, basestring) and val.isdigit()])

    def get_object(self, source_value):
        if self.valid_id(source_value):
            obj = self.getter(int(source_value))
            if not obj:
                raise ValidationError('invalid id')
        else:
            if self.marshal_by_key_only:
                raise ValidationError('invalid type')
            obj = source_value
        return obj

    def validate(self, source_value):
        return super(NestedForeignKey, self).validate(self.get_object(source_value))

    def marshal_value(self, source_value, **kwargs):
        return self.get_object(source_value)

class NestedNew(Nested):
    """Field which can function as a normal Nested field, but can also take an
    integer foreign key when marshalled. In which case, it will look up the
    required object via self.getter."""

    # def __init__(self, *args, **kwargs):
    #     self.getter = kwargs.get('getter', None)
    #     self.marshal_by_key_only = kwargs.get('marshal_by_key_only', True)
    #     super(NestedForeignKey, self).__init__(*args, **kwargs)

    # def valid_id(self, val):

    #     return any([isinstance(val, int),
    #                 isinstance(val, basestring) and val.isdigit()])

    def get_object(self, source_value):
        return source_value
        # if self.valid_id(source_value):
        #     obj = self.getter(int(source_value))
        #     if not obj:
        #         raise ValidationError('invalid id')
        # else:
        #     if self.marshal_by_key_only:
        #         raise ValidationError('invalid type')
        #     obj = source_value
        # return obj

    def validate(self, source_value):
        return super(NestedNew, self).validate(self.get_object(source_value))

    def marshal_value(self, source_value, **kwargs):
        mapping_iterator = kwargs.get('mapping_iterator')
        return mapping_iterator.run(self.get_mapping(), source_value, instance=self.get_object(source_value))

        # return self.get_object(source_value)



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


class SQAMarshalIterator(MarshalIterator):
    def __init__(self, instance):
        super(SQAMarshalIterator, self).__init__(output=instance)

    def update_output(self, field, value):
        if field.include_in_marshal():
            setattr(self.output, field.source, value)
            # if field.source == '__self__':
            #     self.output.update(value)
            # else:
            #     # Sources can be specified using dot notation which indicates
            #     # nested dicts should be created.
            #     # To handle this, we need to split off all but the last
            #     # part of the source string (the part after the final dot),
            #     # and create dicts for all the levels below that if they don't
            #     # already exist.
            #     # Finally, now we've resolved the nested level we actually want
            #     # to update, set the key in the last part to the value passed.
            #     components = field.source.split('.')
            #     components_except_last = components[:-1]
            #     last_component = components[-1]
            #     current_component = self.output
            #     for component in components_except_last:
            #         current_component.setdefault(component, {})
            #         current_component = current_component[component]
            #     current_component[last_component] = value

    def process_field(self, field, data):

        value = self.get_attribute(data, field.name)
        try:
            field.validate(value)
        except ValidationError as e:
            raise FieldError(field.name, e.message)

        to_marshal = value if value is not None else field.default
        if to_marshal is not None:
            return field.marshal_value(to_marshal, mapping_iterator=self.__class__)


class SQASerializer(Serializer):

    def serialize(self, data, **kwargs):
        return super(SQASerializer, self).serialize(data, **kwargs)

    def get_model(self):
        return self.__model__()

    def get_new_model(self):
        return self.get_model()

    def marshal(self, data, role=None, instance=None, **kwargs):
        model_instance = instance or self.get_model()
        return SQAMarshalIterator.run(self.get_mapping(role=role), data, instance=model_instance)
        # # result_dict = super(SQASerializer, self).marshal(data, **kwargs)
        # model_instance = instance or self.get_model()
        # marshal_sqa(model_instance, result_dict)
        # return model_instance
