

import math
import fpcore
import mpmath

from utils.logging import Logger


logger = Logger(level=Logger.EXTRA)


def parse_bound(something):
    wrapped = "(FPCore () {})".format(something)
    fpc = fpcore.parse(wrapped)[0]
    return fpc.simplify().body


class Interval():

    def __init__(self, inf, sup):
        self.inf = parse_bound(inf)
        self.sup = parse_bound(sup)

        ie = self.inf.eval({})
        if math.isfinite(float(ie)) and int(ie) == ie:
            self.inf = parse_bound(int(ie))

        se = self.sup.eval({})
        if math.isfinite(float(se)) and int(se) == se:
            self.sup = parse_bound(int(se))

        assert (float(self.inf) <= float(self.sup))

    def __str__(self):
        return "[{},{}]".format(self.inf, self.sup)

    def __repr__(self):
        return 'Interval("{}", "{}")'.format(self.inf, self.sup)

    def __abs__(self):
        #                 0
        # <---------------+--------------->
        #                    [********]
        if float(self.inf) >= 0.0:
            return Interval(self.inf, self.sup)
        #                 0
        # <---------------+--------------->
        #               [********]
        if float(self.inf) <= 0.0 and 0.0 <= float(self.sup):
            abs_max = max(-self.inf, self.sup)
            return Interval(0.0, abs_max)
        #                 0
        # <---------------+--------------->
        #      [********]
        if float(self.sup) <= 0.0:
            return Interval(-self.sup, -self.sup)

        assert 0, "Unreachable"

    def __getitem__(self, items):
        if items == 0:
            return self.inf
        if items == 1:
            return self.sup
        raise IndexError(items)

    def width(self):
        return self.sup - self.inf

    def contains(self, point):
        logger.log("Testing if {} is in [{}, {}]", point, self.inf, self.sup)
        if type(point) == mpmath.iv.mpf:
            inf = str(self.inf).replace("INFINITY", "inf")
            sup = str(self.sup).replace("INFINITY", "inf")
            me = mpmath.iv.mpf([inf, sup])
            return point in me
        f_point = float(point)
        return float(self.inf) <= f_point and f_point <= float(self.sup)

    def shift(self, k):
        diff = self.sup - self.inf
        shift_by = k*diff
        return Interval(self.inf+shift_by, self.sup+shift_by)

    def split(self, p):
        return self.aligned_split(p, self.inf)

    def aligned_split(self, p, edge):
        assert (0.0 < p)
        assert (self.inf <= edge and edge <= self.sup)

        inf = self.inf
        lower = edge - self.inf
        k = math.floor(lower/p)
        sup = edge - k*p
        sup = min(sup, self.sup)
        assert (0.0 <= sup-inf and sup-inf <= p)
        periods = list()
        if sup-inf != 0:
            periods.append(Interval(inf, sup))

        start = sup
        i = 0
        while sup < self.sup:
            inf = start + i*p
            sup = start + (i+1)*p
            sup = min(sup, self.sup)
            assert (self.inf <= inf and sup <= self.sup)
            periods.append(Interval(inf, sup))

        return periods
