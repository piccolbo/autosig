"""Implementation of autosig."""
from attr import attrib, asdict, NOTHING, fields_dict, make_class
from collections import OrderedDict
from functools import wraps
from inspect import getsource, signature
from itertools import chain
import re
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
        all_params = list(chain(iter(params), kwparams.items()))
        self.params = OrderedDict(sorted(all_params, key=keyfun(l=len(all_params))))

    def __add__(self, other):
        """Combine signatures.

        The resulting signature has the union of the arguments of the left and right operands. The order is determined by the position property of the parameters and when there's a tie, positions are stably sorted with the left operand coming before the right one. Once a name clash occurs, the right operand, quite arbitrarily, wins. Please do not rely on this behavior, it may change.
        """

        return Signature(*(chain(self.params.items(), other.params.items())))


def make_sig_class(sig):
    return make_class(
        "Sig_" + str(abs(hash(sig))),
        attrs=sig.params,
        # bases=(SigBase, ),
        cmp=False,
    )


def autosig(sig_or_f):
    """Decorate  functions or methods to attach signatures.

        Use with (W) or without (WO) an argument:
        @autosig(Signature(a = param(), b=param()))
        def fun(a, b)

        or, equivlently,

        @autosig
        def fun(a=param(), b=param())

        Do not include the self argument in the signature when decorating
        methods



    Parameters
    ----------
    sig : Signature of function
        An instance of class Signature (W) or a function or method (WO) whose
        arguments are intialized with a call to param.

    Returns
    -------
    function
        A decorator (W) or an already decorated function (WO)
        The decorated function, will intialize, convert, and
        validate its arguments and will include argument docstrings
        in its docstring.

    """
    argument_deco = isinstance(sig_or_f, Signature)
    Sig = make_sig_class(
        (
            sig_or_f
            if argument_deco
            else Signature(
                *[(k, v.default) for k, v in signature(sig_or_f).parameters.items()]
            )
        )
    )

    def decorator(f):
        # if decorator used on instance method, f is still a func here
        # hence I special case self arg in the following
        # will break if regular func has self arg TODO: fix
        if argument_deco:
            f_params = dict(signature(f).parameters)
            f_params.pop("self", None)
            Sig_params = signature(Sig).parameters
            assert f_params == Sig_params, "\n".join(
                [
                    "Mismatched signatures:",
                    str(f),
                    str(f_params),
                    str(Sig),
                    str(Sig_params),
                ]
            )  # compared as OrderedDicts, retval ignored TODO: support retval?

        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                bound_args = signature(f).bind(*args, **kwargs).arguments
                args_wo_self = bound_args.copy()
                args_wo_self.pop("self", None)
                params = Sig(**args_wo_self)
            except TypeError as te:
                raise TypeError(re.sub("__init__", f.__qualname__, te.args[0]))
            param_dict = asdict(params)
            if "self" in bound_args:
                param_dict["self"] = bound_args["self"]
            return f(**param_dict)

        wrapped.__doc__ = (
            wrapped.__doc__
            or """Short summary.


            Returns
            -------
            type
                Description of returned object.

            """
        )
        wrapped.__doc__ += "\n\nParameters\n---------\n" + "\n".join(
            [
                k + ": " + v.metadata[AUTOSIG_DOCSTRING]
                for k, v in fields_dict(Sig).items()
            ]
        )

        return wrapped

    return decorator if argument_deco else decorator(sig_or_f)


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
                "{name} called with argument x".format(
                    name=type_or_predicate.__qualname__
                )
                if isinstance(type_or_predicate, BuiltinFunctionType)
                else getsource(type_or_predicate)
            )
            + " where x=={x}",
        )
    )

    def f(_, attribute, x):
        assert predicate(x), msg.format(
            name=attribute.name,
            x=x,
            type_x=type(x),
            type_or_predicate=type_or_predicate,
        )

    return f
