
from calculate_cody_waite_constants import calculate_cody_waite_constants
import lego_blocks
import fpcore


class CodyWaite(lego_blocks.LegoBlock):

    def __init__(self, numeric_type, in_names, out_names,
                 period, bits_per, entries,
                 gensym):
        super().__init__(numeric_type, in_names, out_names)
        assert (len(self.in_names) == 1)
        assert (len(self.out_names) == 2)
        self.period = period
        self.bits_per = bits_per
        self.entries = entries
        self.gensym = gensym

    def to_c(self):
        cdecl = self.numeric_type.c_type()

        cw_in = self.in_names[0]
        r = self.out_names[0]
        k = self.out_names[1]
        inv_period = self.gensym("inv_period")
        period = self.gensym("period")

        period_strs = calculate_cody_waite_constants(self.period,
                                                     self.bits_per,
                                                     self.entries)
        period_str = ",".join(period_strs)

        source_lines = [
            f"{cdecl} {inv_period} = {1/float(self.period)};",
            f"{cdecl} {period}[{len(period_strs)}] = {{{period_str}}};",
            f"int {k};",
            f"{cdecl} {r} = cody_waite_reduce({cw_in}, {inv_period}, {len(period_strs)}, {period}, &{k}, NULL);",
        ]

        return source_lines