from kim.utils import attr_or_key


def test_attr_or_key_util():

    class Foo(object):

        bar = 'baz'

    foo_dict = {'bar': 'baz'}
    invalid = 'str'

    assert attr_or_key(Foo(), 'bar') == 'baz'
    assert attr_or_key(Foo(), 'qux') is None
    assert attr_or_key(foo_dict, 'bar') == 'baz'
    assert attr_or_key(foo_dict, 'qux') is None
    assert attr_or_key(invalid, 'bar') is None
