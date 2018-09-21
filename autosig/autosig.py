"""Implementation of autosig."""
from attr import attrib, asdict, NOTHING, fields_dict, make_class
from collections import OrderedDict
from functools import wraps
from toolz.functoolz import curry
from itertools import chain
import inspect

__all__ = ["Signature", "autosig", "param"]

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
    metadata = {
        AUTOSIG_DOCSTRING: docstring,
        AUTOSIG_POSITION: position,
    }
    kwargs = locals()
    for key in ('docstring', 'position'):
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
    **params : attr._CountingAttr
        Each keyword argument becomes an argument in the signature of a function and must be initialized with a param call.

    Returns
    -------
    Signature
        The object created.
        
    """

    def __init__(self, **params):
        """See class docs."""
        self.params = OrderedDict(
            sorted(params.items(), key=keyfun(l=len(params))))

    def __add__(self, other):
        """Combine signatures.

        The resulting signature has the union of the arguments of the left and right operands. The order is determined by the position property of the parameters and when there's a tie, positions are stably sorted with the left operand coming before the right one. One a name clash occurs, the right operand, quite arbitraly, wins. Please do not rely on this behavior, it may change.
        """

        return Signature(
            **OrderedDict(chain(self.params.items(), other.params.items())))


def make_sig_class(sig):
    return make_class('Sig', attrs=sig.params, cmp=False)


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
        f_params = inspect.signature(f).parameters
        Sig_params = inspect.signature(Sig).parameters
        assert f_params == Sig_params, "\n".join([
            "Mismatched signatures:",
            str(f),
            str(f_params),
            str(Sig),
            str(Sig_params)
        ])  # compared as OrderedDicts, retval ignored TODO: support retval?

        @wraps(f)
        def wrapped(*args, **kwargs):
            params = Sig(
                **inspect.signature(f).bind(*args, **kwargs).arguments)
            return f(**asdict(params))

        wrapped.__doc__ = wrapped.__doc__ or """Short summary.


            Returns
            -------
            type
                Description of returned object.

            """
        wrapped.__doc__ += "\n\nParameters\n---------\n" + "\n".join([
            k + ": " + v.metadata[AUTOSIG_DOCSTRING]
            for k, v in fields_dict(Sig).items()
        ])

        return wrapped

    return decorator
