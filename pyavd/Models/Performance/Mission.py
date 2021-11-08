from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg

from .Segments.Segment import Segment


class Mission(Model):
    """A sequence of flight segments

    Upper Unbounded
    ---------------
    

    Lower Unbounded
    ---------------
    aircraft.W
    """
    def setup(self, aircraft):
        self.aircraft = aircraft

        with Vectorize(4):  # four flight segments
            self.fs = Segment(aircraft)

        Wburn = self.fs.aircraftp.Wburn
        Wfuel = self.fs.aircraftp.Wfuel
        self.takeoff_fuel = Wfuel[0]

        return {
            "definition of Wburn":
                Wfuel[:-1] >= Wfuel[1:] + Wburn[:-1],
            "require fuel for the last leg":
                Wfuel[-1] >= Wburn[-1],
            "flight segment":
                self.fs}