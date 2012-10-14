`blade` is a powerful `Python <http://docs.python.org/>`_ multitool
loosely inspired by `Underscore.js <http://documentcloud.github.com/underscore/>`_
but remixed for maximum `pythonicity <http://docs.python.org/glossary.html#term-pythonic>`_. 

`blade` concentrates power that is normally dispersed across the entire
Python universe in one convenient shrink-wrapped package.

Vitals
======

`blade` works with CPython 2.6, 2.7, 3.1. and 3.2 and PyPy 1.8.

`blade` documentation is at http://readthedocs.org/docs/blade/en/latest/ or
http://packages.python.org/blade/

Installation
============

Install `blade` with `pip <http://www.pip-installer.org/en/latest/index.html>`_...::

  $ pip install blade
  [... possibly exciting stuff happening ...]
  Successfully installed blade
  
...or `easy_install <http://packages.python.org/distribute/>`_...::

  $ easy_install blade
  [... possibly exciting stuff happening ...]
  Finished processing dependencies for blade
  
...or old school by downloading `blade` from http://pypi.python.org/pypi/blade/::

  $ python setup.py install
  [... possibly exciting stuff happening ...]
  Finished processing dependencies for blade

Development
===========

 * Public repository: https://bitbucket.org/lcrees/blade.
 * Mirror: https://github.com/kwarterthieves/blade/
 * Issue tracker: https://bitbucket.org/lcrees/blade/issues
 * License: `BSD <http://www.opensource.org/licenses/bsd-license.php>`_

3 second *blade*
================

Things go in:

  >>> from blade import __
  >>> gauntlet = __(5, 4, 3, 2, 1)
  
Things get bladed:

  >>> gauntlet.initial().rest().slice(1, 2).last()
  blade.lazy.lazyblade ([IN: ([3]) => WORK: ([]) => HOLD: ([]) => OUT: ([3])])

Things come out:

  >>> gauntlet.get()
  3

Slightly more *blade*
=====================

`blade` has 40 plus methods that can be `chained <https://en.wikipedia.org/
wiki/Fluent_interface>`_ into pipelines...

contrived example:
^^^^^^^^^^^^^^^^^^

  >>> __(5, 4, 3, 2, 1).initial().rest().slice(1, 2).last().get()
  3

...or used object-oriented style.

contrived example:
^^^^^^^^^^^^^^^^^^

  >>> from blade import blade
  >>> oo = blade(5, 4, 3, 2, 1)
  >>> oo.initial()
  blade.active.activeblade ([IN: ([5, 4, 3, 2, 1]) => WORK: ([]) => HOLD: ([]) => OUT: ([5, 4, 3, 2])])
  >>> oo.rest()
  blade.active.activeblade ([IN: ([5, 4, 3, 2]) => WORK: ([]) => HOLD: ([]) => OUT: ([4, 3, 2])])
  >>> oo.slice(1, 2)
  blade.active.activeblade ([IN: ([4, 3, 2]) => WORK: ([]) => HOLD: ([]) => OUT: ([3])])
  >>> oo.last()
  blade.active.activeblade ([IN: ([3]) => WORK: ([]) => HOLD: ([]) => OUT: ([3])])
  >>> oo.get()
  3
  
A `blade` object can roll its current state back to previous states
like snapshots of immediately preceding operations, a baseline snapshot, or even 
a snapshot of the original arguments.

contrived example:
^^^^^^^^^^^^^^^^^^
  
  >>> undone = __(1, 2, 3).prepend(1, 2, 3, 4, 5, 6)
  >>> undone.peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.append(1).undo().peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.append(1).append(2).undo(2).peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.snapshot().append(1).append(2).baseline().peek()
  [1, 2, 3, 4, 5, 6, 1, 2, 3]
  >>> undone.original().peek()
  [1, 2, 3]

`blade` objects come in two flavors: `active` and `lazy`.
`active.blade` objects evaluate the result of calling a
method immediately after the call. Calling the same method with
a `lazy.blade` object only yields results when it is iterated over
or `blade.lazy.lazyblade.get` is called to get results.
  
`blade.lazy.lazyblade` combines all `blade` methods in one class:

  >>> from blade import lazyblade

It can be imported under its *dunderscore* (`blade.__`) alias.

  >>> from blade import __  
  
`blade.active.activeblade` also combines every `blade` method in one
combo `blade` class:

  >>> from blade import activeblade

It can be imported under its `blade.blade` alias:
 
  >>> from blade import blade

`blade` methods are available in more focused classes that group related 
methods together. These classes can also be chained into pipelines.

contrived example:
^^^^^^^^^^^^^^^^^^

  >>> from blade.active import mathblade, reduceblade
  >>> one = mathblade(10, 5, 100, 2, 1000)
  >>> two = reduceblade()
  >>> one.minmax().pipe(two).merge().back().min().get()
  2
  >>> one.original().minmax().pipe(two).merge().back().max().get()
  1000
  >>> one.original().minmax().pipe(two).merge().back().sum().get()
  1002