Advanced Topics
===============

Different Field Definitions for Serializing and Marshaling
==========================================================

Occasionally, you may want to use a different field definition for the same
key depending on whether you're serializing or marshaling.

For example, when serializing you may want to expose the `posts` attribute
on your model directly, but when marshaling you want to buffer it into a
temporary attribute called `_posts` so you can perform more processing on it
in your view. In other words, you require the `source` attribute to be
different in each case.

Field key names are normally implied by the attribute name they are assigned
to, but this may be overridden with the `name` attribute. Combine this with
seperate roles for serializing and marshaling to solve the problem:

.. code-block:: python

    class UserSerializer(Serializer):
      posts_serialize = t.Collection(Nested(PostSerializer), name='posts', source='posts')
      posts_marshal = t.Collection(Nested(PostSerializer), name='posts', source='_posts')

      class Meta:
        roles = {'serialize': blacklist('posts_marshal'),
                 'marshal': blacklist('posts_serialize')}

    >> UserSerializer().serialize({'posts': [..]}, role='serialize')
    {'posts': [..] }
    >> UserSerializer().marshal({'posts': [..]}, role='marshal')
    {'_posts': [..]}


Use of NestedForeignKey without a SQLAlchemy relationship
=========================================================

If you're using an `association_proxy` or an `@property` instead of a true
SQLAlchemy `relationship` on your model class, Kim will not be able to infer
the type of the object.

To resolve this, pass `remote_class` to the `NestedForeignKey`:

.. code-block:: python

    user = Field(NestedForeignKey(UserSerializer, remote_class=User))

Custom Types
============

Improve Performance with Raw Mode
=================================

When retrieving many objects with SQLAlchemy, or making very complex queries,
it can be much faster to request specific columns directly rather than going
through the ORM.

This results in results coming back as a `KeyedTuple` instead of a normal
SQLAlchemy object, which would not normally be compatiable with
`NestedForeignKey`.

To support this, you can pass `raw=True` to `serialize()` in conjunction with
a naming convention for nested fields. Use SQLAchemy to label fields for
nested objects by seperating with `__`.

For example, if you have a nested user with a name field, you would use the
label `user__name`. If the user has a nested group with an id, this would
be referred to as `user__group__id` and so on.

<example>

Dot Notation
============


__self__

annoyances:
the role thing
the getter thing
