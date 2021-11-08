from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg


# TODO: Numbers need changing
class WingAero(Model):      
    """Wing aerodynamics model

    Variables
    ---------
    CD      [-]    drag coefficient
    CL      [-]    lift coefficient
    e   0.9 [-]    Oswald efficiency
    Re      [-]    Reynold's number
    D       [N]    drag force

    Upper Unbounded
    ---------------
    D, Re

    Lower Unbounded
    ---------------
    CL
    """
    @parse_variables(__doc__, globals())
    def setup(self, wing, state):
        self.wing = wing
        self.state = state

        c = wing.c
        A = wing.A
        S = wing.S
        rho = state.rho
        V = state.V
        mu = state.mu

        # Ignore linting errors - the decorator on Line 26 will handle these
        return [D >= 0.5*rho*V**2*CD*S,
                Re == rho*V*c/mu,
                CD >= 0.074/Re**0.2 + CL**2/np.pi/A/e]


# Wing model - define wing parameters in the docstring for auto-import
class Wing(Model):
    """Aircraft wing model

    Variables
    ---------
    W        [kg]       weight
    S        [m^2]      surface area
    A     15 [-]        aspect ratio
    c        [m]        mean chord

    Upper Unbounded
    ---------------
    W

    Lower Unbounded
    ---------------
    c, S
    """
    @parse_variables(__doc__, globals())
    def setup(self):
        # Define some constraints in terms of the variables created - use Tight() if actually an equality, but still use >=
        return []

    # Wing dynamic performance handled in WingAero() - will instantiate as dynamic
    dynamic = WingAero