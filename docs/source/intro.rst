Introducing Kim
=================

Kim is a framework for orchestrating the structure and flow of data into and out of your REST API.

There are two key concepts in kim. Marshaling data and Serializing data.  Both these operations are contolled by user defined ``Mappers``.  The shape of your mappers is defined by the useage of ``Field`` objects which
are capabable of dealing with certain types of data into and out from your mappers.

Some of the key features Kim has to offer are:

* An extensible api offering developers lots of flexibility to model complex data structures.
* Separate flows for marshaling and serialing data enabling users to provide tailored data handling for creating object versus fetching them.
* powerful roles system to allow users to dynamically change the shape of their data
* System for handling complex, nested data structures with advanced options for validation throughout.
* First class supoort for handling partial objects
* Large list of built in Field types with support for custom user defined types to be added with ease.


Walkthrough
-------------------------

The following tutorial will take users through an in depth look at all of Kim's features.   The tutorial is accompanied by an example flask application that implements a simple rest api for a blog app.  The tutorial
assume that the user has some working knowledge of python and the concepts behind REST.


You can find the tutorial application http://github.com/mikeywaites/kim-flask-example


:ref:`Kim Tutorial <tutorial_start>`


Why another serialization framework?
-------------------------------------

TODO


A Minimal Application
---------------------

A minimal application, using flask, looks something like this

.. code-block:: python

    from flask import Flask, request, abort, jsonify

    from sqlalchemy import orm
    from flask_sqlalchemy import SQLAlchemy

    from kim import Mapper, field
    from kim.role import whitelist
    from kim.exception import MappingInvalid

    app = Flask(__name__)

    db = SQLAlchemy(app)


    class User(db.Model):
        __tablename__ = 'users'

        id = db.Column(db.String(22), primary_key=True)
        name = db.Column(db.String(300), nullable=False)
        email = db.Column(db.String(300), unique=True, nullable=False)


    class Blog(db.Model):
        __tablename__ = 'blog'

        id = db.Column(db.String(22), primary_key=True)
        title = db.Column(db.String(300), nullable=False)
        user_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False)
        user = orm.relationship('User', backref=orm.backref('blogs'))


    class PostReaders(db.Model):

        __tablename__ = 'post_readers'

        user_id = db.Column(
            db.String(22), db.ForeignKey('users.id'),
            nullable=False, primary_key=True)

        post_id = db.Column(
            db.String(22), db.ForeignKey('post.id'),
            nullable=False, primary_key=True)


    class Post(db.Model):

        __tablename__ = 'post'

        id = db.Column(db.String(22), primary_key=True)
        title = db.Column(db.String(300), nullable=False)
        content = db.Column(db.Text, nullable=False)

        user_id = db.Column(db.String(22), db.ForeignKey('users.id'), nullable=False)
        blog_id = db.Column(db.String(22), db.ForeignKey('blog.id'), nullable=False)

        blog = orm.relationship('Blog', backref=orm.backref('posts'))
        user = orm.relationship('User', backref=orm.backref('posts'))

        readers = orm.relationship("User", secondary=PostReaders.__table__)


    class UserMapper(Mapper):

        __type__ = User

        id = field.String(read_only=True)
        email = field.String()
        name = field.String()


    class BlogMapper(Mapper):

        __type__ = Blog

        id = field.String(read_only=True)
        title = field.String()
        user = field.Nested('UserMapper', role='overview')

        __roles__ = {
            'basic': whitelist('id', 'title')
        }


    @app.route('/', methods=['GET'])
    def blog_index_api():
        """return a list of BLOG objects as JSON for GET requests or create
        a new blog object and save it to the database for POST requests

        """

        if request.method == "POST":
            try:
                blog = BlogMapper(data=request.get_json()).marshal()
            except MappingInvalid:
                abort(400)

            db.session.add(blog)
            db.session.commit()

            data = BlogMapper(obj=blog).serialize(blogs)
            return jsonify(data)

        else:

            blogs = Blog.query.all()
            data = BlogMapper.many().serialize(blogs)

            json_data = jsonify({'objects': data})
            return json_data


    if __name__ == '__main__':

        app.run()
