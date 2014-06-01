``Kim``
=============

A framework agnostic serialization and marshaling library written in python.


Contributing to ``kim``
------------------------
The ``kim`` source is shipped with a Vagrant distribution that will install python and create a virtualenv you can use for development.

Checkout the repository to your prefered location and then run ``vgarant up``.  Salt will be used to provision the new vm.  Once the provisioner
has run and the vm has booted run ``vagrant ssh``.  Change into the directory ``~/www/kim/``.  Before installing kim you should switch the the python
virtualenv by running ``workon kim``.  Now run ``pip install -e .[develop]``.  This will put kim
on your python path and install all the dev dependencies.

Once everything has been installed simply run ``py.test`` to run the tests and start hacking.

Documentation
-------------

comming soon.
