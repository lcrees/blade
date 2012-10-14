# -*- coding: utf-8 -*-
'''ordering test mixins'''

import platform

PYPY = platform.python_implementation() == 'PyPy'

from stuf.six import unittest


class stooges: #@IgnorePep8
    name = 'moe'
    age = 40
class stoog2: #@IgnorePep8
    name = 'larry'
    age = 50
class stoog3: #@IgnorePep8
    name = 'curly'
    age = 60
    class stoog4: #@IgnorePep8
        name = 'beastly'
        age = 969


class stooge: #@IgnorePep8
    name = 'moe'
    age = 40
class stooge2(stooge): #@IgnorePep8
    pname = 'larry'
    page = 50
class stooge3(stoog2): #@IgnorePep8
    aname = 'curly'
    rage = 60
    class stooge4(stooge): #@IgnorePep8
        kname = 'beastly'
        mage = 969


class TestXMath(unittest.TestCase):

    def test_xaverage(self):
        from blade.core import xaverage
        self.assertEqual(xaverage((10, 40, 45)), 31.666666666666668)

    def test_xcount(self):
        from blade.core import xcount
        common = xcount((11, 3, 5, 11, 7, 3, 11))
        self.assertEqual(common.overall, [(11, 3), (3, 2), (5, 1), (7, 1)])
        # most common
        self.assertEqual(common.most, 11)
        # least common
        self.assertEqual(common.least, 7)

    def test_xmedian(self):
        from blade.core import xmedian
        self.assertEqual(xmedian((4, 5, 7, 2, 1)), 4)
        self.assertEqual(xmedian((4, 5, 7, 2, 1, 8)), 4.5)

    def test_xminmax(self):
        from blade.core import xminmax
        self.assertEqual(xminmax((1, 2, 4)), (1, 4))
        self.assertEqual(xminmax((10, 5, 100, 2, 1000)), (2, 1000))

    def test_xinterval(self):
        from blade.core import xinterval
        self.assertEqual(xinterval((3, 5, 7, 3, 11)), 8)

    def test_xsum(self):
        from blade.core import xsum
        self.assertEqual(xsum((1, 2, 3)), 6)
        self.assertEqual(xsum((1, 2, 3), 1), 7)
        self.assertEqual(
            xsum((.1, .1, .1, .1, .1, .1, .1, .1, .1, .1), precision=True), 1.0,
        )


class TestXCmp(unittest.TestCase):

    def test_xall(self):
        from blade.core import xall
        self.assertFalse(xall([True, 1, None, 'yes'], bool))
        self.assertTrue(xall([2, 4, 6, 8], lambda x: x % 2 == 0))

    def test_xany(self):
        from blade.core import xany
        self.assertTrue(xany([None, 0, 'yes', False], bool))
        self.assertTrue(xany([1, 4, 5, 9], lambda x: x % 2 == 0))

    def test_xdiff(self):
        from blade.core import xdiff
        self.assertEqual(
            xdiff(([1, 2, 3, 4, 5], [5, 2, 10], [10, 11, 2])), set([1, 3, 4]),
        )
        self.assertEqual(
            xdiff(([1, 3, 4, 5], [5, 2, 10], [10, 11, 2]), True),
            set([3, 1, 11, 4] if PYPY else [1, 3, 4, 11]),
        )

    def test_xintersect(self):
        from blade.core import xintersect
        self.assertEqual(
            xintersect(([1, 2, 3], [101, 2, 1, 10], [2, 1])), set([1, 2]),
        )

    def test_xunion(self):
        from blade.core import xunion
        self.assertEqual(
            xunion(([1, 2, 3], [101, 2, 1, 10], [2, 1])),
            set([10, 1, 2, 3, 101] if PYPY else [1, 10, 3, 2, 101]),
        )

    def test_xunique(self):
        from blade.core import xunique
        self.assertEqual(
            list(xunique([1, 2, 1, 3, 1, 4])), [1, 2, 3, 4]
        )
        self.assertEqual(
            list(xunique([1, 2, 1, 3, 1, 4], round)), [1, 2, 3, 4],
        )


class TestOrder(unittest.TestCase):

    def test_xshuffle(self):
        from blade.core import xshuffle
        self.assertEqual(
            len(xshuffle((1, 2, 3, 4, 5, 6))), len([5, 4, 6, 3, 1, 2]),
        )

    def test_xgroup(self,):
        from blade.core import xgroup
        self.assertEqual(
            list(xgroup([1.3, 2.1, 2.4])),
            [(1.3, (1.3,)), (2.1, (2.1,)), (2.4, (2.4,))],
        )
        from math import floor
        self.assertEqual(
            list(xgroup([1.3, 2.1, 2.4], floor)),
            [(1.0, (1.3,)), (2.0, (2.1, 2.4))]
        )


class TextXFilter(unittest.TestCase):

    def test_xtraverse(self):
        self.maxDiff = None
        from blade.core import xtraverse
        from stuf.collects import ChainMap, OrderedDict
        test = lambda x: not x[0].startswith('__')
        self.assertEqual(
            list(xtraverse([stoog3], test))[0],
            ChainMap(OrderedDict([
                ('classname', 'stoog3'), ('age', 60), ('name', 'curly')]),
                OrderedDict([
                ('age', 969), ('name', 'beastly'), ('classname', 'stoog4')]))
        )
        self.assertEqual(
            list(xtraverse([stooge, stooge2, stooge3], test)),
            [ChainMap(OrderedDict([
                ('classname', 'stooge'), ('age', 40), ('name', 'moe')])),
            ChainMap(
                OrderedDict([
                    ('classname', 'stooge'), ('age', 40), ('name', 'moe'),
                    ('classname', 'stooge2'), ('page', 50), ('pname', 'larry')
                ])
            ),
            ChainMap(OrderedDict([
                ('classname', 'stooge3'), ('age', 50), ('aname', 'curly'),
                ('name', 'larry'), ('rage', 60)]), OrderedDict([('age', 40),
                ('kname', 'beastly'), ('mage', 969), ('name', 'moe'),
                ('classname', 'stooge4')]))
        ])
        def test(x): #@IgnorePep8
            if x[0] == 'name':
                return True
            elif x[0].startswith('__'):
                return True
            return False
        self.assertEqual(
            list(xtraverse([stooges, stoog2, stoog3], test, True)),
            [ChainMap(OrderedDict([('classname', 'stooges'), ('age', 40)])),
            ChainMap(OrderedDict([('classname', 'stoog2'), ('age', 50)])),
            ChainMap(
                OrderedDict([('classname', 'stoog3'), ('age', 60)]),
                OrderedDict([('classname', 'stoog4'), ('age', 969)])
            )],
        )

    def test_xattrs(self):
        from stuf import stuf
        from blade.core import xattrs
        stooge = [
            stuf(name='moe', age=40),
            stuf(name='larry', age=50),
            stuf(name='curly', age=60)
        ]
        self.assertEqual(
            list(xattrs(stooge, 'name')), ['moe', 'larry', 'curly']
        )
        self.assertEqual(
            list(xattrs(stooge, 'name', 'age')),
            [('moe', 40), ('larry', 50), ('curly', 60)],
        )
        self.assertEqual(list(xattrs(stooge, 'place')), [])

    def test_xitems(self):
        from blade.core import xitems
        stooge = [
            dict(name='moe', age=40),
            dict(name='larry', age=50),
            dict(name='curly', age=60),
        ]
        self.assertEqual(
            list(xitems(stooge, 'name')), ['moe', 'larry', 'curly'],
        )
        self.assertEqual(
            list(xitems(stooge, 'name', 'age')),
            [('moe', 40), ('larry', 50), ('curly', 60)],
        )
        stooge = [['moe', 40], ['larry', 50], ['curly', 60]]
        self.assertEqual(list(xitems(stooge, 0)), ['moe', 'larry', 'curly'])
        self.assertEqual(list(xitems(stooge, 1)), [40, 50, 60])
        self.assertEqual(list(xitems(stooge, 'place')), [])

    def test_xfilter(self):
        from blade.core import xfilter
        self.assertEqual(
            list(xfilter(
                [1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0, invert=True
            )),
            [1, 3, 5]
        )
        self.assertEqual(
            list(xfilter([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)), [2, 4, 6]
        )

    def test_xtruefalse(self):
        from blade.core import xtruefalse
        self.assertEqual(
            tuple(xtruefalse([1, 2, 3, 4, 5, 6], lambda x: x % 2 == 0)),
            ((2, 4, 6), (1, 3, 5))
        )

    def test_xmembers(self):
        from blade.core import xmembers
        self.assertEqual(
            list(xmembers([stoog3], lambda x: not x[0].startswith('__'))),
            [('age', 60), ('name', 'curly'), ('stoog4', stoog3.stoog4)],
        )

    def test_xmro(self):
        from blade.core import xmro
        results = xmro([stooge3])
        self.assertIn(stooge3, results)
        self.assertIn(stoog2, results)


class TestXSlice(unittest.TestCase):

    def test_xdice(self):
        from blade.core import xdice
        self.assertEqual(
            list(xdice(('moe', 'larry', 'curly', 30, 40, 50, True), 2, 'x')),
            [('moe', 'larry'), ('curly', 30), (40, 50), (True, 'x')]
        )

    def test_xfirst(self):
        from blade.core import xfirst
        self.assertEqual(list(xfirst([5, 4, 3, 2, 1])), [5])
        self.assertEqual(list(xfirst([5, 4, 3, 2, 1], 2)), [5, 4])

    def test_xat(self):
        from blade.core import xat
        self.assertEqual(xat((5, 4, 3, 2, 1), 2), 3)
        self.assertEqual(xat((5, 4, 3, 2, 1), 10, 11), 11)

    def test_xslice(self):
        from blade.core import xslice
        self.assertEqual(list(xslice((5, 4, 3, 2, 1), 2)), [5, 4])
        self.assertEqual(list(xslice((5, 4, 3, 2, 1), 2, 4)), [3, 2])
        self.assertEqual(list(xslice((5, 4, 3, 2, 1), 2, 4, 2)), [3])

    def test_xlast(self):
        from blade.core import xlast
        self.assertEqual(list(xlast((5, 4, 3, 2, 1))), [1])
        self.assertEqual(list(xlast((5, 4, 3, 2, 1), 2)), [2, 1])

    def test_xinitial(self):
        from blade.core import xinitial
        self.assertEqual(list(xinitial([5, 4, 3, 2, 1])), [5, 4, 3, 2])

    def test_xrest(self):
        from blade.core import xrest
        self.assertEqual(list(xrest([5, 4, 3, 2, 1])), [4, 3, 2, 1])

    def test_xchoice(self):
        from blade.core import xchoice
        self.assertEqual(len([xchoice([1, 2, 3, 4, 5, 6])]), 1)

    def test_xsample(self):
        from blade.core import xsample
        self.assertEqual(len(list(xsample([1, 2, 3, 4, 5, 6], 3))), 3)


class TestXReduce(unittest.TestCase):

    def test_xflatten(self):
        from blade.core import xflatten
        self.assertEqual(
            list(xflatten([[[1, [2], [3, [[4]]]], 'here']])),
            [1, 2, 3, 4, 'here'],
        )

    def test_xreduce(self):
        from blade.core import xreduce
        self.assertEqual(xreduce((1, 2, 3), lambda x, y: x + y), 6)
        self.assertEqual(xreduce((1, 2, 3), lambda x, y: x + y, 1), 7)
        self.assertEqual(
            xreduce(([0, 1], [2, 3], [4, 5]), lambda x, y: x + y, reverse=True),
            [4, 5, 2, 3, 0, 1],
        )
        self.assertEqual(
            xreduce([[0, 1], [2, 3], [4, 5]], lambda x, y: x + y, [0, 0], True),
            [4, 5, 2, 3, 0, 1, 0, 0],
        )


class TestXRepeat(unittest.TestCase):

    def test_xrepeat(self):
        from blade.core import xrepeat
        test = lambda *args: list(args)
        self.assertEqual(
            list(xrepeat([40, 50, 60], 3)),
            [(40, 50, 60), (40, 50, 60), (40, 50, 60)],
        )
        self.assertEqual(
            list(xrepeat((40, 50, 60), 3, test)),
            [[40, 50, 60], [40, 50, 60], [40, 50, 60]],
        )

    def test_xcopy(self):
        from blade.core import xcopy
        testlist = [[1, [2, 3]], [4, [5, 6]]]
        newlist = list(xcopy(testlist))
        self.assertFalse(newlist is testlist)
        self.assertListEqual(newlist, testlist)
        self.assertFalse(newlist[0] is testlist[0])
        self.assertListEqual(newlist[0], testlist[0])
        self.assertFalse(newlist[1] is testlist[1])
        self.assertListEqual(newlist[1], testlist[1])


class TestXMap(unittest.TestCase):

    def test_xkwargmap(self):
        from blade.core import xkwargmap
        test = lambda *args, **kw: sum(args) * sum(kw.values())
        self.assertEqual(
            list(xkwargmap(
                [((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})],
                test,
            )),
            [6, 10, 14],
        )
        self.assertEqual(
            list(xkwargmap(
                [((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})],
                test,
                True,
                1, 2, 3, b=5, w=10, y=13
            )),
            [270, 330, 390],
        )
        self.assertEqual(
            list(xkwargmap(
                (((1, 2), {'a': 2}), ((2, 3), {'a': 2}), ((3, 4), {'a': 2})),
                test,
                False,
                1, 2, 3,
                b=5, w=10, y=13,
            )),
            [6, 10, 14],
        )

    def test_xargmap(self):
        from blade.core import xargmap
        self.assertEqual(
            list(xargmap(
                [(1, 2), (2, 3), (3, 4)], lambda x, y: x * y,
            )),
            [2, 6, 12],
        )
        self.assertEqual(
            list(xargmap(
                [(1, 2), (2, 3), (3, 4)],
                lambda x, y, z, a, b: x * y * z * a * b,
                True,
                7, 8, 9
            )),
            [1008, 3024, 6048],
        )
        self.assertEqual(
            list(xargmap(
                [(1, 2), (2, 3), (3, 4)],
                lambda x, y, z, a, b: x * y * z * a * b,
                True,
                7, 8, 9
            )),
            [1008, 3024, 6048],
        )

    def test_xinvoke(self):
        from blade.core import xinvoke
        self.assertEqual(
            list(xinvoke([[5, 1, 7], [3, 2, 1]], 'index', 1)), [1, 2],
        )
        self.assertEqual(
            list(xinvoke([[5, 1, 7], [3, 2, 1]], 'sort')),
            [[1, 5, 7], [1, 2, 3]],
        )

    def test_xkeyvalue(self):
        from blade.core import xkeyvalue
        self.assertEqual(
            list(xkeyvalue(
            [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
            keys=True
            )), [1, 2, 3, 1, 2, 3],
        )
        self.assertEqual(
            list(xkeyvalue(
                [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
                values=True
            )),
            [2, 3, 4, 2, 3, 4],
        )
        self.assertEqual(
            list(xkeyvalue(
            [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])],
            lambda x, y: x * y,
            )),
            [2, 6, 12, 2, 6, 12],
        )
        self.assertEqual(
            dict(xkeyvalue(
                [dict([(1, 2), (2, 3), (3, 4)]), dict([(1, 2), (2, 3), (3, 4)])]
            )),
            dict([(1, 2), (2, 3), (3, 4)]),
        )
