"""
Kim
--------------------------


Links
`````

* `Website
  <http://github.com/mikeywaites/kim/.

"""

from __future__ import print_function
from setuptools import setup

install_requires = [
    'SQLAlchemy',
    'iso8601',
]

setup(
    name='Kim',
    version='0.0.2',
    url='http://github.com/mikeywaites/kim/',
    license='Public Domain',
    author='Mike Waites, Jack Saunders',
    author_email='mikey.wait.es@gmail.com',
    description='A pyhton serialization library',
    long_description=__doc__,
    packages=['kim', 'kim.contrib'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=install_requires,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
