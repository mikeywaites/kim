# encoding: utf-8
from collections import defaultdict

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.exc import NoResultFound

from ..serializers import Serializer
from ..mapping import MarshalVisitor, SerializeVisitor, get_attribute

from ..types import Nested, NumericType, Collection
from ..exceptions import ValidationError, ConfigurationError
from ..utils import recursive_defaultdict


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
        self.remote_class = kwargs.pop('remote_class', None)
        if self.allow_updates_in_place and self.allow_create:
            raise ConfigurationError('allow_create and allow_updates_in_place may not be used together')
        super(NestedForeignKey, self).__init__(*args, **kwargs)

    def valid_id(self, val):
        return any([isinstance(val, int),
                    isinstance(val, basestring) and val.isdigit()])

    def get_object(self, source_value):
        if self.allow_updates_in_place:
            return
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


class RelationshipCollection(Collection):
    __visit_name__ = 'relationship_collection'

    def __init__(self, *args, **kwargs):
        self.remote_class = kwargs.pop('remote_class', None)
        super(RelationshipCollection, self).__init__(*args, **kwargs)


class SQASerializeVisitor(SerializeVisitor):
    def visit_type_nested_foreign_key(self, type, data, **kwargs):
        return self.visit_type_nested(type, data, **kwargs)

    def visit_type_relationship_collection(self, type, data, **kwargs):
        return self.visit_type_collection(type, data)


class SQAMarshalVisitor(MarshalVisitor):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model', None)
        self.instance = kwargs.pop('instance', None)
        self.partial = kwargs.pop('partial', False)
        super(SQAMarshalVisitor, self).__init__(*args, **kwargs)

    def get_data(self, field):
        """ Override super so if instance and partial we can populate the
        field data from the instance.
        """

        if self.instance and self.partial:
            data = get_attribute(self.data, field.name)
            if data is None:
                data = get_attribute(self.instance, field.name)
            return data
        else:
            return super(SQAMarshalVisitor, self).get_data(field)

    def update_output(self, field, value):
        if not field.read_only:
            components = field.source.split('.')
            output = self.output
            for component in components[:-1]:
                output = getattr(output, component)
            setattr(output, components[-1], value)

    def initialise_output(self):
        if not self.instance:
            self.output = self.model()
        else:
            self.output = self.instance

    def _get_relationship_model(self, field):
        if field.field_type.remote_class:
            return field.field_type.remote_class
        # Find what sort of model we require by introspection of
        # the relationship
        components = field.source.split('.')
        RemoteClass = self.output
        for component in components:
            inspection = inspect(RemoteClass)
            relationship = inspection.mapper.relationships.get(component)
            RemoteClass = relationship.mapper.class_
        return RemoteClass

    def visit_type_nested_foreign_key(self, type, data, instance=None, model=None, **kwargs):
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
                return self.Cls(type.get_mapping(), data, instance=resolved, model=model)._run()
            else:
                return resolved
        else:
            if type.allow_updates_in_place:
                return self.Cls(type.get_mapping(), data, instance=instance, model=model)._run()
            elif type.allow_create:
                return self.Cls(type.get_mapping(), data, model=model)._run()
            else:
                raise ValidationError('No id passed and creation or update in place not allowed')

    def visit_field_nested_foreign_key(self, field, data):
        if data is not None:
            existing = get_attribute(self.output, field.source)
            RemoteClass = self._get_relationship_model(field)
            return self.visit_type_nested_foreign_key(field.field_type, data, instance=existing, model=RemoteClass)

    def visit_field_relationship_collection(self, field, data):
        existing_list = get_attribute(self.output, field.source)
        RemoteClass = self._get_relationship_model(field)
        return self.visit_type_relationship_collection(field.field_type, data, instance_list=existing_list, model=RemoteClass)

    def visit_type_relationship_collection(self, type, data, instance_list=None, model=None, **kwargs):
        result = []
        for i, value in enumerate(type.marshal_members(data)):
            try:
                instance = instance_list[i]
            except IndexError:
                instance = None
            value = self.visit_type(type.inner_type, value, instance=instance, model=model)
            result.append(value)
        return result


class SQARawSerializeVisitor(SQASerializeVisitor):
    Cls = SQASerializeVisitor # somewhat hacky: make nested calls go to the parent class not this one

    def _remove_none(self, output):
        # If all components of a dictionary are none, remove it and mark the entire thing as none
        all_none = True
        for k, v in output.iteritems():
            if type(v) == defaultdict:
                output[k] = self._remove_none(v)
            else:
                if v is not None:
                    all_none = False
        if all_none:
            return None
        else:
            return output

    def transform_data(self, data):
        """Transform flat data from a KeyedTuple with keys in the form:
            [
                'id',
                'name',
                'contact_details__phone',
                'contact_details__address__postcode'
            ]
            Into:
            {
                'id': x,
                'name': x,
                'contact_details': {
                    'phone': x,
                    'address': {
                        'postcode': x
                    }
                }
            }
        """
        output = recursive_defaultdict()
        for key in data.keys():
            path = key.split('__')
            target = output
            # Walk along the path until we find the final dict to insert the
            # data into
            for component in path[:-1]:
                target = target[component]
            # And finally set the key on the final dict to the relevant data
            target[path[-1]] = getattr(data, key)

        return self._remove_none(output)

    def __init__(self, mapping, data):
        transformed_data = self.transform_data(data)
        super(SQARawSerializeVisitor, self).__init__(mapping, transformed_data)


class SQASerializer(Serializer):

    def marshal(self, data, instance=None, role=None, **kwargs):
        return SQAMarshalVisitor.run(self.get_mapping(role=role), data, model=self.__model__, instance=instance, **kwargs)

    def serialize(self, data, role=None, raw=False, **kwargs):
        if raw:
            return SQARawSerializeVisitor.run(self.get_mapping(role=role), data, **kwargs)
        else:
            return SQASerializeVisitor.run(self.get_mapping(role=role), data, **kwargs)
