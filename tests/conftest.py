import pytest

from kim.mapper import _MapperConfig


@pytest.fixture(scope='function', autouse=True)
def empty_registry():

    _MapperConfig.MAPPER_REGISTRY.clear()
