=======
History
=======


0.9.2 (2019-10-1)
-----------------

* Single argument validators.
* Late init feature for signatures.

0.8.2 (2019-09-18)
------------------

* Switch from pipenv to poetry for development

0.8.0 (2019-08-27)
------------------

* autosig can decorate methods (exclude self from signature)

0.7.0 (2018-09-25)
------------------

* Argumentless autosig decorator for the use case of reusable parameter definitions but no reusable signatures.

0.6.0 (2018-09-24)
------------------

* Added ``check`` the quick validator generator. ``check(int)`` checks an argument is integer. ``check(\lambda x: x>0)`` checks an argument is positive. Behind the scenes it creates uses an assert statement which hopefully prints a useful message.

0.5.0 (2018-09-21)
------------------

* All new API, many breaking changes (sorry)
* signature decorator is gone
* create signatures directly withe the Signature constructor (it is no longer a base class to inherit from)
* do not use inheritance to define new signatures form old ones. It was a dead end as far as controlling the order of arguments. Use instead  the + operator to combine two signatures, analogous to inheriting from one while adding new attributes.
* the new approach gives control over order of arguments, allows to mix mandatory and default arguments in one signature yet allow to reuse it ("stick" new mandatory arguments in between the arguments of the old signature)

0.4.1 (2018-09-05)
------------------

* Close abstraction holes revealing dependency on attr (which is gratefully acknowledged, but could be confusing).

0.3.1 (2018-08-30)
------------------

* Improved docstring generation

0.3.0 (2018-08-30)
------------------

* Compose docstring from param docstrings

0.2.3 (2018-08-28)
------------------

* Better and passing tests.

0.2.2 (2018-08-27)
------------------

* More stringent enforcement of signatures including defaults. Fixed build.

0.1.0 (2018-04-25)
------------------

* First release on PyPI.
