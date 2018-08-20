"""Tests for autosig."""
from hypothesis import given
from hypothesis.strategies import builds, text, dictionaries, just
from string import ascii_letters
from attr import make_class, asdict, attrib
from functools import partial
from autosig import Signature, autosig

# hypothesis strategy for identifiers
# min_size is 10 to avoid hitting reserved words by mistake
identifiers = partial(text, alphabet=ascii_letters, min_size=10)


def signatures():
    """Short summary.

    Returns
    -------
    type
        Description of returned object.

    """
    return builds(
        make_class,
        name=identifiers(),
        attrs=dictionaries(
            keys=identifiers(), values=just(attrib(default=True)), min_size=3),
        bases=just((Signature, )))


@given(sig=signatures())
def test_sig_checks(sig):
    """Autosig-decorated functions accept a compatible set of arguments."""

    @autosig(Sig=sig)
    def f(*args, **kwargs):
        pass

    f(**asdict(sig()))


@given(sig1=signatures(), sig2=signatures())
def test_sig_doesnt_check(sig1, sig2):
    """Autosig-decorated functions fail on an incompatible set of arguments."""

    @autosig(Sig=sig1)
    def f(*args, **kwargs):
        pass

    try:
        f(**asdict(sig2()))
    except Exception:
        return
    raise Exception
