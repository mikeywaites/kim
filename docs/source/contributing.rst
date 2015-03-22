Contributing to Kim
========================


Development with docker
-----------------------

Kim provides a Docker container for running the test suite in both python 2.x and python 3.x.

Simply pull the kim docker containers from the docker registry by running the following::

    docker pull mikeywaites/kim:2
    docker pull mikeywaites/kim:3

Now we can run the tests in both python 2 and 3 by running the following commands::

    docker run --interactive --tty --rm --volume="$(pwd):/usr/src/app" mikeywaites/kim:3 python setup.py test
    docker run --interactive --tty --rm --volume="$(pwd):/usr/src/app" mikeywaites/kim:2 python setup.py test
