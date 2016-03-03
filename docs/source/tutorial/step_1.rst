.. _tutorial_start:

1 - Defining Mappers
==============================

Our rest API is going to expose a few simple operations for blogging application called blogger.  Defining :py:class:``kim.mapper.Mapper``  will feel fairly familiar for those who've worked with Django's ORM or SQLAlchemy's declarative_base ORM.
Each mapper is composed of multiple :py:class:``kim.field.Field`` objects which define the shape of the mapper.  They are responsible for handling the different types of data passed to your mappers and provide a pipeline which data is pushed into and out of
when serializing and marshaling requests.


.. code-block:: python

    from kim import Mapper
    from kim import field

    from ..models import User, Blog, Post


    class UserMapper(Mapper):

        __type__ = User

        id = field.String(read_only=True)
        name = field.String()
        email = field.String()


    class BlogMapper(Mapper):

        __type__ = Blog

        id = field.String(read_only=True)
        title = field.String()



Above we have defined two very simple Mappers to represent two of the objects our API will expose.
Both Mappers inherit from the base :py:class:``kim.mapper.Mapper`` object.  Each mapper defines some attributes mapper to :py:class:``kim.field.Field`` objects.  Each field represents a scalar type in python and will handle the relevant data when marshaling and serializing a mapper.



Mapper Types
-------------------

Each :py:class:``kim.mapper.Mapper`` must define a ``__type__`` attribute.  The ``__type__`` property may be any callable object that supports the ``getattr`` and ``setattr`` interfaces.


In the above exaple our mappers are mapping to SQLAlchemy models but this could just as eaily by a dict or custom object.

.. code-block:: python

    from kim import Mapper
    from kim import field

    from ..models import User, Blog, Post


    class UserDictMapper(Mapper):

        __type__ = dict

        id = field.String(read_only=True)
        name = field.String()
        email = field.String()
