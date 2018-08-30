"""Implementation of autosig."""
from attr import attrs as signature
from attr import attrib, asdict, NOTHING, fields_dict
from functools import wraps
import inspect

__all__ = ["Signature", "signature", "autosig", "param"]

AUTOSIG_DOCSTRING = "__autosig_docstring__"


def param(
        default=NOTHING,
        validator=None,
        repr=True,
        cmp=True,
        hash=None,
        init=True,
        convert=None,
        metadata=None,
        type=None,
        converter=None,
        factory=None,
        docstring="",
):
    """See below."""
    if metadata is None:
        metadata = {}
    metadata[AUTOSIG_DOCSTRING] = docstring
    return attrib(
        default=default,
        validator=validator,
        repr=repr,
        cmp=cmp,
        hash=hash,
        init=init,
        convert=convert,
        metadata=metadata,
        type=type,
        converter=converter,
        factory=factory,
    )


# TODO:fix docs
param.__doc__ = attrib.__doc__


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
