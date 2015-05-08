from kim.role import Role, whitelist, blacklist


def test_whitelist_membership():

    role = whitelist('name', 'id')
    import ipdb; ipdb.set_trace()
    assert 'name' in role
    assert 'id' in role
    assert 'email' not in role


def test_blacklist_membership():

    role = blacklist('name', 'id')
    res = 'name' in role
    assert res is False


def test_merge_roles():

    role = Role('name', 'id') | Role('name', 'email')
    assert 'name' in role
    assert 'id' in role
    assert 'email' in role
