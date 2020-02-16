import pytest

from kim.role import whitelist, blacklist, RoleError


def test_whitelist_membership():

    role = whitelist("name", "id")
    assert "name" in role
    assert "id" in role
    assert "email" not in role


def test_blacklist_membership():

    role = blacklist("name", "id")
    res = "name" in role
    assert res is False


def test_union_whitelist_roles():

    role = whitelist("name", "id") | whitelist("name", "email")
    assert "name" in role
    assert "id" in role
    assert "email" in role
    assert role.whitelist


def test_union_whitelist_and_blacklist():

    role = whitelist("name", "id") | blacklist("name", "email")
    assert "id" in role
    assert "name" not in role
    assert "email" not in role
    assert role.whitelist


def test_union_blacklist_and_whitelist():

    role = blacklist("name", "id") | whitelist("name", "email")
    assert "email" in role
    assert "name" not in role
    assert "id" not in role
    assert role.whitelist


def test_union_blacklist_and_blacklist():

    role = blacklist("name", "id") | blacklist("name", "email")
    # use fields here to test for membership as it's a blacklist so membership
    # is negated
    assert "name" in role.fields
    assert "id" in role.fields
    assert "email" in role.fields
    assert role.whitelist is False


def test_union_of_built_in_types_not_supported():

    with pytest.raises(RoleError):
        blacklist("name", "id") | set("name")
