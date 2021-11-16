from gpkit import Model, Vectorize, VectorVariable, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np

from .Segments import *


class Mission(Model):
    """A sequence of flight segments according to Target Mission Profile

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft=None):
        self.aircraft = aircraft
        mission = self.mission = []

        # with Vectorize(4):  # four flight segments
        #     self.fs = Segment(aircraft)
        
        mission += Takeoff(aircraft)
        mission += Climb(aircraft)

        return {"flight segment": mission}