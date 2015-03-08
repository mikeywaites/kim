SQLAlchemy Quickstart
=====================

This document assumes you have already read the main Quickstart guide and only
deals with the differences applicable to use of `Kim` with `SQLAlchemy`.

For these examples, assume we have objects that look like this:

.. code-block:: python

	class User(Base):
		__tablename__ = 'users'

		id = Column(Integer, primary_key=True)
    name = Column(Integer, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

	class Post(Base):
		__tablename__ = 'posts'

		id = Column(Integer, primary_key=True)
		title = Column(String, nullable=False)
		content = Column(String, nullable=False)

		user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
		user = relationship("User", backref="posts")


Defining Serializers
====================

Serializers for SQLAlchemy objects should inherit from
`kim.contrib.sqa.SQASerializer`. Such objects must have a `__model__` property
pointing to the SQA model they represent.

With the exception of collections and nested, SQASerializers may be defined
identically to normal Serializers:

.. code-block:: python

    from kim.contrib.sqa import SQASerializer
    from kim.fields import Field
    import kim.types as t

    class UserSerializer(SQASerializer):
    	__model__ = User

    	id = Field(t.Integer, read_only=True)
      name = Field(t.String)

    >>> u = db.session.query(User).first()
    >>> UserSerializer().serialize(u)
    {'name': 'Bob Jones', 'id': 1}


Nested Serializers
==================

To include a foreign key as a nested serializer, it's normally nessasary to use
the *NestedForeignKey* type. This is identical to the *Nested* type, but
allows extra options when marshaling to set the foreign key on the resultant
object to the correct remote object.

This means we can take input data like this:

.. code-block:: python

    {'title': 'my post',
     'content': 'some content',
     'user': {'id': 2}
     }

Marshaling this data will result in a Post object with it's user relationship
set to the User with ID 2.

Let's define a PostSerializer with a nested UserSerializer:

.. code-block:: python

    from kim.contrib.sqa import NestedForeignKey

    class PostSerializer(SQASerializer):
      __model__ = Post

      id = Field(t.Integer, read_only=True)
      title = Field(t.String)
      content = Field(t.String)

      user = Field(
              NestedForeignKey(
                UserSerializer,
                getter=lambda id: db.session.query(User).get(id)
              )
            )

      data = {'title': 'my post',
              'content': 'some content',
              'user': {'id': 2}
              }

      >>> p = PostSerializer().marshal(data)
      <Post object>

      >>> p.user
      <User object ID 2>

The *getter* argument to NestedForeignKey is mandatory. It will be passed
an id and should return the corresponding object. If the object cannot be
found (or the user does not have the relevant permissions,) either return
None or raise NoResultFound. This will result in a MappingErrors being raised.

Usually you will need more information in a getter method than just the id.
This should be passed to the serializer's __init__ method, and the getter set
dynamically:


.. code-block:: python

    class PostSerializer(SQASerializer):
      __model__ = Post

      id = Field(t.Integer, read_only=True)
      title = Field(t.String)
      content = Field(t.String)

      user = Field(NestedForeignKey(UserSerializer))

      def __init__(self, *args, **kwargs):
        self.admins_only = kwargs.pop('admins_only')
        super(PostSerializer, self).__init__(*args, **kwargs)
        self.fields['user'].field_type.getter = self.user_getter

      def user_getter(self, id):
        if self.admins_only:
          return db.session.query(User) \
                           .filter(User.id == id, is_admin == True) \
                           .first()
        else:
          return db.session.query(User) \
                           .filter(User.id == id) \
                           .first()



Update Options for NestedForeignKey
===================================

There are four modes in which NestedForeignKey can be used, intended to cover
all use cases:

* Set by ID only - when passed data containing an ID the field
will look up the relevant object and assign it as the relationship. Any
keys other than 'id' will be ignored. *For security, this is the default.*

* allow_updates - when passed data containing an ID the field
will look up the relevant object and assign it as the relationship. Any
other keys will be updated on the object.

For example, this data:

.. code-block:: python

    {'user': {'id': 1, 'name': 'bob'}}

Would cause the user with ID 1 to be selected *and* the name field on that user
updated to 'bob'. For obvious reasons, use this option with caution.

* allow_updates_in_place - No ID key is required to be passed. Instead, any
other keys will be updated on the *existing* object assigned to the
relationship.

* allow_create - If an ID is not passed, a *new* object will be created with
the data contained. This option is incompatiable with allow_updates_in_place.

For example, this data:

.. code-block:: python

    {'user': {'name': 'fred'}}

Would cause a new user object with name 'fred' to be created, and the
relationship set to it.

To use any of these options, pass them to NestedForeignKey, eg:

.. code-block:: python

      user = Field(NestedForeignKey(UserSerializer, allow_updates=True))


Relationship Collections
========================

If you have a list based relationship, for example a one-to-many, use
`RelationshipCollection` in place of the usual `t.Collection`. This will
ensure that existing instances are updated correctly and newly created
instances are of the correct type.

`RelationshipCollection` should be used with an inner type of
`NestedForeignKey`, and supports all the update/create options outlined above
in the same way as scalar `NestedForeignKey`s.

.. code-block:: python

    from kim.contrib.sqa import RelationshipCollection

    class UserSerializer(SQASerializer):
      __model__ = User

      id = Field(t.Integer, read_only=True)
      name = Field(t.String)
      posts = Field(RelationshipCollection(NestedForeignKey(PostSerializer)))




