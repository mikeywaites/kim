import pytest

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from kim.mapper import Mapper, MappingInvalid
from kim import field


Base = declarative_base()
DBSession = sessionmaker()


@pytest.fixture
def mappers(request):
    class __Mappers(object):
        pass

    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested("UserMapper", required=True, allow_create=True)

    mappers = __Mappers()
    mappers.UserMapper = UserMapper
    mappers.PostMapper = PostMapper
    return mappers


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    @hybrid_property
    def anonymous(self):
        return False


class PostReader(Base):

    __tablename__ = "post_reader"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)


class Post(Base):

    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship(User, backref=backref("posts", lazy="dynamic"))
    readers = relationship(User, secondary=PostReader.__table__, lazy="dynamic")


@pytest.fixture(scope="session")
def connection(request):
    engine = create_engine("sqlite://")
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


def test_partial_updates(db_session):
    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested("UserMapper", required=True, allow_create=True)
        readers = field.Collection(field.Nested("UserMapper"), required=False)

    data = {"title": "new"}
    user = User(id="id", name="mike")
    post = Post(title="test post", user=user)
    mapper = PostMapper(data=data, obj=post, partial=True)
    obj = mapper.marshal()
    assert obj.title == "new"


def test_marshal_nested_mapper_allow_create(db_session, mappers):

    data = {"id": 2, "title": "my post", "user": {"id": 1, "name": "mike",}}
    mapper = mappers.PostMapper(data=data)
    obj = mapper.marshal()

    assert isinstance(obj, Post)
    assert obj.title == "my post"
    assert isinstance(obj.user, User)


def test_marshal_nested_mapper(db_session, mappers):

    data = {"id": 2, "title": "my post", "user": {"id": 1, "name": "mike",}}
    mapper = mappers.PostMapper(data=data)
    obj = mapper.marshal()

    assert isinstance(obj, Post)
    assert obj.title == "my post"
    assert isinstance(obj.user, User)


def test_serializer_nested_mapper(db_session, mappers):

    data = {"id": 2, "title": "my post", "user": {"id": 1, "name": "mike",}}
    mapper = mappers.PostMapper(data=data)
    obj = mapper.marshal()

    assert isinstance(obj, Post)
    assert obj.title == "my post"
    assert isinstance(obj.user, User)


def test_marshal_nested_mapper_defaults(db_session):
    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    def getter(session):
        return db_session.query(User).get(session.data["id"])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested("UserMapper", required=True, getter=getter)

    data = {
        "id": 2,
        "title": "my post",
        "user": {"id": 1, "name": "should be ignored",},
    }
    user = User(id=1, name="mike")
    instance = Post(title="my post", user=user)

    db_session.add(instance)
    db_session.flush()

    mapper = PostMapper(data=data, obj=instance)
    obj = mapper.marshal()

    assert obj.user == user
    assert obj.user.name == "mike"


def test_marshal_nested_mapper_defaults_not_found(db_session):
    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    def getter(session):
        return db_session.query(User).get(session.data["id"])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested("UserMapper", required=True, getter=getter)

    data = {
        "id": 2,
        "title": "my post",
        "user": {"id": 1, "name": "should be ignored",},
    }

    mapper = PostMapper(data=data)

    with pytest.raises(MappingInvalid):
        mapper.marshal()

    assert mapper.errors == {"user": "user not found"}


def test_marshal_nested_mapper_allow_updates(db_session):
    class UserMapper(Mapper):

        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String()

    def getter(session):
        return db_session.query(User).get(session.data["id"])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested(
            "UserMapper", required=True, getter=getter, allow_updates=True
        )

    data = {"id": 2, "title": "my post", "user": {"id": 1, "name": "new name",}}
    user = User(id=1, name="mike")
    instance = Post(title="my post", user=user)

    db_session.add(instance)
    db_session.flush()

    mapper = PostMapper(data=data, obj=instance)
    obj = mapper.marshal()

    assert obj.user == user
    assert obj.user.name == "new name"


def test_marshal_nested_mapper_allow_updates_in_place(db_session):
    class UserMapper(Mapper):

        __type__ = User

        name = field.String()

    def getter(session):
        return db_session.query(User).get(session.data["id"])

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested("UserMapper", required=True, allow_updates_in_place=True)

    data = {"id": 2, "title": "my post", "user": {"name": "new name",}}
    user = User(id=1, name="mike")
    instance = Post(title="my post", user=user)

    db_session.add(instance)
    db_session.flush()

    mapper = PostMapper(data=data, obj=instance)
    obj = mapper.marshal()

    assert obj.user == user
    assert obj.user.name == "new name"


def test_marshal_collection_appender_query(db_session):
    class UserMapper(Mapper):

        __type__ = User

        name = field.String()

    def foo_getter(session):
        return session.data

    class PostMapper(Mapper):

        __type__ = Post

        title = field.String()
        user = field.Nested("UserMapper", required=False, allow_updates_in_place=True)
        readers = field.Collection(
            field.Nested("PostMapper", getter=foo_getter), required=False
        )

    user1 = User(id=1, name="mike")
    user2 = User(id=2, name="jack")
    instance = Post(title="my post", user=user1, readers=[user1])

    db_session.add(user1)
    db_session.add(user2)
    db_session.add(instance)
    db_session.flush()
    data = {
        "title": "new title",
    }

    mapper = PostMapper(data=data, obj=instance, partial=True)
    obj = mapper.marshal()
    assert obj.title == "new title"
