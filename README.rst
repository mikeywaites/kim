``Kim``
=============

Kim is a framework agnostic serialization and marshaling (de-serilization)
library for python web applications.

It helps you transform data from your ORM objects into JSON serializable dicts
to output from your REST API.

In the other direction, you can use the exact same serializer definition to
transform JSON POST data from your clients back into ORM objects to save in
your database.

Kim can work with basic Python objects and dicts, and has an adapter for
seamless intergration with SQLAlchemy. Django integration is coming soon.

Example
-------
.. code-block:: python

	class Person(db.Model):
		name = Column(String)
		age = Column(Integer)


	class MySerializer(SQASerializer):
		name = Field(String)
		current_age = Field(Integer, source='age')


	person1 = db.session.query(Person).first()

	>>> MySerializer().serialize(person)
	{'name': 'jack', 'current_age': 24}

	person2 = MySerializer().marshal({'name': 'mike', 'current_age': 28})

	>>> person2.name
	'mike'

	>>> person2.age
	28


Features
--------
* Serialization (output) and marshaling (input)
* Automatic validation and sanitization of input when marshaling.
* Declarative Serializer definition syntax
* Flexible Types API - many common types built in or easily define your own
* Support for roles - whitelist/blacklist fields for different use cases
* Nested serializers including support for nested roles
* Support for Collections, including Collections of Nested enabling a wide range
  of DB relationships to be directly mapped
* Designed for extensibility - Serializers are syntactic sugar on top of an
  easy to understand low level API


Installation
------------
.. code-block:: shell

	pip install kim


.. Contributing to ``kim``
.. ------------------------
.. The ``kim`` source is shipped with a Vagrant distribution that will install python and create a virtualenv you can use for development.

.. Checkout the repository to your prefered location and then run ``vgarant up``.  Salt will be used to provision the new vm.  Once the provisioner
.. has run and the vm has booted run ``vagrant ssh``.  Change into the directory ``~/www/kim/``.  Before installing kim you should switch the the python
.. virtualenv by running ``workon kim``.  Now run ``pip install -e .[develop]``.  This will put kim
.. on your python path and install all the dev dependencies.

.. Once everything has been installed simply run ``py.test`` to run the tests and start hacking.

