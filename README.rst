.. Kim documentation master file, created by
   sphinx-quickstart on Fri May 15 15:12:15 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Kim: A JSON Serialization and Marshaling framework
=================================================

.. image:: https://img.shields.io/pypi/v/requests.svg
    :target: https://pypi.python.org/pypi/py-kim

.. image:: https://img.shields.io/pypi/l/requests.svg
    :target: https://pypi.python.org/pypi/py-kim

.. image:: https://circleci.com/gh/mikeywaites/kim.svg?style=shield&circle-token=d46954b5e66c2cc885f35c745baaea9a70e961af
    :target: https://pypi.python.org/pypi/py-kim


-------------------

**Introducing Kim**::

    >>> mapper = UserMapper(data=response.json())
    >>> mapper.marshal()
    User(id='one', name='Bruce Wayne', 'title'='CEO/Super Hero')
    >>> user_two = User.query.get('two')
    >>> mapper = UserMapper(obj=user_two)
    >>> mapper.serialize()
    {u'id': 'two', u'name': 'Martha Wayne', 'title': 'Mother of Batman'}

Kim Features
----------------

Kim is a feature packed framework for handling even the most complex
marshaling and serialization requirements.

- Web framework agnostic - Flask, Django, Framework-XXX supported!
- Highly customisable field processing system
- Security focused
- Control included fields with powerful roles system
- Handle mixed data types with polymorphic mappers
- Marshal and Serialize nested objects

Kim officially supports Python 2.7 & 3.3–3.5


Installation
--------------

Install Kim using pip::

    $ pip install py-kim


Documentation
--------------

Learn all of Kim's features with these simple step-by-step instructions or check out the
quickstart guide for a rapid overview to get going quickly.

.. _Kim User Guide: http://kim.readthedocs.org/latest
