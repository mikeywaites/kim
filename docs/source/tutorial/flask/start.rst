======================
Kim tutorial - Flask
======================

This Kim tutorial series is going to take you through creating a fully featured, working rest api using flask which will aim to demonstrate all the features Kim has to offer.
The following tutorial assumes the following:

* You have an understanding of python
* You have some working knowledge of flask
* You have some experience with SQL(postgres) and SqlAlchemy



Setting up the project.
----------------------------

Fristly check out the ``kim-flask-example`` repo `<https://github.com/mikeywaites/kim-flask-example>`.
The repo contains a Flask application factory and boilerplate for connecting to the database using SqlAlchemy.

Open the ``fooder/models/food.py`` file in the example project.  As you can see this file contains
a collection of models representing our database schema.   We are going to create some Restful endpoints to expose our database data to our users
and also allow them to create new data using Kim.


Our first api
^^^^^^^^^^^^^^^^^^^^^^

Take a look at The file ``fooder/api/views.py`` There is a fairly contrived example of an apo endpoint that returns all the data for all the vegetables stored in our database.

.. code-block:: python

    # fooder/api/views.py
    # Copyright (C) 2014-2015 the Kim authors and contributors
    # <see AUTHORS file>
    #
    # This module is part of Kim and is released under
    # the MIT License: http://www.opensource.org/licenses/mit-license.php

    from flask import Blueprint, jsonify

    from fooder.models.food import get_vegetables

    api_mod = Blueprint('api', __name__)


    @api_mod.route('/')
    def home():

        return jsonify({'foo': 'bar'}), 200


    @api_mod.route('/vegetables')
    def vegetables():

        objs = get_vegetables()
        data = {'objects': [{'id': v.id,
                             'name': v.name,
                             'description': v.description,
                             'category': v.category} for v in objs]}
        return jsonify(data), 200


As you can see this is fine for a quick and dirty example but it would very quickly throw up problems with maintainabilty and flexibility in more complex scenarios.

At a very basic level, this is the problem that Kim aims to solve.  A way to represent the structure of json data into and out from your database.

For example, what if under different circumstances we needed to change what fields were returned in each vegetable object?  Lets see a version of the same api using Kim to map the vegetable object

.. code-block:: python

    # fooder/api/views.py
    # Copyright (C) 2014-2015 the Kim authors and contributors
    # <see AUTHORS file>
    #
    # This module is part of Kim and is released under
    # the MIT License: http://www.opensource.org/licenses/mit-license.php

    from flask import Blueprint, jsonify

    from kim import Mapper

    from fooder.models.food import Vegetable, get_vegetables

    api_mod = Blueprint('api', __name__)


    @api_mod.route('/')
    def home():

        return jsonify({'foo': 'bar'}), 200


    class VegetableMapper(Mapper):

        __type__ = Vegetable

        id = Field(String, read_only=True)
        name = Field(String, required=True)
        description = Field(String, required=True)
        category = Field(String, required=True)
        type = Field(String, read_only=True)

        __roles__ = {
            'overview': whitelist('id', 'overview', 'description')
        }


    @api_mod.route('/vegetables')
    def vegetables():

        objs = get_vegetables()
        veg_mapper = VegetableMapper()
        resp = jsonify(veg_mapper.serialize(objs, many=True, role='overview'))
        return resp, 200
