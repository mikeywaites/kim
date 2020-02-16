from kim.utils import attr_or_key


def test_attr_or_key_util():
    class Foo(object):

        bar = "baz"

    foo_dict = {"bar": "baz"}
    invalid = "str"

    assert attr_or_key(Foo(), "bar") == "baz"
    assert attr_or_key(Foo(), "qux") is None
    assert attr_or_key(foo_dict, "bar") == "baz"
    assert attr_or_key(foo_dict, "qux") is None
    assert attr_or_key(invalid, "bar") is None


def test_attr_or_key_util_dot_syntax():
    class Bar(object):
        xyz = "abc"

    class Foo(object):

        bar = Bar()

    foo_dict = {"bar": {"xyz": "abc"}}

    assert attr_or_key(Foo(), "bar.xyz") == "abc"
    assert attr_or_key(Foo(), "bar.qux") is None
    assert attr_or_key(foo_dict, "bar.xyz") == "abc"
    assert attr_or_key(foo_dict, "bar.qux") is None


def test_attr_or_key_util_dot_syntax_escape():

    foo_dict = {"bar.xyz": "abc"}

    assert attr_or_key(foo_dict, "bar\\.xyz") == "abc"
