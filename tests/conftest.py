import pytest

from kim.mapper import _MapperConfig, Mapper


@pytest.fixture(scope='function', autouse=True)
def empty_registry():

    _MapperConfig.MAPPER_REGISTRY.clear()


def marshal_mapper_session(data, output):

    mapper = Mapper(data=data)
    return mapper.get_mapper_session(data, output)


def serialize_mapper_session(obj, output):

    mapper = Mapper(obj=obj)
    return mapper.get_mapper_session(obj, output)
