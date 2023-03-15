
import math
import lambdas

import numeric_types
import lego_blocks.forms as forms
from lambdas import types


class Estrin(types.Transform):

    def __init__(self, in_node: types.Node, split=0):
        """
        Takes a polynomial and implements it using estrin form

        in_node: A polynomial
        """
        super().__init__(in_node)
        self.domain = self.in_node.domain
        self.split = split

    def type_check(self):
        """ Check that the input is a polynomial """
        self.in_node.type_check()
        our_in_type = self.in_node.out_type

        # TODO: turn into an exception
        assert type(our_in_type) == types.Poly

        self.out_type = types.Impl(our_in_type.function, our_in_type.domain)

    def generate(self):
        """ Implement a polynomial using the estrin form lego block """
        p = super().generate()
        in_name = self.gensym("in")
        out_name = self.gensym("out")
        return [forms.Estrin(numeric_types.fp64(), [in_name], [out_name], p, self.split)]

    @classmethod
    def generate_hole(cls, out_type):
        # We only output
        # (Impl (func) low high)
        if (type(out_type) != types.Impl
            or not math.isfinite(float(out_type.domain.inf))
                or not math.isfinite(float(out_type.domain.sup))):
            return list()

        # To get this output we need as input
        # (Poly (func) low high)
        in_type = types.Poly(out_type.function,
                             out_type.domain)
        return [Estrin(lambdas.Hole(in_type)), ]
