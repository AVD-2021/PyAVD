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
        mission = self.mission = {}
        
        # TODO: link to Streamlit frontend - session_state.mission_profile
        mission.update({"Takeoff": Takeoff(aircraft)})
        mission.update({"Climb": Climb(0.04, 0.05, 0.1, aircraft=aircraft, goAround=False)})


        return mission