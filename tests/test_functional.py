import pytest
import mock

from kim.exception import MappingInvalid, FieldInvalid
from kim.mapper import Mapper, PolymorphicMapper
from kim.role import blacklist
from kim.field import Integer, Collection, String
from kim.pipelines import marshaling
from kim.pipelines import serialization

from .helpers import TestType
from .fixtures import SchedulableMapper


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


def test_marshal_with_input_validation_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @marshaling.validates('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(data=data)
    mapper.marshal()

    assert hook_mock.called
    assert hook_mock.call_count == 1


def test_serialize_with_validation_hooks():
    """Serialization should not run any validation hooks
    """

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @serialization.validates('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(obj=data)
    mapper.serialize()

    assert not hook_mock.called
    assert hook_mock.call_count == 0


def test_marshal_with_input_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @marshaling.inputs('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(data=data)
    mapper.marshal()

    assert hook_mock.called
    assert hook_mock.call_count == 1


def test_serialize_with_input_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @serialization.inputs('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(obj=data)
    mapper.serialize()

    assert hook_mock.called
    assert hook_mock.call_count == 1


def test_marshal_with_proces_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @marshaling.processes('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(data=data)
    mapper.marshal()

    assert hook_mock.called
    assert hook_mock.call_count == 1


def test_serialize_with_process_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @serialization.processes('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(obj=data)
    mapper.serialize()

    assert hook_mock.called
    assert hook_mock.call_count == 1


def test_marshal_with_output_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @marshaling.outputs('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(data=data)
    mapper.marshal()

    assert hook_mock.called
    assert hook_mock.call_count == 1


def test_serialize_with_output_hooks():

    hook_mock = mock.Mock()

    class MapperBase(Mapper):

        __type__ = TestType

        my_score = Integer(name='score')

        @serialization.outputs('score')
        def greater_than(session):

            hook_mock()

            return session.data

    data = {'score': 5}

    mapper = MapperBase(obj=data)
    mapper.serialize()

    assert hook_mock.called
    assert hook_mock.call_count == 1


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


def test_mapper_marshal_partial_with_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()
        ignore_this = String()

    data = {'name': 'bob', 'ignore_this': 'should be ignored'}
    obj = TestType(id=2, unrelated_attribute='test', ignore_this='unchanged')

    mapper = MapperBase(obj=obj, data=data, partial=True)
    result = mapper.marshal(role=blacklist('ignore_this'))

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'
    assert result.ignore_this == 'unchanged'
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
    assert data.object_type == 'event'


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

    data = {
        'object_type': 'event',
        'name': 'Test Event',
        'location': 'London',
    }
    mapper = SchedulableMapper(data=data)
    data = mapper.marshal()
    obj = TestType(id=2, name='bob', location='London', object_type='event')

    mapper = SchedulableMapper(obj=obj)
    result = mapper.serialize()

    assert result == {
        'id': 2,
        'name': 'bob',
        'object_type': 'event',
        'location': 'London'
    }
