import pytest

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from kim.mapper import Mapper
from kim import field


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


def test_marshal_nested_mapper(db_session):

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
