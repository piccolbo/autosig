"""Tests for autosig."""
from attr import asdict
from autosig import Signature, autosig, param
from autosig.autosig import make_sig_class
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
from hypothesis.strategies import builds, text, dictionaries
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

    def single_arg_Signature(d):
        return Signature(**d)

    return builds(single_arg_Signature,
                  dictionaries(
                      keys=identifiers(), values=params(), min_size=3))
    # TODO: we may be able to eliminate the min_size now that we are not making any probabilty assumptions


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
    assume(
        inspect.signature(Sig1).parameters !=\
        inspect.signature(Sig2).parameters)
    deco = autosig(sig1)
    try:
        deco(Sig2)
    except Exception:
        return
    raise Exception


# @reproduce_failure("3.69.12",
#                   b"AXicY2RkgEEGBkaSIQMjnM1IkX5GMu3H7hbK/EKuWygNC2Q2AKKOAMk=")
@given(sig1=signatures(), sig2=signatures())
def test_decorated_call_fails(sig1, sig2):
    """Autosig-decorated functions fail on a call with incompatible arguments."""
    Sig1 = make_sig_class(sig1)
    Sig2 = make_sig_class(sig2)
    assume(
        dict(inspect.signature(Sig1).parameters)!=\
        dict(inspect.signature(Sig2).parameters)
    )  # yapf: disable we are ignoring order at this time TODO: fix
    f = autosig(sig1)(Sig1)
    try:
        f(**asdict(Sig2()))
    except Exception:
        return
    raise Exception
