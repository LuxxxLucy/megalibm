
import math
from fpcore.ast import Variable
from lambdas.narrow import Narrow
import lego_blocks
import numeric_types
import lambdas

import fpcore

from dirty_equal import dirty_equal

from interval import Interval
from lambdas import types
from sympy_based_equal import sympy_based_equal
from utils import Logger

class TransformOut(types.Transform):

    def __init__(self,
                 in_node: types.Node,
                 expr: fpcore.ast.Expr):
        super().__init__(in_node)
        self.expr = expr

    def __str__(self):
        inner = str(self.in_node)
        return f"(TransformOut {self.reduction} {self.reconstruction} {inner})"

    def replace_lambda(self, search, replace):
        if self == search:
            return replace
        new_in_node = self.in_node.replace_lambda(search, replace)
        return self.__class__(new_in_node, self.reduction, self.reconstruction)

    def type_check(self):
        # Make sure the impl we are using can type check
        self.in_node.type_check()
        inner_impl_type = self.in_node.out_type
        f = inner_impl_type.function
        domain = inner_impl_type.domain

        # TODO: add this to fpcore
        # assert self.expr.contains_variable("y")
        new_f = self.expr.substitute(Variable("y"), f.body)

        self.passed_check = True
        self.domain = domain
        self.out_type = types.Impl(new_f, self.domain)

    def generate(self):
        # in = ...
        # out = expr(in)

        so_far = super().generate()

        t_in = so_far[-1].out_names[0]
        t_out = self.gensym("t_out")

        rec = lego_blocks.TransformOut(
            numeric_types.fp64(),
            [t_in], [t_out],
            self.expr
        )

        return so_far + [rec]

