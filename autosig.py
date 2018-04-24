"""Implementation of autosig."""
from attr import attrs
from attr import attrib as param
from attr import asdict
from functools import wraps

__all__ = "Signature signature autosig param".split()

signature = attrs

@attrs
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


# def signature(Base=Signature):
#     def decorator(decoratee):
#         @attrs
#         class Decorated(Base, decoratee):
#             pass
#
#         return Decorated
#     return decorator


def autosig(sig):
    """Short summary.

    Parameters
    ----------
    sig : type
        Description of parameter `sig`.

    Returns
    -------
    type
        Description of returned object.

    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            params = sig(*args, **kwargs)
            params.validate()
            return f(**asdict(params))

        return wrapped

    return decorator
