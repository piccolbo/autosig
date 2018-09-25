=======
Autosig
=======


.. image:: https://img.shields.io/pypi/v/autosig.svg
        :target: https://pypi.python.org/pypi/autosig

.. image:: https://img.shields.io/travis/piccolbo/autosig.svg
        :target: https://travis-ci.org/piccolbo/autosig

.. image:: https://codecov.io/gh/piccolbo/autosig/branch/master/graph/badge.svg
        :target: https://codecov.io/gh/piccolbo/autosig

.. image:: https://readthedocs.org/projects/autosig/badge/?version=latest
        :target: https://autosig.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/piccolbo/autosig/shield.svg
     :target: https://pyup.io/repos/github/piccolbo/autosig/
     :alt: Updates




Autosig helps you write good python 3 APIs. Go straight to the `documentation <https://autosig.readthedocs.io/en/latest/>`_. Install with ``pip install autosig``. Python 3 only.

Motivation
----------

When I look at a great API I always observe a great level of consistency: similarly named and ordered arguments at a syntactic level; similar defaults, range of allowable values etc. on the semantic side. When looking at the code, one doesn't see these regularities represented very explicitly.

Imagine we are starting to develop a library with three entry points, ``map``, ``reduce`` and ``filter``::

  from collections import Iterable


  def map(function, iterable):
      assert callable(function)
      assert isinstance(iterable, Iterable)
      return (function(x) for x in iterable)


  def reduce(function, iterable):
      total = next(iterable)
      for x in iterable:
          total = function(total, x)
      return total


  def filter(iterable, fun):
      if not isinstance(iterable, Iterable):
          iterable = [iterable]
      if isinstance(fun, set):
          fun = lambda x: x in fun
      return (x for x in iterable if fun(x))



But this is hardly well crafted. The order and naming of arguments isn't consistent. One function checks its argument right away. The next doesn't. The third attempts certain conversions to try and work with arguments that are not iterables or functions. There are reasons to build strict or tolerant APIs, but it's unlikely that mixing the two within the same API is a good idea, unless it's done deliberately (for instance offering a strict and tolerant version of every function). It wouldn't be difficult to fix these problems in this small API but we would end up with duplicated logic that we need to keep aligned for the foreseeable future. Let's do it instead the ``autosig`` way::

  from autosig import param, Signature, autosig, check
  from collections import Iterable


  def to_callable(x):
      return (lambda y: y in x) if isinstance(x, set) else x


  def to_iterable(x):
      return x if isinstance(x, Iterable) else [x]


  API_signature = Signature(
      function=param(converter=to_callable, validator=check(callable)),
      iterable=param(converter=to_iterable, validator=check(Iterable)))


  @autosig(API_signature)
  def map(function, iterable):
      return (function(x) for x in iterable)


  @autosig(API_signature)
  def reduce(function, iterable):
      total = next(iterable)
      for x in iterable:
          total = function(total, x)
      return total


  @autosig(API_signature)
  def filter(function, iterable):
      return (x for x in iterable if function(x))


Let's go through it step by step. First we defined 2 simple conversion
functions. This is a good first step independent of ``autosig``. Next we create
a signature object, with two parameters. These are intialized with objects that
define the checking and conversion that needs to be done on those parameters,
independent of which function is going to use that signature. ``check`` creates
a function that uses its argument, a Callable or Iterable, to validate an
argument. Finally, we repeat the definition of our three API function, attaching
the signature just defined with a decorator and then skipping all the checking
and conversion logic and going straight to the meat of the function!

At the cost of a little more code we have gained a lot:

* Explicit definition of the desired API signature, in a single place --- DRY principle;
* association of that signature with API functions, checked at load time --- no room for error;
* uniform application of conversion and validation logic without repeating it;

``autosig`` is the pro tool for the API designer! If you want to take a look at a real package that uses ``autosig``, check out `altair_recipes <https://github.com/piccolbo/altair_recipes>`_.


Features
--------

* Define reusable parameters with defaults, conversion and validation logic, documentation, preferred position in the signature and whether keyword-only.
* Define reusable signatures as ordered maps from names to parameters.
* Combine signatures to create complex ones on top of simple ones.
* Decorate functions with their signatures. Enforced at load time. Conversion and validation logic executed at call time.
* Open source (BSD license)
* Extensive property-based testing, excellent coverage



Credits
-------

This package is heavily based on `attrs <https://github.com/python-attrs/attrs>`_. While that may change in the future, for now it must be said this is a thin layer over that, with a bit of reflection sprinkled over. It is, I suppose, a quite original direction to take ``attrs`` into.

This package was created with Cookiecutter_ and the `elgertam/cookiecutter-pipenv`_ project template, based on `audreyr/cookiecutter-pypackage`_.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`elgertam/cookiecutter-pipenv`: https://github.com/elgertam/cookiecutter-pipenv
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
