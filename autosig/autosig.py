"""Implementation of autosig."""
from attr import (
    attrib,
    asdict,
    NOTHING,
    fields_dict,
    make_class,
)
from collections import OrderedDict
from functools import wraps
from inspect import getsource, signature
from itertools import chain
from toolz.functoolz import curry
from types import BuiltinFunctionType

__all__ = ["Signature", "autosig", "check", "param"]

AUTOSIG_DOCSTRING = "__autosig_docstring__"
AUTOSIG_POSITION = "__autosig_position__"


def param(
        default=NOTHING,
        validator=None,
        converter=None,
        docstring="",
        position=-1,
        kw_only=False,
):
    """Define parameters in a signature class.

    Parameters
    ----------
    default : Any
        The default value for the parameter (defaults to no default, that is, mandatory).
    validator : callable or list thereof
        A validator for the actual parameter. If list, all element of the list are called. Return value is ignored, only exceptions raised count.
    converter : callable
        The callable is executed with the parameter as an argument and its value assigned to the parameter itself. Useful for type conversions, but not only (e.g. limit range of parameter).
    docstring : string
        Description of parameter `docstring` (the default is "").
    position : int
        Desired position of the param in the signature. Negative values start from the end.
    kw_only : bool
        Whether to make this parameter keyword-only.


    Notes
    -----
    Type annotations will be enforced. This is a thin layer over attrs's attrib().

    Returns
    -------
    attr.Attribute
        Object describing all the properties of the parameter. Can be reused in multiple signature definitions to enforce consistency.

    """
    metadata = {AUTOSIG_DOCSTRING: docstring, AUTOSIG_POSITION: position}
    kwargs = locals()
    for key in ("docstring", "position"):
        del kwargs[key]
    return attrib(**kwargs)


@curry
def keyfun(x, l):
    pos = x[1].metadata[AUTOSIG_POSITION]
    return pos if pos >= 0 else l + pos


class Signature:
    """Class to represent signatures.

    Parameters
    ----------
    \*params : (str, attr.Attribute)
        Each argument is a pair with the name of an argument in the signature and a desription of it generated with a call to param.
    \*\*kwparams : attr.Attribute
        Each keyword argument becomes an argument named after the key in the signature of a function and must be initialized with a param call. Requires python >=3.6. If both *param and **params are provided the first will be concatenated with items of the second, in this order.

    Returns
    -------
    Signature
        The object created.

    """

    def __init__(self, *params, **kwparams):
        """See class docs."""
        self.params = OrderedDict(
            sorted(
                chain(iter(params), kwparams.items()),
                key=keyfun(l=len(params))))

    def __add__(self, other):
        """Combine signatures.

        The resulting signature has the union of the arguments of the left and right operands. The order is determined by the position property of the parameters and when there's a tie, positions are stably sorted with the left operand coming before the right one. One a name clash occurs, the right operand, quite arbitraly, wins. Please do not rely on this behavior, it may change.
        """

        return Signature(*(chain(self.params.items(), other.params.items())))


# class SigBase:
#     def __init__(self):
#         self.validations = []
#         self.defaults = {}
#
#     def validate(self):
#         for val in self.validations:
#             val(self)
#
#     def default(self):
#         for k, v in self.defaults.items():
#             setattr(self, k, v(self))
#
#     def __attrs_post_init__(self):
#         self.default()
#         self.validate()


def make_sig_class(sig):
    return make_class(
        "Sig",
        attrs=sig.params,
        # bases=(SigBase, ),
        cmp=False,
    )


def autosig(sig):
    """Decorate  functions to attach signatures.

    Parameters
    ----------
    sig : Signature
        A class with one member per parameter, initialized with a call to param

    Returns
    -------
    function
        The decorated function, will intialize, convert, and
        validate its arguments.

    """

    Sig = make_sig_class(sig)

    def decorator(f):
        f_params = signature(f).parameters
        Sig_params = signature(Sig).parameters
        assert f_params == Sig_params, "\n".join([
            "Mismatched signatures:",
            str(f),
            str(f_params),
            str(Sig),
            str(Sig_params)
        ])  # compared as OrderedDicts, retval ignored TODO: support retval?

        @wraps(f)
        def wrapped(*args, **kwargs):
            params = Sig(**signature(f).bind(*args, **kwargs).arguments)
            return f(**asdict(params))

        wrapped.__doc__ = (wrapped.__doc__ or """Short summary.


            Returns
            -------
            type
                Description of returned object.

            """)
        wrapped.__doc__ += "\n\nParameters\n---------\n" + "\n".join([
            k + ": " + v.metadata[AUTOSIG_DOCSTRING]
            for k, v in fields_dict(Sig).items()
        ])

        return wrapped

    return decorator


def check(type_or_predicate):
    """Transform a type or predicate into a autosig-friendly validator.

    Parameters
    ----------
    type_or_predicate : type or callable
        A type or a single argument function returning a bool, indicating whether the check was passed. The function will be passed an argument value when check(function) is used as validator argument to param.

    Returns
    -------
    Callable
        A Callable to be used as validator argument to param.

    """
    predicate, msg = (
        (
            lambda x: isinstance(x, type_or_predicate),
            "type of {name} = {x} should be {type_or_predicate}, {type_x} found instead",
        )
        if isinstance(type_or_predicate, type)
        else (
            type_or_predicate,
            (
                "{name} called with argument x".format(name=type_or_predicate.__qualname__)
                if isinstance(type_or_predicate, BuiltinFunctionType)
                else getsource(type_or_predicate)
            )
            + " where x=={x}"))  # yapf: disable

    def f(_, attribute, x):
        assert predicate(x), msg.format(
            name=attribute.name,
            x=x,
            type_x=type(x),
            type_or_predicate=type_or_predicate,
        )

    return f
