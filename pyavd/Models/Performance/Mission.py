from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg

from .Segments import Segment


class Mission(Model):
    """A sequence of flight segments

    """
    def setup(self, aircraft):
        self.aircraft = aircraft

        with Vectorize(4):  # four flight segments
            self.fs = Segment(aircraft)


        return {
            "definition of Wburn":
                Wfuel[:-1] >= Wfuel[1:] + Wburn[:-1],
            "require fuel for the last leg":
                Wfuel[-1] >= Wburn[-1],
            "flight segment":
                self.fs}