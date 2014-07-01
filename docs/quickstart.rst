Quickstart
===================

Let's get started with Kim.

For these examples, assume we have objects that look like this:

.. code-block:: python

    class England(object):
        name = 'England'
        nickname = 'The Three Lions'

    class Gerrard(object):
        name = 'Steve Gerrard'
        goals_per_game = Decimal('0.24')
        date_of_birth = datetime(1980, 5, 30)
        team = England()

    gerrard = Gerrard()


In a real application these would most likely be ORM objects from your database,
but for the purposes of this example basic objects will suffice.


Defining Serializers
---------------------

Each object should have a corresponding *Serializer*. A serializer defines the
fields the output/input should consist of and their expected types.

.. code-block:: python

    from kim.serializers import Serializer
    from kim.fields import Field
    import kim.types as t

    class PlayerSerializer(Serializer):
        name = Field(t.String)

    >>> PlayerSerializer().serialize(gerrard)
    {'name': 'Steven Gerrard'}


Options on Fields
-----------------

*Fields* can take options which control where the data is found and how it is
treated.

Common options include:

* `required` - specify this field may not be omitted when marshaling
* `source` - where to find the data for this field on the object. If omitted,
  this defaults to the attribute name in the serializer
* `default` - a default value to use when marshaling if no data is given
* `read_only` - specify that this field should only be included when
  serializing, not marshaling

See the API reference for other options.

Let's use the source parameter to rename the `date_of_birth` attribute on our
object:

.. code-block:: python

    class PlayerSerializer(Serializer):
        name = Field(t.String)
        birthday = Field(t.DateTime, source='date_of_birth')

    >>> PlayerSerializer().serialize(gerrard)
    {'name': 'Steven Gerrard',
     'birthday': '1980-05-30T00:00:00Z'}


Types
-----

Many common *Types* are predefined in the `kim.types` module:

* `String`
* `Integer`
* `Boolean`
* `DateTime`
* `Date`
* `Float`
* `Decimal`

See the API reference for a full list.

Where needed, arguments can be passed to types by instantiating the Type
object. If arguments are not required, you do not have to instantiate the type.

Let's add `goals_per_game` as a Decimal type and specify the precision:

.. code-block:: python

    class PlayerSerializer(Serializer):
        name = Field(t.String)
        birthday = Field(t.DateTime, source='date_of_birth')
        goals_per_game = Field(t.Decimal(precision=2))

    >>> PlayerSerializer().serialize(gerrard)
    {'name': 'Steven Gerrard',
     'birthday': '1980-05-30T00:00:00Z',
     'goals_per_game': '0.24'}


Note that the Decimal type serializes to a string in order to avoid rounding
errors which may occur if a javascript float.


Serializing Many Objects at Once
--------------------------------

If you have a list of objects and would like to output a list of serialized
dictionaries, you can use the *many* option:

.. code-block:: python

    class PlayerSerializer(Serializer):
        name = Field(t.String)

    players = [Gerrard(), Gerrard(), Gerrard()]

    >>> PlayerSerializer().serialize(players, many=True)
    [{'name': 'Steven Gerrard'},
     {'name': 'Steven Gerrard'},
     {'name': 'Steven Gerrard'}]


Nested Types
------------

Nesting allows Serializers to be included as nested dictionaries inside other
Serializers. This is useful for modeling foreign key relationships.

The *Nested* type is used to nest a serializer, it takes the target Serializer
as it's first argument:

.. code-block:: python

    class TeamSerializer(Serializer):
        name = Field(t.String)
        nickname = Field(t.String)

    class PlayerSerializer(Serializer):
        name = Field(t.String)
        birthday = Field(t.DateTime, source='date_of_birth')
        goals_per_game = Field(t.Decimal(precision=2))
        team = Field(t.Nested(TeamSerializer))

    >>> PlayerSerializer().serialize(gerrard)
    {'name': 'Steven Gerrard',
     'birthday': '1980-05-30T00:00:00Z',
     'goals_per_game': '0.24',
     'team': {
        'name': 'England',
        'nickname': 'The Three Lions'
     }}



Roles
-----
As our serializer has become quite large, we'd like the option to limit the
fields returned in certain situations. This can be achieved with *Roles*.

Roles are specified as either a `whitelist` of fields to be included, or a
`blacklist` of fields to exclude.

Let's add a simple role to our serializer:

.. code-block:: python

    from kim.roles import whitelist

    class PlayerSerializer(Serializer):
        name = Field(t.String)
        birthday = Field(t.DateTime, source='date_of_birth')
        goals_per_game = Field(t.Decimal(precision=2))

        class Meta:
            roles = {'simple': whitelist('name', 'birthday')}

    >>> PlayerSerializer().serialize(gerrard, role='simple')
    {'name': 'Steven Gerrard',
     'birthday': '1980-05-30T00:00:00Z'}

    # If no role passed, all fields will be included as normal
    >>> PlayerSerializer().serialize(gerrard)
    {'name': 'Steven Gerrard',
     'birthday': '1980-05-30T00:00:00Z',
     'goals_per_game': '0.24'}


Roles may also be used in Nested Serializers, by passing `role` to the Nested
Type.


Marshaling
----------

So far we have only considered the output case - converting from Python
objects to dictionaries - which is refered to as serializing.

The reverse of this process - converting from dictionaries to Python - is
called *marshaling*. Other libraries refer to this process as deserializing.

This should be used when you want to parse JSON data from your clients,
most likely on POST and PUT requests to your API.

Marshaling is essentially serializing in reverse, with one key difference:
marshaling triggers *validation* to be run on the input. This checks that all
the fields are of the expected type, and may also run more advanced checks such
as assuring an email address is valid.

It is also possible to define your own custom validators on a per field or
per serializer basis.

Let's use our PlayerSerializer to marshal some data.

.. code-block:: python

    class PlayerSerializer(Serializer):
        name = Field(t.String, required=True)
        birthday = Field(t.DateTime, source='date_of_birth')
        goals_per_game = Field(t.Decimal(precision=2))

    post_data = {'name': 'Wayne Rooney', 'birthday': '1985-10-24T00:00:00Z'}

    >>> player = PlayerSerializer().marshal(post_data)
    {'name': 'Wayne Rooney',
     'date_of_birth': datetime(1980, 10, 24)}

Note that because the `source` of the birthday field is `date_of_birth`, the
result of marshaling puts the date in `date_of_birth`.

If you attempt to marshal invalid data or omit required fields, Kim will raise
a `MappingErrors`. You could catch this and return a 400.

.. code-block:: python

    post_data = {'birthday': 'this is not a date!'}

    >>> player = PlayerSerializer().marshal(post_data)
    MappingErrors: {'name': ['This is a required field'],
                    'birthday': ['Date must be in iso8601 format']}


Defining Custom Validators
--------------------------

If you wish to perform additional business logic level validation, you can do
this by defining a custom validator on your Serializer.

The API is very similar to `clean` methods on Django Forms. Defining a method
called `validate_<field name>` will result in it being called after the
Type level validation for that field is completed.

Validators must return `True` if no problems are found. Otherwise, they should
raise a ValidationError.

Let's restrict our birthday field to players with names beginning with the
letter F:

.. code-block:: python

    from kim.exceptions import ValidationError

    class PlayerSerializer(Serializer):
        name = Field(t.String, required=True)
        goals_per_game = Field(t.Decimal(precision=2))

        def validate_name(self, value):
            if value.startswith('L'):
                return True
            else:
                raise ValidationError('player name must begin with F')

    post_data = {'name': 'Wayne Rooney'}

    >>> player = PlayerSerializer().marshal(post_data)
    MappingErrors: {'name': ['player name must begin with F']}

    post_data = {'name': 'Frank Lampard'}

    >>> player = PlayerSerializer().marshal(post_data)
    {'name': 'Frank Lampard'}


If you want to validate across the entire data, for example to check fields
which are dependent on each other, define a method called `validate`, which
will be called once all the individual fields have successfully validated.

In this case, you should raise `MappingErrors` from validate, not
`ValidationError`.

Let's only allow players with long names if they've scored lots of goals:


.. code-block:: python

    from kim.exceptions import MappingErrors

    class PlayerSerializer(Serializer):
        name = Field(t.String, required=True)
        goals_per_game = Field(t.Decimal(precision=2))

        def validate(self, data):
            if len(data['name']) > 10 and data['goals_per_game'] < 2:
                raise MappingErrors({'goals_per_game': 'not enough goals scored for name length'})
            else:
                return True

    post_data = {'name': 'Wayne Rooney', 'goals_per_game': 1}

    >>> player = PlayerSerializer().marshal(post_data)
    MappingErrors: {'goals_per_game': 'not enough goals scored for name length'}

    post_data = {'name': 'Frank Lampard', 'goals_per_game': 5}

    >>> player = PlayerSerializer().marshal(post_data)
    {'name': 'Frank Lampard', 'goals_per_game': Decimal('5.00')}



What Next?
----------

If you are using Kim with SQLAlchemy, please read the SQL Alchemy Introduction
next.

You will also find the API Reference useful for more advanced topics.

If you want to extend Kim, or are interested in gaining a deeper understanding
of the architecture, see Internals.