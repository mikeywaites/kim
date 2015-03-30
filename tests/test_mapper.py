import six

from collections import OrderedDict

from kim.mapper import Mapper
from kim.fields import Field


class TestField(Field):
    pass


def test_mapper_sets_declared_fields():
    """Ensure that on attributes inheriting from :class:`kim.fields.Field`
    are set in a mappers fields.
    """

    class MyTestMapper(Mapper):

        name = TestField()
        other = 'not a field'

    mapper = Mapper()
    mapper_with_fields = MyTestMapper()
    assert mapper.declared_fields == OrderedDict()
    assert 'name' in mapper_with_fields.declared_fields
    assert isinstance(mapper_with_fields.declared_fields['name'], TestField)
    assert 'other' not in mapper_with_fields.declared_fields


def test_mapper_inheritance():

    class OtherField(Field):
        pass

    class MapperBase(Mapper):

        id = TestField()
        name = TestField()

    class NewMapper(MapperBase):

        id = OtherField()
        additional_field = TestField()

    mapper = MapperBase()
    other_mapper = NewMapper()

    assert len(mapper.declared_fields.keys()) == 2
    assert 'id' in mapper.declared_fields
    assert 'name' in mapper.declared_fields

    assert len(other_mapper.declared_fields.keys()) == 3
    assert 'id' in other_mapper.declared_fields
    assert 'name' in other_mapper.declared_fields
    assert 'additional_field' in other_mapper.declared_fields

    assert isinstance(other_mapper.declared_fields['id'], OtherField)
