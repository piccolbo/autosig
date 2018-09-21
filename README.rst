=======
Autosig
=======


.. image:: https://img.shields.io/pypi/v/autosig.svg
        :target: https://pypi.python.org/pypi/autosig

.. image:: https://img.shields.io/travis/piccolbo/autosig.svg
        :target: https://travis-ci.org/piccolbo/autosig

.. image:: https://codecov.io/gh/piccolbo/autosig/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/piccolbo/autosig

.. image:: https://readthedocs.org/projects/autosig/badge/?version=latest
        :target: https://autosig.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/piccolbo/autosig/shield.svg
     :target: https://pyup.io/repos/github/piccolbo/autosig/
     :alt: Updates


Autosig allows to create classes that describe signatures of functions and common processing of arguments. This allows to:

* Model functions that share the same signature with instances of class Signature
* Model the commonalities between different signatures, e.g. sharing the first few arguments
* Model common processing normally associated with signatures, such as default values, type checking, validation and conversion, this both at the level of individual arguments and globally for a signature (e.g, check the the first argument is a DataFrame vs. check the that first two arguments are both of the same type)

Since a signature is modeled with class, inheritance can be used to capture commonalities and differences between signatures::

 from autosig import *
 # define a class with Signature x and y are parameters with no special properties
 binary_op = Signature(
     x = param(),
     y = param())

 # define a parameter with an int annotation, converting to int if necessary)
 int_param = param(converter=int)

 # define another signature with two integer parameters, same annotation and
 # conversion behavior
 binary_int_op = Signature(
     x = int_param,
     y = int_param)


 # define a binary operator
 @autosig(binary_op)
 def add(x, y):
     return x + y

 # define a binary operator with int parameters
 @autosig(binary_int_op)
 def int_add(x, y):
     return x + y

 add(2, 3) # 5
 add(2, "3") # fails
 int_add(2, "3") # 5
