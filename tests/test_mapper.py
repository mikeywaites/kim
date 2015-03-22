from kim.mapper import Mapper


def test_mapper_instantiation():
    """Simple test that instantiates a new ``Mapper`` object as a proof of
    concept for python 2.x and 3.x support.
    """
    mapper = Mapper()
    assert isinstance(mapper, Mapper)
