from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np

from .Segments import Segment


class Mission(Model):
    """A sequence of flight segments

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft):
        self.aircraft = aircraft

        with Vectorize(4):  # four flight segments
            self.fs = Segment(aircraft)



        return {"flight segment":self.fs}