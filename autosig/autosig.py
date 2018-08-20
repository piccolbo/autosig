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
        @wraps(f)
        def wrapped(*args, **kwargs):
            params = Sig(**inspect.getcallargs(f, *args, **kwargs))
            params.validate()
            return f(**asdict(params))

        return wrapped

    return decorator
