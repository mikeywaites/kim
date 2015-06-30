import pytest

from kim.exception import MapperError
from kim.mapper import Mapper, _MapperConfig
from kim.field import Field, String, Integer
from kim.role import whitelist


class TestType(object):
    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class TestField(Field):
    pass


def test_mapper_sets_fields():
    """Ensure that on attributes inheriting from :class:`kim.fields.Field`
    are set in a mappers fields.
    """

    class MyTestMapper(Mapper):

        __type__ = TestType

        name = TestField()
        other = 'not a field'

    mapper_with_fields = MyTestMapper(data={})
    assert 'name' in mapper_with_fields.fields
    assert isinstance(mapper_with_fields.fields['name'], TestField)
    assert 'other' not in mapper_with_fields.fields
    assert not getattr(mapper_with_fields, 'name', False)


def test_mapper_must_define_mapper_type():
    """Ensure that a :class:`.MapperError` is raised if a :class:`.Mapper`
    fails to set its __type__ attr.
    """

    mapper = Mapper(data={})
    with pytest.raises(MapperError):
        mapper._get_mapper_type()


def test_mapper_inheritance():
    """test inheriting from other mapper classes
    """

    class OtherField(Field):
        pass

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

    class NewMapper(MapperBase):

        __type__ = TestType

        id = OtherField()
        additional_field = TestField()

    mapper = MapperBase(data={})
    other_mapper = NewMapper(data={})

    assert len(mapper.fields.keys()) == 2
    assert 'id' in mapper.fields
    assert 'name' in mapper.fields

    assert len(other_mapper.fields.keys()) == 3
    assert 'id' in other_mapper.fields
    assert 'name' in other_mapper.fields
    assert 'additional_field' in other_mapper.fields

    assert isinstance(other_mapper.fields['id'], OtherField)


def test_get_mapper_type():
    """ensure the correct object is returned when acessing the Mapper.__type__
    via :meth:``_get_mapper_type``
    """

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()

    mapper = MapperBase(data={})
    assert mapper._get_mapper_type() == TestType


def test_order_of_fields():
    """ensure fields set by mapper metaclass are set in order
    using _creation_order
    """

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

    class MyMapper(MapperBase):

        email = TestField()

    class ThirdMapper(MyMapper):

        id = TestField()
        id._creation_order = 999

    mapper = MyMapper(data={})
    assert ['id', 'name', 'email'] == list(mapper.fields.keys())

    mapper = ThirdMapper(data={})
    assert ['name', 'email', 'id'] == list(mapper.fields.keys())


def test_override_default_role():

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

        __roles__ = {
            '__default__': whitelist('id', )
        }

    mapper = MapperBase(data={})
    assert mapper.roles == {'__default__': whitelist('id', )}


def test_inherit_parent_roles():

    class RoleMixin(object):

        __roles__ = {
            'id_only': ['id', ]
        }

    class Parent(Mapper, RoleMixin):

        __type__ = TestType

        id = TestField()
        name = TestField()

        __roles__ = {
            'parent': ['name'],
            'overview': ['id', 'name']
        }

    class Child(Parent):

        __type__ = TestType

        __roles__ = {
            'overview': ['name', ]
        }

    mapper = Child(data={})
    assert mapper.roles == {
        '__default__': whitelist('id', 'name'),
        'overview': ['name', ],
        'parent': ['name', ],
        'id_only': ['id', ],
    }


def test_new_mapper_sets_roles():

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        name = TestField()

    class MyMapper(MapperBase):

        email = TestField()

        __roles__ = {
            'overview': ['email', ]
        }

    class OtherMapper(MyMapper):

        __roles__ = {
            'private': ['id', ]
        }

    mapper = MapperBase(data={})
    assert mapper.roles == {'__default__': whitelist('id', 'name')}

    mapper = MyMapper(data={})
    assert mapper.roles == {
        'overview': ['email', ],
        '__default__': whitelist('id', 'name', 'email')}

    mapper = OtherMapper(data={})
    assert mapper.roles == {
        '__default__': whitelist('id', 'name', 'email'),
        'overview': ['email'],
        'private': ['id', ]
    }


def test_mapper_sets_field_names():

    class MapperBase(Mapper):

        __type__ = TestType

        id = TestField()
        named = TestField(name='other_name')
        name = TestField(attribute_name='my_name')

    mapper = MapperBase(data={})
    assert mapper.fields['id'].opts.name == 'id'
    assert mapper.fields['name'].opts.name == 'my_name'
    assert mapper.fields['named'].opts.name == 'other_name'


def test_mapper_must_pass_obj_or_data():
    with pytest.raises(MapperError):
        Mapper()


def test_mapper_serialize():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    obj = TestType(id=2, name='bob')

    mapper = MapperBase(obj)
    result = mapper.serialize()

    assert result == {'id': 2, 'name': 'bob'}


def test_mapper_marshal():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'id': 2, 'name': 'bob'}

    mapper = MapperBase(data=data)
    result = mapper.marshal()

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'


def test_mapper_marshal_update():

    class MapperBase(Mapper):

        __type__ = TestType

        id = Integer()
        name = String()

    data = {'id': 2, 'name': 'bob'}
    obj = TestType(unrelated_attribute='test')

    mapper = MapperBase(obj=obj, data=data)
    result = mapper.marshal()

    assert isinstance(result, TestType)
    assert result.id == 2
    assert result.name == 'bob'
    assert result.unrelated_attribute == 'test'


def test_mapper_registered_in_class_registry():

    class MapperBase(Mapper):

        __type__ = TestType
        id = Integer()
        name = String()

    assert 'MapperBase' in _MapperConfig.MAPPER_REGISTRY


def test_mapper_already_registered():

    class MapperOne(Mapper):

        __type__ = TestType
        id = Integer()
        name = String()

    def create_mapper():
        class MapperOne(Mapper):

            __type__ = TestType
            id = Integer()
            name = String()

    with pytest.raises(MapperError):
        create_mapper()
