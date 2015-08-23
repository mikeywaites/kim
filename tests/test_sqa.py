import pytest

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from kim.mapper import Mapper
from kim import field
from kim.field import FieldInvalid


Base = declarative_base()
DBSession = sessionmaker()


class User(Base):

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)


class Post(Base):

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship(User)


@pytest.fixture(scope='session')
def connection(request):
    engine = create_engine('sqlite://')
    Base.metadata.create_all(engine)
    connection = engine.connect()

    DBSession.configure(bind=connection)
    Base.metadata.bind = engine
    request.addfinalizer(Base.metadata.drop_all)
    return connection


@pytest.fixture
def db_session(request, connection):
    trans = connection.begin()
    request.addfinalizer(trans.rollback)

    return DBSession()


def test_marshal_nested_mapper_allow_create(db_session):

    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested('UserMapper', required=True, allow_create=True)

    data = {
        'id': 2,
        'title': 'my post',
        'user': {
            'id': 1,
            'name': 'mike',
        }
    }
    mapper = PostMapper(data=data)
    obj = mapper.marshal()

    assert isinstance(obj, Post)
    assert obj.title == 'my post'
    assert isinstance(obj.user, User)


def test_marshal_nested_mapper_defaults(db_session):

    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    def getter(field, data):
        return db_session.query(User).get(data['id'])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested('UserMapper', required=True, getter=getter)

    data = {
        'id': 2,
        'title': 'my post',
        'user': {
            'id': 1,
            'name': 'should be ignored',
        }
    }
    user = User(id=1, name='mike')
    instance = Post(title='my post', user=user)

    db_session.add(instance)
    db_session.flush()

    mapper = PostMapper(data=data, obj=instance)
    obj = mapper.marshal()

    assert obj.user == user
    assert obj.user.name == 'mike'


def test_marshal_nested_mapper_defaults_not_found(db_session):

    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    def getter(field, data):
        return db_session.query(User).get(data['id'])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested('UserMapper', required=True, getter=getter)

    data = {
        'id': 2,
        'title': 'my post',
        'user': {
            'id': 1,
            'name': 'should be ignored',
        }
    }

    mapper = PostMapper(data=data)

    with pytest.raises(FieldInvalid):
        mapper.marshal()


def test_marshal_nested_mapper_allow_updates(db_session):

    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    def getter(field, data):
        return db_session.query(User).get(data['id'])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested('UserMapper', required=True, getter=getter,
                            allow_updates=True)

    data = {
        'id': 2,
        'title': 'my post',
        'user': {
            'id': 1,
            'name': 'new name',
        }
    }
    user = User(id=1, name='mike')
    instance = Post(title='my post', user=user)

    db_session.add(instance)
    db_session.flush()

    mapper = PostMapper(data=data, obj=instance)
    obj = mapper.marshal()

    assert obj.user == user
    assert obj.user.name == 'new name'


def test_marshal_nested_mapper_allow_updates_in_place(db_session):

    class UserMapper(Mapper):

        __type__ = User

        name = field.String()

    def getter(field, data):
        return db_session.query(User).get(data['id'])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested('UserMapper', required=True,
                            allow_updates_in_place=True)

    data = {
        'id': 2,
        'title': 'my post',
        'user': {
            'name': 'new name',
        }
    }
    user = User(id=1, name='mike')
    instance = Post(title='my post', user=user)

    db_session.add(instance)
    db_session.flush()

    mapper = PostMapper(data=data, obj=instance)
    obj = mapper.marshal()

    assert obj.user == user
    assert obj.user.name == 'new name'
