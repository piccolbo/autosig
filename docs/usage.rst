=====
Usage
=====

To use autosig in a project::

    from autosig import *

To define a signature::

    api_sig = Signature(x = param(default=0, converter=int))

To associate that signature with a function::

    @api_sig
    def entry_point(x=0)
        # signature executed here, in this case int conversion
        return x

The same works with methods, just leave the self argument out::

    class C:
        @api_sig
        def entry_point(self, x=0)
            # signature executed here, in this case int conversion
            return x

Simple signatures can be combined to for more complex ones::

    sig = Signature(x=param())+Signature(y=param())

Signatures can now include return values::

    api_sig = Signature(Retval(validator=int), x = param(default=0, converter=int))

You can skip signatures altogehter and just capture commonalities between arguments with the argumentless form of the decorator::

    x_arg = param(...)
    y_arg = param(...)

    @autosig
    def entry_point(x = x_arg, y = y_arg):
        return x + y


``param`` allows you to define a number of properties or behaviours of function arguments: validator, converter, docstring, default value, position; ``Retval``, which defines properties of return values, allows to specify only the first three.
