# encoding: utf-8
import pytest
import mock

from kim import (
    MappingInvalid, MapperError, Mapper, PolymorphicMapper, blacklist, Integer,
    Collection, String, whitelist)
from kim.pipelines import marshaling
from kim.pipelines import serialization

from .helpers import TestType
from .fixtures import SchedulableMapper, EventMapper


def test_field_serialize_from_source():
    """On TestType, our score field is called 'normalised_score' but in the
    json output we just want it to be called 'score'"""

    class MapperBase(Mapper):

        __type__ = TestType

        score = Integer(source='normalised_score')

    obj = TestType(normalised_score=5)

    mapper = MapperBase(obj=obj)
    result = mapper.serialize()

    assert result == {'score': 5}


def test_field_marshal_to_source():
    """On TestType, our score field is called 'normalised_score' but in the
    json input we just want it to be called 'score'"""

    class MapperBase(Mapper):

        __type__ = TestType

        score = Integer(source='normalised_score')

    data = {'score': 5}

    mapper = MapperBase(data=data)
    result = mapper.marshal()

    assert result.normalised_score == 5


def test_field_serialize_from_source_collection():

    class MapperBase(Mapper):

        __type__ = TestType

        scores = Collection(Integer(), source='normalised_scores')

    obj = TestType(normalised_scores=[1, 2, 3])

    mapper = MapperBase(obj=obj)
    result = mapper.serialize()

    assert result == {'scores': [1, 2, 3]}


def test_field_marshal_to_source_collection():

    class MapperBase(Mapper):

        __type__ = TestType

        scores = Collection(Integer(), source='normalised_scores')

    data = {'scores': [1, 2, 3]}

    mapper = MapperBase(data=data)
    result = mapper.marshal()

    assert result.normalised_scores == [1, 2, 3]


def test_field_serialize_from_name():
    """On TestType, we have not defined a custom source so 'name' should be
    used in the json output"""

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

    obj = TestType(score=5)

    mapper = MapperBase(obj=obj)
    result = mapper.serialize()

    assert result == {'score': 5}


def test_field_marshal_to_name():
    """On TestType, we have not defined a custom source so 'name' should be
    used when updating the object"""

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

    data = {'score': 5}

    mapper = MapperBase(data=data)
    result = mapper.marshal()

    assert result.score == 5


def test_field_marshal_required():
    """A required field is not present, so an error should be raied"""

    class MapperBase(Mapper):

        __type__ = TestType

        name = String()  # required=True is default

    data = {}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()


def test_field_marshal_required_none():
    """A required field is None, so an error should be raied"""

    class MapperBase(Mapper):

        __type__ = TestType

        name = String()  # required=True is default

    data = {'name': None}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()


def test_field_marshal_none_allow_none():
    """A non required field is None, but allow_none is True,
    so an error should not be raised"""

    class MapperBase(Mapper):

        __type__ = TestType

        name = String(required=False)  # allow_none=True is the default

    data = {'name': None}

    mapper = MapperBase(data=data)
    result = mapper.marshal()
    assert result.name is None


def test_field_marshal_none_allow_none_false():
    """A non required field is None, allow_none is False,
    so an error should be raised"""

    class MapperBase(Mapper):

        __type__ = TestType

        name = String(required=False, allow_none=False)

    data = {'name': None}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()


def test_mapper_top_level_validate_with_fieldinvalid():

    class MapperBase(Mapper):

        __type__ = TestType

        password = String(
            error_msgs={'must_match': 'Passwords must match'})
        password_confirm = String()

        def validate(self, output):
            if output.password != output.password_confirm:
                self.fields['password'].invalid('must_match')

    data = {'password': 'abc', 'password_confirm': 'abc'}

    mapper = MapperBase(data=data)
    mapper.marshal()

    data = {'password': 'abc', 'password_confirm': 'xyz'}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()

    assert mapper.errors == {'password': 'Passwords must match'}


def test_mapper_top_level_validate_with_mappinginvalid():

    class MapperBase(Mapper):

        __type__ = TestType

        name = String()
        age = Integer()

        def validate(self, output):
            if output.name == 'jack' and output.age != 36:
                raise MappingInvalid(
                    {'name': 'wrong age for jack', 'age': 'jack must be 36'})

    data = {'name': 'jack', 'age': 36}

    mapper = MapperBase(data=data)
    mapper.marshal()

    data = {'name': 'jack', 'age': 25}

    mapper = MapperBase(data=data)
    with pytest.raises(MappingInvalid):
        mapper.marshal()

    assert mapper.errors == {
        'name': 'wrong age for jack', 'age': 'jack must be 36'}


def test_mapper_marshal_partial():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'name': 'bob'}
    obj = TestType(id=2, unrelated_attribute='test')

    mapper = MapperBase(obj=obj, data=data, partial=True)
    result = mapper.marshal()

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'
    assert result.unrelated_attribute == 'test'


def test_mapper_marshal_partial_with_name():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String(name='my_name', source='name')

    data = {'my_name': 'bob'}
    obj = TestType(id=2, unrelated_attribute='test')

    mapper = MapperBase(obj=obj, data=data, partial=True)
    result = mapper.marshal()

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'
    assert result.unrelated_attribute == 'test'


def test_mapper_serialize_partial():
    # partial=True should have no effect on serializing

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj=obj, partial=True)
    result = mapper.serialize()

    assert result == {'id': 2, 'name': 'bob'}


def test_marshal_polymorphic_mapper():

    data = {
        'object_type': 'event',
        'name': 'Test Event',
        'location': 'London',
    }
    mapper = SchedulableMapper(data=data)
    data = mapper.marshal()

    assert data.name == 'Test Event'
    assert data.location == 'London'


def test_marshal_polymorphic_mapper_polymorphic_key_missing():

    data = {
        'name': 'Test Event',
        'location': 'London',
    }
    mapper = SchedulableMapper(data=data)

    with pytest.raises(MappingInvalid):
        data = mapper.marshal()


def test_marshal_polymorphic_mapper_marshal_disabled():

    class MapperA(PolymorphicMapper):

        id = Integer(read_only=True)
        name = String()
        object_type = String(choices=['event', 'task'])

        __mapper_args__ = {
            'polymorphic_on': object_type,
            'allow_polymorphic_marshal': False,
        }

    class MapperB(MapperA):

        __mapper_args__ = {
            'polymorphic_name': 'task'
        }

    data = {
        'object_type': 'event',
        'name': 'Test Event',
        'location': 'London',
    }

    with pytest.raises(MappingInvalid):
        MapperA(data=data)


def test_serialize_polymorphic_mapper():

    obj = TestType(id=2, name='bob', location='London', object_type='event')

    mapper = SchedulableMapper(obj=obj)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'object_type': 'event',
        'location': 'London'
    }


def test_serialize_polymorphic_invalid_polymorphic_key():

    obj = TestType(id=2, name='bob', location='London', object_type='unknown')

    with pytest.raises(MapperError):
        SchedulableMapper(obj=obj)


def test_serialize_polymorphic_type_directly():

    obj = TestType(id=2, name='bob', location='London', object_type='event')

    mapper = EventMapper(obj=obj)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'object_type': 'event',
        'location': 'London'
    }


def test_marshal_with_mapper_directly_doesnt_require_polymorphic_key():

    data = {
        'name': 'Test Event',
        'location': 'London',
    }
    mapper = EventMapper(data=data)

    data = mapper.marshal()
    print(data)


def test_marshal_polymorphic_mapper_directly():

    data = {
        'object_type': 'event',
        'name': 'Test Event',
        'location': 'London',
    }
    mapper = EventMapper(data=data)
    data = mapper.marshal()

    assert data.name == 'Test Event'
    assert data.location == 'London'


def test_serialize_polymorphic_mapper_with_role():

    obj = TestType(id=2, name='bob', object_type='event', location='London')

    mapper = SchedulableMapper(obj=obj)
    data = mapper.serialize(role='public')

    assert data == {
        'name': 'bob',
        'id': 2,
        'location': 'London'
    }


def test_serialize_polymorphic_child_mapper_with_role():


    obj = TestType(id=2, name='bob', object_type='event', location='London')

    mapper = EventMapper(obj=obj)
    data = mapper.serialize(role='event_only_role')

    assert data == {
        'id': 2,
        'location': 'London'
    }


def test_serialize_polymorphic_child_mapper_with_deferred_role():


    obj = TestType(id=2, name='bob', object_type='event', location='London')

    mapper = EventMapper(obj=obj)
    data = mapper.serialize(role='event_only_role', deferred_role=whitelist('id'))

    assert data == {
        'id': 2,
    }


def test_serialize_polymorphic_child_mapper_deferred_role_fields_across_types():


    obj = TestType(id=2, name='bob', object_type='event', location='London')
    obj2 = TestType(id=3, name='bob', object_type='task', status='failed')

    mapper = SchedulableMapper(obj=obj)
    data = mapper.serialize(
        role='public', deferred_role=whitelist('id', 'status', 'location'))

    assert data == {
        'id': 2,
        'location': 'London'
    }

    mapper = SchedulableMapper(obj=obj2)
    data = mapper.serialize(
        role='public', deferred_role=whitelist('id', 'status', 'location'))

    assert data == {
        'id': 3,
        'status': 'failed'
    }


def test_serialize_polymorphic_child_mapper_deferred_role_disallowed_fields():


    obj = TestType(id=2, name='bob', object_type='event', location='London')
    obj2 = TestType(id=3, name='bob', object_type='task', status='failed')

    mapper = SchedulableMapper(obj=obj)
    data = mapper.serialize(
        role='name_only', deferred_role=whitelist('id', 'name'))

    assert data == {
        'name': 'bob'
    }


def test_serialize_polymorphic_child_mapper_deferred_role_blacklist():


    obj = TestType(id=2, name='bob', object_type='event', location='London')

    mapper = SchedulableMapper(obj=obj)
    data = mapper.serialize(
        role='public', deferred_role=blacklist('id'))

    assert data == {
        'name': 'bob',
        'location': 'London',
    }


def test_serialize_polymorphic_child_mapper_existing_blacklist_with_deferred():


    obj = TestType(id=2, name='bob', object_type='event', location='London')

    mapper = SchedulableMapper(obj=obj)
    data = mapper.serialize(
        role='event_blacklist', deferred_role=whitelist('id'))

    assert data == {
        'id': 2,
    }


def test_serialize_polymorphic_child_mapper_deferred_role_requires_role():


    obj = TestType(id=2, name='bob', object_type='event', location='London')

    mapper = SchedulableMapper(obj=obj)
    with pytest.raises(MapperError):
        mapper.serialize(role='public', deferred_role='foo')



def test_serialize_polymorphic_mapper_many():

    obj1 = TestType(id=2, name='bob', location='London', object_type='event')
    obj2 = TestType(id=3, name='fred', status='Done', object_type='task')

    result = SchedulableMapper.many().serialize([obj1, obj2], role='public')

    assert result == [
        {
            'id': 2,
            'name': 'bob',
            'location': 'London'
        },
        {
            'id': 3,
            'name': 'fred',
            'status': 'Done'
        }
    ]


def test_serialize_polymorphic_mapper_many_with_deferred_role():

    obj1 = TestType(id=2, name='bob', location='London', object_type='event')
    obj2 = TestType(id=3, name='fred', status='Done', object_type='task')

    result = SchedulableMapper.many().serialize(
        [obj1, obj2], role='public', deferred_role=whitelist('id'))

    assert result == [
        {
            'id': 2,
        },
        {
            'id': 3,
        }
    ]


def test_mapper_serialize_with_default():

    class MapperBase(Mapper):

        __type__ = TestType

        name = String(default='my default')

    obj = TestType()

    mapper = MapperBase(obj=obj)
    result = mapper.serialize()

    assert result == {'name': 'my default'}
