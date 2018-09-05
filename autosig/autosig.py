"""Implementation of autosig."""
from attr import attrs
from attr import attrib, asdict, NOTHING, fields_dict
from functools import wraps
import inspect

__all__ = ["Signature", "signature", "autosig", "param"]

AUTOSIG_DOCSTRING = "__autosig_docstring__"


def param(
        default=NOTHING,
        validator=None,
        converter=None,
        docstring="",
):
    """Define parameters in a signature class.

    Parameters
    ----------
    default : Any
        The default value for the parameter (defaults to no default, that is mandatory).
    validator : callable or list thereof
        A validator for the actual parameter. If list, all element of the list are called. Return value is ignored, only exceptions raised count.
    converter : callable
        The callable is executed with the parameter as an argument and its value assigned to the parameter itself. Useful for type conversions, but not only (e.g. limit range of parameter)
    docstring : string
        Description of parameter `docstring` (the default is "").

    Notes
    -----
    Type annotations will be enforced. This is a thin layer over attrs's attrib().

    Returns
    -------
    attr.Attribute
        Object describing all the properties of the parameter. Can be reused in multiple signature definitions to enforce consistency.

    """
    metadata = {}
    metadata[AUTOSIG_DOCSTRING] = docstring
    kwargs = locals()
    del kwargs['docstring']
    return attrib(**kwargs)


def signature(cls):
    """Decorate class to be used as signature.

    Parameters
    ----------
    cls : class
        The class to use as signature.

    Returns
    -------
    class
        A class that can be used as signature (passed as argument to autosig).

    """
    return attrs(cls, cmp=False)


@signature
class Signature:
    """Base class for signatures."""

    def validate(self):
        """Validate arguments as a whole.

        Per-argument validation is done with `param`
        """
        pass

    def default(self):
        """Provide defaults that depend on the value of other arguments.

        Per-argument defaults are set with `param`
        """
        pass


def autosig(Sig):
    """Decorate  functions to attach signatures.

    Parameters
    ----------
    Sig : A subclass of Signature
        A class with one member per parameter, initialized with a call to param

    Returns
    -------
    function
        The decorated function, will intialize, convert, and
        validate its arguments.

    """

    def decorator(f):
        f_params = inspect.signature(f).parameters
        Sig_params = inspect.signature(Sig).parameters
        assert f_params == Sig_params, "\n".join([
            "Mismatched signatures:",
            str(f),
            str(f_params),
            str(Sig),
            str(Sig_params)
        ])

        @wraps(f)
        def wrapped(*args, **kwargs):
            params = Sig(
                **inspect.signature(f).bind(*args, **kwargs).arguments)
            params.default()
            params.validate()
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
