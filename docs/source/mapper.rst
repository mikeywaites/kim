=======
Mapper
=======

Mappers are the building blocks of Kim - they define how JSON output
should look and how input JSON should be expected to look.

Mappers consist of Fields. Fields define the shape and nature of the data
both when being serialised(output) and marshaled(input).

Mappers must define a __type__. This is the type that will be
instantiated if a new object is marshaled through the mapper. __type__
maybe be any object that supports setter and getter functionality.


Declaring mappers
------------------

A new ``Mapper`` is defined by creating a subclass of the base ``Mapper`` provided by kim.  Fields are then added to a ``Mapper`` as class
attributes to define the shape of the data when using the ``Mapper``.

.. code-block:: python

    from kim import Mapper

    class UserMapper(Mapper):
        __type__ = User

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('myapp.mappers.CompanyMapper')


Mapper __type__
^^^^^^^^^^^^^^^^^

A ``Mapper`` must define a ``__type__`` property.  A python type that supports the getter and setter protocol maybe used.

.. code-block:: python

    from kim import Mapper

    class MyUser(object):

        def __init__(self, id=None, name=None, company=None):
            self.id = id
            self.name = name
            self.company = company

    class UserMapper(Mapper):
        __type__ = MyUser

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('myapp.mappers.CompanyMapper')


Mapper __roles__
^^^^^^^^^^^^^^^^^

A ``Mapper`` may also define a ``__roles__`` property.  Usage of roles is covered extensively in the :ref:`Roles section<roles>` of the documentation.

.. code-block:: python

    from kim import Mapper

    class UserMapper(Mapper):
        __type__ = MyUser

        id = field.Integer(read_only=True)
        name = field.String(required=True)
        company = field.Nested('CompanyMapper')

        __roles__ = {
            'public' whitelist('name'),
        }


Using Mappers
-----------------

Now we have seen how to define mappers, it's time to take a look out how Kim handles marshaling and serializing data.  A critical design feature of Kim's mappers is that each Mapper represents a single datum.
Whilst its possible to map many objects, which is demonstrated below, :py:class:`.Mapper` only handles one object at a time.

Marshaling data
^^^^^^^^^^^^^^^^^

Marshaling defines the process of pushing data into a mapper.  It valdiates the data is in the correct state before marshaling the input to the Mappers defined ``__type__`` object.

When marshaling, users pass data to the contructor of the :py:class:`.Mapper` using the ``data`` kwarg.  Once a mapper has been instantiated, users simply call the :meth:`kim.mapper.Mapper.marshal` method
to process the data.

.. code-block:: python

    data = json.loads(request.body)
    user = UserMapper(data=data).marshal()

    db.session.add(user)
    db.session.commit()


Marshaling many objects.
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    users = UserMapper.many().marshal(users_json)

    db.session.add_all(users)
    db.session.commit()



Serializing data
^^^^^^^^^^^^^^^^^

Serializing data is the opposite process from marshaling.  A mapper is provided with an object, typically a database orm object or other valid type, and kim serializes the object attributes into the defined data structure.

When serializing, users pass the object being serialized to the Mappers contructor using the ``obj`` kwarg.  Once the mapper has been instantiated, users simply call the :meth:`kim.mapper.Mapper.serialize` method to process the output.

.. code-block:: python

    user = get_user_by_id(1)
    return json.dumps(UserMapper(obj=user).serialize())


Serializing many objects.
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    users = get_user()
    return UserMapper.many().serialize(users)
