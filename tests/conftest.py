import pytest

from kim.mapper import _MapperConfig, Mapper


@pytest.fixture(scope="function", autouse=True)
def empty_registry():

    _MapperConfig.MAPPER_REGISTRY.clear()


def get_mapper_session(data=None, obj=None, output=None):

    mapper = Mapper(data=data, obj=obj)
    return mapper.get_mapper_session(data or obj, output)
