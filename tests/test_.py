"""Tests for autosig."""
from attr import asdict
from autosig import Signature, autosig, param, check
from autosig.autosig import make_sig_class
from functools import partial
from hypothesis import (
    HealthCheck,
    PrintSettings,
    assume,
    given,
    # reproduce_failure,
    settings,
    unlimited,
)
from hypothesis.strategies import builds, text, dictionaries
from inspect import signature
from pytest import raises
from string import ascii_letters, punctuation

# hypothesis strategy for identifiers
# min_size is 5 to avoid hitting reserved words by mistake
identifiers = partial(text, alphabet=ascii_letters, min_size=5, max_size=10)
docstrings = partial(
    text, alphabet=ascii_letters + punctuation + " \n", min_size=25, max_size=50
)


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

    return builds(
        lambda x: Signature(**x), dictionaries(keys=identifiers(), values=params())
    )


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

    Sig = make_sig_class(sig)
    autosig(sig)(Sig)(**asdict(Sig()))


@given(sig1=signatures(), sig2=signatures())
def test_decorator_fails(sig1, sig2):
    """Autosig-decorated functions fail on an incompatible signature."""
    Sig1 = make_sig_class(sig1)
    Sig2 = make_sig_class(sig2)
    assume(signature(Sig1).parameters != signature(Sig2).parameters)
    deco = autosig(sig1)
    try:
        deco(Sig2)
    except Exception:
        return
    raise Exception


@given(sig1=signatures(), sig2=signatures())
def test_decorated_call_fails(sig1, sig2):
    """Autosig-decorated functions fail on a call with incompatible arguments."""
    Sig1 = make_sig_class(sig1)
    Sig2 = make_sig_class(sig2)
    assume(
        not set(signature(Sig2).parameters.keys())
        <= set(signature(Sig1).parameters.keys())
    )

    f = autosig(sig1)(Sig1)
    try:
        f(**asdict(Sig2()))
    except Exception:
        return
    raise Exception


def test_argumentless_decorator():
    """Non-randomized test for argumentless decorator
    """

    @autosig
    def fun(a=param(validator=check(int))):
        pass

    fun(1)
    with raises(
        AssertionError,
        message="type of a = 1.0 should be <class 'int'>, <class 'float'> found instead",
    ):
        fun(1.0)
