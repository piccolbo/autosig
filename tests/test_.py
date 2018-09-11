"""Tests for autosig."""
from attr import make_class, asdict
from autosig import Signature, autosig, param
from functools import partial
from hypothesis import (
    HealthCheck,
    PrintSettings,
    assume,
    given,
    #    reproduce_failure,
    settings,
    unlimited,
)
from hypothesis.strategies import builds, text, dictionaries, just
import inspect
from string import ascii_letters, punctuation

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
        bases=just((Signature, )),
    )
    return a_class


settings.register_profile(
    "this",
    timeout=unlimited,
    suppress_health_check=[HealthCheck.too_slow],
    print_blob=PrintSettings.ALWAYS,
)
settings.load_profile("this")


@given(sig=signatures())
def test_decorated_call(sig):
    """Autosig-decorated functions accept a compatible set of arguments."""

    autosig(sig)(sig)(**asdict(sig()))


@given(sig1=signatures(), sig2=signatures())
def test_decorator_fails(sig1, sig2):
    """Autosig-decorated functions fail on an incompatible signature."""
    assume(
        inspect.signature(sig1).parameters !=\
        inspect.signature(sig2).parameters)
    deco = autosig(sig1)
    try:
        deco(sig2)
    except Exception:
        return
    raise Exception


# @reproduce_failure("3.69.12",
#                   b"AXicY2RkgEEGBkaSIQMjnM1IkX5GMu3H7hbK/EKuWygNC2Q2AKKOAMk=")
@given(sig1=signatures(), sig2=signatures())
def test_decorated_call_fails(sig1, sig2):
    """Autosig-decorated functions fail on a call with incompatible arguments."""
    assume(
        dict(inspect.signature(sig1).parameters)!=\
        dict(inspect.signature(sig2).parameters)
    )  # yapf: disable we are ignoring order at this time TODO: fix
    f = autosig(sig1)(sig1)
    try:
        f(**asdict(sig2()))
    except Exception:
        return
    raise Exception
