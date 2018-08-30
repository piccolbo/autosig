"""Tests for autosig."""
from hypothesis import given
from hypothesis.strategies import builds, text, dictionaries, just
from string import ascii_letters, punctuation
from attr import make_class, asdict
from functools import partial
from autosig import Signature, autosig, param

# hypothesis strategy for identifiers
# min_size is 10 to avoid hitting reserved words by mistake
identifiers = partial(text, alphabet=ascii_letters, min_size=5, max_size=10)
docstrings = partial(
    text,
    alphabet=ascii_letters + punctuation + " \n",
    min_size=25,
    max_size=50)


def params():
    """Generate params.

    Returns
    -------
    Hypothesis strategy
        Strategy to generate params.

    """
    return builds(param, default=text(), docstring=docstrings())


def signatures():
    """Generate signatures.

    Returns
    -------
    Hypothesis strategy
        Strategy to generate signatures.

    """
    a_class = builds(
        make_class,
        name=identifiers(),
        attrs=dictionaries(keys=identifiers(), values=params(), min_size=3),
        bases=just((Signature, )))
    return a_class


@given(sig=signatures())
def test_decorated_call(sig):
    """Autosig-decorated functions accept a compatible set of arguments."""

    autosig(sig)(sig)(**asdict(sig()))


@given(sig1=signatures(), sig2=signatures())
def test_decorator_fails(sig1, sig2):
    """Autosig-decorated functions fail on an incompatible signature."""
    deco = autosig(sig1)
    try:
        deco(sig2)
    except Exception:
        return
    raise Exception


@given(sig1=signatures(), sig2=signatures())
def test_decorated_call_fails(sig1, sig2):
    """Autosig-decorated functions fail on a call with incompatible arguments."""
    f = autosig(sig1)(sig1)
    try:
        f(**asdict(sig2()))
    except Exception:
        return
    raise Exception
