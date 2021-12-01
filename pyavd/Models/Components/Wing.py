from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u


# TODO: Numbers need changing
'''

    alpha_0         -1.8            [deg]       Zero-lift AoA

    U               state.U         [m/s]       Airspeed
    rho             state.rho       [kg/m^3]    Air density
    mu              state.mu        [kg/m/s]    Dynamic viscosity
    Re                              [-]         Reynold's number
'''

## ADD wing lift curve slop (CL_alpha), aerodynamic position (x_ac)
class WingAero(Model):      
    """Wing aerodynamics model

    Variables
    ---------
    M                               [kg]            Mass
    CD                              [-]             Drag coefficient
    CL                              [-]             Lift coefficient
    e               0.9             [-]             Oswald efficiency
    Re                              [-]             Reynolds number
    D                               [N]             Drag force
    CL_alpha_w      4.6265          [-]             Lift Curve Slope of Wing
    i_w                             [deg]           Wing Setting Angle
    x_cg                            [m]             x Center of Gravity location
    z_cg                            [m]             z Center of Gravity location

    """
    @parse_variables(__doc__, globals())
    def setup(self, wing, state):
        constraints     = self.constraints  = {}

        self.wing = wing
        self.state = state

        c       = wing.c
        AR      = wing.AR
        Sref    = wing.Sref
        rho     = state.rho
        U       = state.U
        mu      = state.mu

        # Aerodynamic properties
        print(f"rho:{rho}, U:{U}, c:{c}, mu:{mu}, Re:{rho * U * c / mu}")

        self.Re = rho * U * c / mu
        self.D  = 0.5 * rho * U**2 * Sref * CD
        self.CL = 0.5 * rho * U**2 * Sref * CL_alpha_w

        # constraints.update({"Reynolds": [Re >= rho * U * c / mu]})
        # constraints.update({"Drag": [D >= 0.5 * rho * U**2 * Sref * CD]})
        # constraints.update({"Lift": [CL >= 0.5 * rho * U**2 * Sref * CL_alpha_w]})

        return constraints


# Wing model - define wing parameters in the docstring for auto-import - note that undefined vars are free, otherwise fixed

### ADD wing sweep (lam) and taper ratio (gam) (from Stability)
class Wing(Model):
    """Aircraft wing model

    Variables
    ---------
    M                          [kg]          Mass
    Sref        22.0           [m^2]         Surface Area
    AR          3.5            [-]           Aspect Ratio
    c           1.83           [m]           Mean Chord
    b           13.0           [m]           Wing Semi-span
    sweep       9.1            [deg]         Wing Sweep
    taper       0.36           [-]           Wing Taper
    x_cg                       [m]           x Center of Gravity location
    z_cg                       [m]           z Center of Gravity location

    """
    @parse_variables(__doc__, globals())
    def setup(self):
        # Define some constraints in terms of the variables created - use Tight() if actually an equality, but still use >=

        return []

    # TODO: define sweep and taper

    # Wing dynamic performance handled in WingAero() - will alias as dynamic
    dynamic = WingAero



# Aliases - update: unused for now
class Starboard_Wing(Wing):
    def setup(self): return super().setup()


class Port_Wing(Wing):
    def setup(self): return super().setup()