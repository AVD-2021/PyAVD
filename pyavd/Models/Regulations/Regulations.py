from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


class Regulations(Model):
    """FAR25 airworthiness regualtions - for commercial transport aircraft 

    Variables
    ---------------
    h_obs_takeoff   35         [ft]           FAR25 AIR 6.3   
    h_obs_land      50         [ft]           FAR25 AIR 7.2
    """
    def setup(self, aircraft):

        # All operational constraints go here - returned at end


        return []