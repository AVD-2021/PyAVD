from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np


class Stability(Model):
    """Stability model

    Variables
    ---------
    
    depsilon_dalpha                 [-]             Rate of Change of Downwash with AoA        
    fuse_Cm                         [-]             Pitching Moment Coefficient of Fuselage
    x_np                            [m]             Neutral Point Position
    x_cg                            [m]             Centre of Gravity - x-axis
    SM                              [-]             Static Margin - Kn

    """
    @parse_variables(__doc__, globals())
    def setup(self, wing):
        constraints = self.constraints  = []

        self.fuse = fuse
        self.wing = wing            # wing is the Wing() model

        # Implement later when I get OCD
        # Kn = SM
        K_f = self.Kf = Variable("K_f", "", "K_f")
        K_a = 1.0/wing.AR - 1.0/(1.0 + wing.AR**1.7)

        constraints.update({"Pitching Moment Coefficient Fuselage": 
            # taking Fuselage width to be the max width; c is c_bar
            fuse_Cm >= (K_f * self.components.fuselage.length * (self.components.fuselage.width**2) / (self.wing.c * self.wing.S))})
        
        constraints.update({"Rate of Change of Downwash with AoA: "})


        return [constraints]

    
    def __depsilon_dalpha(wing_ar, wing_taper_ratio, rel_tail_h, rel_tail_l, wing_span, wing_sweep, TBD):
        """calc_deta_dalpha [summary]
            Arguments:  wing aspect ratio [dimensionless], wing taper ratio [dimensionless],
                        relative height of the horizontal tailplane stabilizer to the wing [meters],
                        relative longitudinal distance between the wing and horizontal tailplane stabilizer [meters]
                        wing span [meters], wing_sweep at 1/4 chord position [TBD]
    
        """

        #TODO: check that wing_span is b (and not tailplane span)
        
        K_lambda  = (10.0 - 3.0 * wing_taper_ratio) / 7.0

        K_h = (1 - np.abs(rel_tail_h / wing_span) ) / (2 * rel_tail_l / wing_span)**(1/3)

        eval_at_M0 = 4.44(K_a * K_lambda * K_h * np.sqrt(np.cos(wing_sweep))) ** (1.19)   

        # TODO: we need the lift curve slope of the wing evaluated at M=flight M (for all flight regimes) and M=0
        # need to figure out with aero guys how they will give this data
        compressibility_correction = None

        return eval_at_M0 * compressibility_correction

    def __adjusted_htail_cl(self):

        return eta_h * hstabilizer_lift_curve_slope * (1-deta_dalpha) * (hstabilizer_ref_area/wing_ref_area)

    def __xnp(self):

        eta_h = self.get_etah()
        deta_dalpha = self.calc_deta_dalpha()
        fuse_CM = self.calc_fuseCM()
        adjusted_htail_Cl = self.calc_adjusted_htail_cl()

        # Equation 5.1-2 on nuclino
        # Note: names are descriptive so aero guys can figure it out on their own
        numerator = wing_lift_curve_slope * pos_wing_AC / (c_bar) - fuse_CM + adjusted_htail_Cl * (pos_hstabilizer_AC/c_bar)

        denominator = wing_lift_curve_slope + adjusted_htail_Cl

        return (numerator/denominator) * c_bar
    

    def __static_margin(x_np, x_cg, c_bar, aircraft):
        """calc_static_margin
            Arguments:  longitudinal position of neutral point,
                        longitudinal position of centre of gravity,
                        mean chord of the wing,

            Return: static margin of aircraft without thrust, SM of AC with thrust
        """

        SM_off =  (x_np - x_cg) / c_bar

        if aircraft.engine_location == "underwing_mounted":
            SM_on = SM_off - 0.02
        
        elif aircraft.engine_location == "aft_mounted":
            SM_on = SM_off + 0.015 # TODO: we can either add 0.02 or 0.01 not sure what is best lol

        if aircraft.engine_type == "propeller":
            SM_on = SM_off - 0.07

        return SM_off, SM_on


        #def calc_dcm_da():


"""
NOTES:



"""