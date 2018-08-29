"""Implementation of autosig."""
from attr import attrs as signature
from attr import attrib as param
from attr import asdict
from functools import wraps
import inspect

__all__ = ["Signature", "signature", "autosig", "param"]


@signature
class Signature:
    """Base class for signatures."""

    def validate(self):
        """Short summary.

        Returns
        -------
        type
            Description of returned object.

        """
        return True

    def default(self):
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
            params.validate()
            return f(**asdict(params))

        return wrapped

    return decorator
