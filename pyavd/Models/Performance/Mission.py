from gpkit import Model, Vectorize, VectorVariable, constraints, parse_variables, ureg as u
from gpkit.constraints.tight import Tight
import numpy as np
from functools import reduce

from .Segments import *


class Mission(Model):
    """A sequence of flight segments according to Target Mission Profile

    Variables
    ---------

    """
    @parse_variables(__doc__, globals())
    def setup(self, aircraft=None):
        self.aircraft   = aircraft
        constraints     = self.constraints   = []
        mission         = self.mission       = []
        
        # TODO: link to Streamlit frontend - session_state.mission_profile
        takeoff = self.takeoff  = Takeoff(aircraft=aircraft) 
        climb   = self.climb    = Climb(0.04, 0.05, 0.1, aircraft=aircraft)
        cruise  = self.cruise   = Cruise(aircraft=aircraft)
        # descent = self.descent  = Descent(aircraft=aircraft)
        climb2  = self.climb2   = Climb_GoAround(0.04, 0.05, 0.1, aircraft=aircraft)
        cruise2 = self.cruise2  = Cruise(aircraft=aircraft)
        # loiter  = self.loiter   = Loiter(aircraft=aircraft)
        landing = self.landing  = Landing(aircraft=aircraft)

        mission += [takeoff, climb, cruise, climb2, cruise2, landing]

        # Aggregate fuel fraction
        aggregate = reduce(lambda x, y: x * y, [fs.fuel_frac for fs in mission])
        constraints += [aircraft.M_fuel/aircraft.M_0 == 1.01 * (1 - aggregate)]

        return constraints, mission
