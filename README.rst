=======
Autosig
=======

**Experimental**

Autosig allows to create classes that describe signatures of functions and common processing of arguments. This allows to:

* Model functions that share the same signature
* Model the commonalities between different signatures, e.g. sharing the first few arguments
* Model common processing normally associated with signatures, such as default values, type checking, validation and conversion, this both at the level of individual arguments and globally for a signature (e.g, check the the first argument is a DataFrame vs. check the that first two arguments are both of the same type)

Since a signature is modeled with class, inheritance can be used to capture commonalities and differences between signatures::

 from autosig import *
 # define a class with @signature decorator inheriting from a subclass of
 # Signature (I know, a little redundant in this case)
 # x and y are parameters with no special properties
 @signature
 class BinaryOp(Signature):
     x = param()
     y = param()

 # define a parameter with an int annotation, converting to int if necessary)
 int_param = param(converter=int, type=int)

 # define another signature with two integer parameters, same annotation and
 # conversion behavior
 @signature
 class BinaryIntOp(BinaryOp):
     x = int_param
     y = int_param


 # define a binary operator
 @autosig(sig=BinaryOp)
 def add(x, y):
     return x + y

 # define a binary operator with int parameters
 @autosig(sig=BinaryIntOp)
 def int_add(x, y):
     return x + y

 add(2, 3) # 5
 add(2, "3") # fails
 int_add(2, "3") # 5
