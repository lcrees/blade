# -*- coding: utf-8 -*-
'''blade mixins.'''

from math import fsum
from copy import deepcopy
from inspect import getmro, isclass
from random import randrange, shuffle
from functools import reduce, partial
from collections import deque, namedtuple
from operator import attrgetter, itemgetter, methodcaller, truediv
from itertools import (
    chain, combinations, groupby, islice, repeat, permutations, starmap, tee)

from stuf.deep import selfname, members
from stuf.base import identity, dualidentity
from stuf.six.moves import filterfalse, zip_longest  # @UnresolvedImport
from stuf.collects import OrderedDict, Counter, ChainMap
from stuf.iterable import deferfunc, deferiter, count, partmap, partstar
from stuf.six import (
    filter, items, keys as keyz, map as xmap, isstring, values as valuez, next)

Count = namedtuple('Count', 'least most overall')
GroupBy = namedtuple('Group', 'keys groups')
MinMax = namedtuple('MinMax', 'min max')
TrueFalse = namedtuple('TrueFalse', 'true false')
slicer = partial(lambda n, i, x, y: n(i(x, y, None)), next, islice)
xmerge = chain.from_iterable
xsort = sorted
xreverse = reversed
xpermutate = permutations
xcombine = combinations
xzip = partial(lambda zl, i: zl(*i), zip_longest)

################################################################################
## BLADE COMPARISON OPERATIONS #################################################
################################################################################

def xall(iterable, func, cut=False):
    '''
    Discover if `func` is :data:`True` for **all** items in `iterable`.

   :argument iterable: iterable object
    :return: :func:`bool`

    >>> from blade import xall, oneorall
    >>> xall(lambda x: x % 2 == 0, (2, 4, 6, 8))
    True
    '''
    return all(xmap(func, iterable))

def xany(iterable, func):
    '''
    Discover if `func` is :data:`True` for **any** items in `iterable`.

   :argument iterable: iterable object
    :return: :func:`bool`

    >>> from blade import xany
    >>> oneorall(list(xany(lambda x: x % 2 == 0, (1, 4, 5, 9))))
    True
    '''
    return any(xmap(func, iterable))

def xdiff(iterable, symmetric=False):
    '''
    Discover difference within a series of iterable items in `iterable`.

    :argument iterable: iterable object
    :keyword bool symmetric: do a symmetric difference operation

    :return: :func:`list`

    >>> from blade import xdiff
    >>> # default behavior
    >>> list(xdiff(([1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2])))
    [1, 3, 4]
    >>> # symmetric difference
    >>> list(xdiff(([1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2]), False))
    [1, 2, 3, 4, 11]
    '''
    if symmetric:
        test = partial(lambda s, x, y: s(x).symmetric_difference(y), set)
    else:
        test = partial(lambda s, x, y: s(x).difference(y), set)
    return reduce(test, iterable)

def xintersect(iterable):
    '''
    Discover intersection within a series of iterable items in `iterable`.

    :argument iterable: iterable object
    :return: :func:`list`

    >>> from blade import xintersect
    >>> list(xintersect(([1, 2, 3], [101, 2, 1, 10], [2, 1])))
    [1, 2]
    '''
    return reduce(partial(lambda s, x, y: s(x).intersection(y), set), iterable)

def xunion(iterable):
    '''
    Discover union within a series of iterable items in `iterable`.

    :argument iterable: iterable object
    :return: :func:`list`

    >>> from blade import xunion
    >>> list(xunion(([1, 2, 3], [101, 2, 1, 10], [2, 1])))
    [1, 10, 3, 2, 101]
    '''
    return reduce(partial(lambda s, x, y: s(x).union(y), set), iterable)

def xunique(iterable, func=None):
    '''
    Discover unique items in `iterable`.

    :argument iterable: iterable object

    >>> from blade import xunique
    >>> # no key function
    >>> list(xunique((1, 2, 1, 3, 1, 4)))
    [1, 2, 3, 4]
    >>> # with key function
    >>> list(xunique(round, (1, 2, 1, 3, 1, 4)))
    [1.0, 2.0, 3.0, 4.0]
    '''
    def unique(key, iterable, _n=next):
        seen = set()
        seenadd = seen.add
        try:
            while 1:
                element = key(_n(iterable))
                if element not in seen:
                    yield element
                    seenadd(element)
        except StopIteration:
            pass
    return unique(identity if func is None else func, iter(iterable))

################################################################################
## BLADE MATH OPERATIONS #######################################################
################################################################################

def xaverage(iterable):
    '''
    Discover average value of numbers in `iterable`.

    :argument iterable: iterable object
    :return: a number

    >>> from blade import xaverage
    >>> oneorall(list(xaverage((10, 40, 45))))
    31.666666666666668
    '''
    i1, i2 = tee(iterable)
    return truediv(sum(i1, 0.0), count(i2))

def xcount(iterable):
    '''
    Discover how common each item in `iterable` is and the overall count of
    each item in `iterable`.

    :argument iterable: iterable object

    :return: Collects :func:`~collections.namedtuple` ``Count(least=int,
      most=int, overall=[(thing1, int), (thing2, int), ...])``

    >>> common = __(11, 3, 5, 11, 7, 3, 5, 11).count().get()
    >>> # least common thing
    >>> common.least
    7
    >>> # most common thing
    >>> common.most
    11
    >>> # total count for every thing
    >>> common.overall
    [(11, 3), (3, 2), (5, 2), (7, 1)]
    '''
    cnt = Counter(iterable).most_common
    commonality = cnt()
    return Count(
        # least common
        commonality[:-2:-1][0][0],
        # most common (mode)
        cnt(1)[0][0],
        # overall commonality
        commonality,
    )

def xmedian(iterable):
    '''
    Discover the median value among items in `iterable`.

    :argument iterable: iterable object
    :return: a number

    >>> __(4, 5, 7, 2, 1).median().get()
    4
    >>> __(4, 5, 7, 2, 1, 8).median().get()
    4.5
    '''
    i1, i2 = tee(sorted(iterable))
    result = truediv(count(i1) - 1, 2)
    pint = int(result)
    if result % 2 == 0:
        return slicer(i2, pint)
    i3, i4 = tee(i2)
    return truediv(slicer(i3, pint) + slicer(i4, pint + 1), 2)

def xminmax(iterable):
    '''
    Discover the minimum and maximum values among items in `iterable`.

    :argument iterable: iterable object
    :return:  :func:`~collections.namedtuple` ``MinMAx(min=value, max=value)``.

    >>> minmax = __(1, 2, 4).minmax().get()
    >>> minmax.min
    1
    >>> minmax.max
    4
    '''
    i1, i2 = tee(iterable)
    return MinMax(min(i1), max(i2))

def xinterval(iterable):
    '''
    Discover the length of the smallest interval that can contain the value of
    every items in `iterable`.

    :argument iterable: iterable object

    :return: a number

    >>> __(3, 5, 7, 3, 11).range().get()
    8
    '''
    i1, i2 = tee(sorted(iterable))
    return deque(i1, maxlen=1).pop() - next(i2)

def xsum(iterable, start=0, precision=False):
    '''
    Discover the total value of adding `start` and items in `iterable` together.

    :argument iterable: iterable object
    :keyword start: starting number
    :type start: :func:`int` or :func:`float`
    :keyword bool precision: add floats with extended precision

    >>> # default behavior
    >>> __(1, 2, 3).sum().get()
    6
    >>> # with a starting mumber
    >>> __(1, 2, 3).sum(start=1).get()
    7
    >>> # add floating points with extended precision
    >>> __(.1, .1, .1, .1, .1, .1, .1, .1).sum(precision=True).get()
    0.8
    '''
    return fsum(iterable) if precision else sum(iterable, start)

################################################################################
## BLADE ORDERING OPERATIONS ###################################################
################################################################################

def xgroup(iterable, func=None):
    '''
    Group items in `iterable` using `func` as the :term:`key function`.

    :argument iterable: iterable object

    :return: :func:`~collections.namedtuple` ``Group(keys=keys, groups=tuple)``

    >>> from blade import __
    >>> # default grouping
    >>> __(1.3, 2.1).group().get()
    [Group(keys=1.3, groups=(1.3,)), Group(keys=2.1, groups=(2.1,))]
    >>> from math import floor
    >>> # use func for key function
    >>> __(1.3, 2.1, 2.4).func(floor).group().get()
    [Group(keys=1.0, groups=(1.3,)), Group(keys=2.0, groups=(2.1, 2.4))]
    '''
    def grouper(func, iterable, _n=next, _g=GroupBy, _t=tuple):
        try:
            it = groupby(sorted(iterable, key=func), func)
            while 1:
                k, v = _n(it)
                yield _g(k, _t(v))
        except StopIteration:
            pass
    return grouper(identity if func is None else func, iterable)


def xshuffle(iterable):
    '''
    Randomly sort items in `iterable`.

    :argument iterable: iterable object

    >>> __(5, 4, 3, 2, 1).shuffle().get() # doctest: +SKIP
    [3, 1, 5, 4, 2]
    '''
    iterable = list(iterable)
    shuffle(iterable)
    return iterable

################################################################################
## BLADE REPEATING OPERATIONS ##################################################
################################################################################

def xcopy(iterable):
    '''
    Duplicate each items in `iterable`.

    :argument iterable: iterable object

    >>> __([[1, [2, 3]], [4, [5, 6]]]).copy().get()
    [[1, [2, 3]], [4, [5, 6]]]
    '''
    return xmap(deepcopy, iterable)

def xrepeat(iterable, n=None, func=False):
    '''
    Repeat items in `iterable` `n` times or invoke `func` `n` times.

    :argument iterable: iterable object
    :keyword int n: number of times to repeat
    :keyword bool func: repeat results of invoking `func`

    >>> # repeat iterable
    >>> __(40, 50, 60).repeat(3).get()
    [(40, 50, 60), (40, 50, 60), (40, 50, 60)]
    >>> def test(*args):
    ...    return list(args)
    >>> # with func
    >>> __(40, 50, 60).func(test).repeat(n=3, func=True).get()
    [[40, 50, 60], [40, 50, 60], [40, 50, 60]]
    '''
    if not func:
        return repeat(tuple(iterable), n)
    return starmap(func, repeat(tuple(iterable), n))


################################################################################
## BLADE MAPPING OPERATIONS ####################################################
################################################################################

def xargmap(iterable, func, merge=False, *args):
    '''
    Feed each items in `iterable` to `func` as :term:`positional
    argument`\s.

    :argument iterable: iterable object

    :keyword bool merge: merge global positional :meth:`params` with
      positional arguments derived from items in `iterable` when passed to
      `func`

    >>> from blade import __
    >>> # default behavior
    >>> test = __((1, 2), (2, 3), (3, 4))
    >>> test.func(lambda x, y: x * y).argmap().get()
    [2, 6, 12]
    >>> # merge global positional arguments with iterable arguments
    >>> test.original().func(
    ...   lambda x, y, z, a, b: x * y * z * a * b
    ... ).params(7, 8, 9).argmap(merge=True).get()
    [1008, 3024, 6048]
    '''
    if merge:
        return partstar(lambda f, *arg: f(*(arg + args)), iterable, func)
    return starmap(func, iterable)

def xinvoke(iterable, name, *args, **kw):
    '''
    Feed global :term:`positional argument`\s and :term:`keyword
    argument`\s to each items in `iterable`'s `name` :term:`method`.

    .. note::

      The original thing is returned if the return value of :term:`method`
      `name` is :data:`None`.

    :argument iterable: iterable object
    :argument str name: method name

    :rtype: :obj:`blade` :term:`object`

    >>> # invoke list.index()
    >>> __([5, 1, 7], [3, 2, 1]).params(1).invoke('index').get()
    [1, 2]
    >>> # invoke list.sort() but return sorted list instead of None
    >>> __([5, 1, 7], [3, 2, 1]).invoke('sort').get()
    [[1, 5, 7], [1, 2, 3]]
    '''
    def invoke(caller, thing):
        read = caller(thing)
        return thing if read is None else read
    return partmap(invoke, iterable, methodcaller(name, *args, **kw))

def xkwargmap(iterable, func, merge=False, *args, **kw):
    '''
    Feed each items in `iterable` as a :func:`tuple` of
    :term:`positional argument`\s and :term:`keyword argument`\s to
    `func`.

    :argument iterable: iterable object

    :keyword bool merge: merge global positional or keyword :meth:`params`
      with positional and keyword arguments derived from items in `iterable`
      into a single :func:`tuple` of wildcard positional and keyword
      arguments like ``(*iterable_args + global_args, **global_kwargs +
      iterable_kwargs)`` when passed to `func`

    >>> # default behavior
    >>> test = __(
    ...  ((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})
    ... )
    >>> def tester(*args, **kw):
    ...    return sum(args) * sum(kw.values())
    >>> test.func(tester).kwargmap().get()
    [6, 10, 14]
    >>> # merging global and iterable derived positional and keyword args
    >>> test.original().func(tester).params(
    ...   1, 2, 3, b=5, w=10, y=13
    ... ).kwargmap(merge=True).get()
    [270, 330, 390]
    '''
    if merge:
        def kwargmap(func, *params):
            arg, kwarg = params
            kwarg.update(kw)
            return func(*(arg + args), **kwarg)
    else:
        kwargmap = lambda f, x, y: f(*x, **y)
    return partstar(kwargmap, iterable, func)

def xkeyvalue(iterable, func=None, keys=False, values=False):
    '''
    Run `func` on incoming :term:`mapping` things.

    :argument iterable: iterable object
    :keyword bool keys: collect mapping keys only
    :keyword bool values: collect mapping values only

    >>> # filter items
    >>> __(dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
    ... ).func(lambda x, y: x * y).mapping().get()
    [2, 6, 12, 2, 6, 12]
    >>> # mapping keys only
    >>> __(dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
    ... ).mapping(keys=True).get()
    [1, 2, 3, 1, 2, 3]
    >>> # mapping values only
    >>> __(dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])
    ... ).mapping(values=True).get()
    [2, 3, 4, 2, 3, 4]
    '''

    if keys:
        func = identity if func is None else func
        return xmap(func, xmerge(xmap(keyz, iterable)))
    elif values:
        func = identity if func is None else func
        return xmap(func, xmerge(xmap(valuez, iterable)))
    func = dualidentity if func is None else func
    return starmap(func, xmerge(xmap(items, iterable)))

################################################################################
## BLADE FILTERING OPERATIONS ##################################################
################################################################################

def xattrs(iterable, *names):
    '''
    Collect :term:`attribute` values from items in `iterable` that match an
    **attribute name** found in `names`.

    :argument iterable: iterable object
    :argument str names: attribute names

    >>> from blade import __
    >>> from stuf import stuf
    >>> stooge = [
    ...    stuf(name='moe', age=40),
    ...    stuf(name='larry', age=50),
    ...    stuf(name='curly', age=60),
    ... ]
    >>> __(*stooge).attrs('name').get()
    ['moe', 'larry', 'curly']
    >>> # multiple attribute names
    >>> __(*stooge).attrs('name', 'age').get()
    [('moe', 40), ('larry', 50), ('curly', 60)]
    >>> # no attrs named 'place'
    >>> __(*stooge).attrs('place').get()
    []
    '''
    def attrs(iterable, _n=next):
        try:
            get = attrgetter(*names)
            while 1:
                try:
                    yield get(_n(iterable))
                except AttributeError:
                    pass
        except StopIteration:
            pass
    return attrs(iter(iterable))

def xtruefalse(iterable, func):
    '''
    Divide items in `iterable` into two `iterable`\s, the first everything
    `func` is :data:`True` for and the second everything `func` is :data:`False`
    for.

    :argument iterable: iterable object

    >>> divide = xtruefalse([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)
    >>> divide.true
    (2, 4, 6)
    >>> divide.false
    (1, 3, 5)
    '''
    truth, false = tee(iterable)
    return TrueFalse(
        tuple(filter(func, truth)), tuple(filterfalse(func, false))
    )

def xfilter(iterable, func, invert=False):
    '''
    Collect items in `iterable` matched by `func`.

    :argument iterable: iterable object

    :keyword bool invert: collect items in `iterable` `func` is
      :data:`False` rather than :data:`True` for

    >>> # filter for true values
    >>> list(xfilter([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)
    [2, 4, 6]
    >>> # filter for false values
    >>> list(xfilter([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0, invert=True)
    [1, 3, 5]
    '''
    return (filterfalse if invert else filter)(func, iterable)

def xitems(iterable, *keys):
    '''
    Collect values from items in `iterable` (usually a :term:`sequence` or
    :term:`mapping`) that match a **key** found in `keys`.

    :argument iterable: iterable object

    :argument str keys: keys or indices

    >>> stooge = [
    ...    dict(name='moe', age=40),
    ...    dict(name='larry', age=50),
    ...    dict(name='curly', age=60)
    ... ]
    >>> # get items from mappings like dictionaries, etc...
    >>> list(xitems(stooge, 'name'))
    ['moe', 'larry', 'curly']
    >>> list(xitems(stooge, 'name', 'age'))
    [('moe', 40), ('larry', 50), ('curly', 60)]
    >>> # get items from sequences like lists, tuples, etc...
    >>> stooge = [['moe', 40], ['larry', 50], ['curly', 60]]
    >>> list(xitems(stooge, 0))
    ['moe', 'larry', 'curly']
    >>> list(xitems(stooge, 1))
    [40, 50, 60]
    >>> list(xitems(stooge, 'place'))
    []
    '''
    def itemz(iterable, _n=next):
        try:
            get = itemgetter(*keys)
            while 1:
                try:
                    yield get(_n(iterable))
                except (IndexError, KeyError, TypeError):
                    pass
        except StopIteration:
            pass
    return itemz(iter(iterable))

def xtraverse(iterable, func, invert=False):
    '''
    Collect values from deeply :term:`nested scope`\s from items in `iterable`
    matched by `func`.

    :argument iterable: iterable object

    :keyword bool invert: collect items in `iterable` that `func` is
      :data:`False` rather than :data:`True` for

    :returns: :term:`sequence` of `ChainMaps <http://docs.python.org/dev/
      library/collections.html#collections.ChainMap>`_ containing
      :class:`collections.OrderedDict`

    :rtype: :obj:`blade` :term:`object`

    >>> class stooge:
    ...    name = 'moe'
    ...    age = 40
    >>> class stooge2:
    ...    name = 'larry'
    ...    age = 50
    >>> class stooge3:
    ...    name = 'curly'
    ...    age = 60
    ...    class stooge4(object):
    ...        name = 'beastly'
    ...        age = 969
    >>> def test(x):
    ...    if x[0] == 'name':
    ...        return True
    ...    elif x[0].startswith('__'):
    ...        return True
    ...    return False
    >>> # using func while filtering for False values
    >>> list(xtraverse([stooge, stooge2, stooge3], test, invert=True))
    ... # doctest: +NORMALIZE_WHITESPACE
    [ChainMap(OrderedDict([('classname', 'stooge'), ('age', 40)])),
    ChainMap(OrderedDict([('classname', 'stooge2'), ('age', 50)])),
    ChainMap(OrderedDict([('classname', 'stooge3'), ('age', 60)]),
    OrderedDict([('age', 969), ('classname', 'stooge4')]))]
    '''
    ifilter = filterfalse if invert else filter
    def members(iterable):  # @IgnorePep8
        mro = getmro(iterable)
        names = iter(dir(iterable))
        beenthere = set()
        adder = beenthere.add
        try:
            OD = OrderedDict
            vz = vars
            cn = chain
            ga = getattr
            ic = isclass
            nx = next
            while 1:
                name = nx(names)
                # yes, it's really supposed to be a tuple
                for base in cn([iterable], mro):
                    var = vz(base)
                    if name in var:
                        obj = var[name]
                        break
                else:
                    obj = ga(iterable, name)
                if (name, obj) in beenthere:
                    continue
                else:
                    adder((name, obj))
                if ic(obj):
                    yield name, OD((k, v) for k, v in ifilter(
                        func, members(obj),
                    ))
                else:
                    yield name, obj
        except StopIteration:
            pass
    def traverse(iterable):  # @IgnorePep8
        try:
            iterable = iter(iterable)
            OD = OrderedDict
            sn = selfname
            nx = next
            while 1:
                iterator = nx(iterable)
                chaining = ChainMap()
                chaining['classname'] = sn(iterator)
                cappend = chaining.maps.append
                for k, v in ifilter(func, members(iterator)):
                    if isinstance(v, OD):
                        v['classname'] = k
                        cappend(v)
                    else:
                        chaining[k] = v
                yield chaining
        except StopIteration:
            pass
    return traverse(iterable)

def xmembers(iterable, func, inverse=False):
    '''
    Collect values from shallowly from classes or objects matched by `func`.

    :argument iterable: iterable object
    :keyword bool invert: collect items in `iterable` that `func` is
      :data:`False` rather than :data:`True` for

    :returns: :term:`sequence` of :func:`tuple` of keys and value
    '''
    return xfilter(xmerge(xmap(members, iterable)), func, inverse)

def xmro(iterable):
    return xmerge(xmap(getmro, iterable))

################################################################################
## BLADE REDUCING OPERATIONS ###################################################
################################################################################

def xflatten(iterable):
    '''
    Reduce nested items in `iterable` to flattened items in `iterable`.

    :argument iterable: iterable object

    >>> list(xflatten([[1, [2], [3, [[4]]]], 'here']))
    [1, 2, 3, 4, 'here']
    '''
    def flatten(iterable, _n=next, _is=isstring):
        next_ = iter(iterable)
        try:
            while 1:
                item = _n(next_)
                try:
                    # don't recur over strings
                    if _is(item):
                        yield item
                    else:
                        # do recur over other things
                        for j in flatten(item):
                            yield j
                except (AttributeError, TypeError):
                    # does not recur
                    yield item
        except StopIteration:
            pass
    return flatten(iterable)

def xreduce(iterable, func, initial=None, reverse=False):
    '''
    Reduce `iterable` items in `iterable` down to one items in `iterable` using
    `func`.

    :argument iterable: iterable object

    :keyword initial: starting value

    :keyword bool reverse: reduce from `the right side <http://www.zvon.org/
      other/haskell/Outputprelude/foldr_f.html>`_ of items in `iterable`

    >>> # reduce from left side
    >>> xreduce([1, 2, 3], lambda x, y: x + y)
    6
    >>> # reduce from left side with initial value
    >>> xreduce([1, 2, 3]. lambda x, y: x + y, initial=1)
    7
    >>> # reduce from right side
    >>> xreduce([[0, 1], [2, 3], [4, 5]], lambda x, y: x + y, reverse=True)
    [4, 5, 2, 3, 0, 1]
    >>> # reduce from right side with initial value
    >>>  xreduce(
    ... [[0, 1], [2, 3], [4, 5]], lambda x, y: x + y, [0, 0], reverse=True
    ... )
    [4, 5, 2, 3, 0, 1, 0, 0]
    '''
    if reverse:
        if initial is None:
            return reduce(partial(lambda f, x, y: f(y, x), func), iterable)
        return reduce(partial(lambda f, x, y: f(y, x), func), iterable, initial)
    if initial is None:
        return reduce(func, iterable)
    return reduce(func, iterable, initial)

################################################################################
## BLADE SLICING OPERATIONS ####################################################
################################################################################

def xat(iterable, n, default=None):
    '''
    :term:`Slice` off items in `iterable` found at index `n`.

    :argument iterable: iterable object
    :argument int n: index of some items in `iterable`
    :keyword default: default returned if nothing is found at `n`

    >>> # default behavior
    >>> xat([5, 4, 3, 2, 1], 2)
    3
    >>> # return default value if nothing found at index
    >>> xat([5, 4, 3, 2, 1], 10, 11)
    11
    '''
    return next(islice(iterable, n, None), default)

def xchoice(iterable):
    '''
    Randomly :term:`slice` off **one** items in `iterable`.

    :argument iterable: iterable object

    >>> list(xchoice([1, 2, 3, 4, 5, 6])) # doctest: +SKIP
    3
    '''
    i1, i2 = tee(iterable)
    return xat(i1, randrange(0, count(i2)))

def xdice(iterable, n, fill=None):
    '''
    :term:`Slice` one `iterable` items in `iterable` into `n` iterable items in
    `iterable`.

    :argument iterable: iterable object
    :argument int n: number of items in `iterable` per slice
    :keyword fill: value to pad out incomplete iterables

    >>> list(xdice(['moe', 'larry', 'curly', 30, 40, 50, True], 2, 'x'))
    [('moe', 'larry'), ('curly', 30), (40, 50), (True, 'x')]
    '''
    return zip_longest(fillvalue=fill, *[iter(iterable)] * n)

def xfirst(iterable, n=0):
    '''
    :term:`Slice`  off `n` things from the **starting** end of `iterable` or
    just the **first** items in `iterable`.

    :argument iterable: iterable object
    :keyword int n: number of items in `iterable`

    >>> # default behavior
    >>> list(xfirst([5, 4, 3, 2, 1]))
    5
    >>> # first things from index 0 to 2
    >>> list(xfirst([5, 4, 3, 2, 1], 2))
    [5, 4]
    '''
    return islice(iterable, n) if n else deferiter(iter(iterable))

def xinitial(iterable):
    '''
    :term:`Slice` off every items in `iterable` except the **last** `iterable`.

    :argument iterable: iterable object

    >>> list(xinitial([5, 4, 3, 2, 1]))
    [5, 4, 3, 2]
    '''
    i1, i2 = tee(iterable)
    return islice(i1, count(i2) - 1)

def xlast(iterable, n=0):
    '''
    :term:`Slice` off `n` things from the **tail** end of items in `iterable` or
    just the **last** items in `iterable`.

    :argument iterable: iterable object
    :keyword int n: number of items in `iterable` to slice off

    >>> # default behavior
    >>> list(xlast([5, 4, 3, 2, 1]))[0]
    1
    >>> # fetch last two things
    >>> list(xlast([5, 4, 3, 2, 1], 2))
    [2, 1]
    '''
    if n:
        i1, i2 = tee(iterable)
        return islice(i1, count(i2) - n, None)
    return iter(deferfunc(deque(iterable, maxlen=1).pop))

def xrest(iterable):
    '''
    :term:`Slice` off every items in `iterable` except the **first** item.

    :argument iterable: iterable object

    >>> list(xrest([5, 4, 3, 2, 1]))
    [4, 3, 2, 1]
    '''
    return islice(iterable, 1, None)

def xsample(iterable, n):
    '''
    Randomly :term:`slice` off `n` items in `iterable`.

    :argument iterable: iterable object
    :argument int n: sample size

    >>> list(xsample([1, 2, 3, 4, 5, 6], 3)) # doctest: +SKIP
    [2, 4, 5]
    '''
    i1, i2 = tee(iterable)
    return partmap(
        lambda i, r, c, x: i(x, r(0, c)),
        tee(i2, n),
        islice,
        randrange,
        count(i1),
    )

def xslice(iterable, start, stop=None, step=None):
    '''
    Take :term:`slice` out of items in `iterable`.

    :argument iterable: iterable object
    :argument int start: starting index of slice
    :keyword int stop: stopping index of slice
    :keyword int step: size of step in slice

    >>> # slice from index 0 to 3
    >>> list(xslice([5, 4, 3, 2, 1], 2))
    [5, 4]
    >>> # slice from index 2 to 4
    >>> list(xslice([5, 4, 3, 2, 1], 2, 4))
    [3, 2]
    >>> # slice from index 2 to 4 with 2 steps
    >>> list(xslice([5, 4, 3, 2, 1], 2, 4, 2))
    3
    '''
    if stop is not None and step is not None:
        return islice(iterable, start, stop, step)
    elif stop is not None:
        return islice(iterable, start, stop)
    return islice(iterable, start)
