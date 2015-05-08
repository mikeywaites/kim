from kim.role import Role


def test_merge_roles():

    role = Role('name', 'id') | Role('name', 'email')
    assert 'name' in role
    assert 'id' in role
    assert 'email' in role
