.. _benchmarks:

Benchmarks
==========

Below is the output of a benchmark written and maintained by @voidfiles.  You can find the results
here https://voidfiles.github.io/python-serialization-benchmark/

Here's the output from the test suite using a Python 3 Docker container
on a 2015 Mac Book pro with 8gb of ram.

=====================  ========================  ======================  ==========
Library                  Many Objects (seconds)    One Object (seconds)    Relative
=====================  ========================  ======================  ==========
Custom                                0.0110412              0.00528884     1
lima                                  0.01336                0.0066793      1.22715
serpy                                 0.0427153              0.0221367      3.97134
Strainer                              0.0533044              0.0241542      4.74333
Lollipop                              0.39349                0.188841      35.6602
Marshmallow                           0.561764               0.299909      52.7663
kim                                   0.855853               0.357965      74.3306
Django REST Framework                 1.11779                0.844406     120.159
=====================  ========================  ======================  ==========
