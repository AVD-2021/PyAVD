from logging import WARNING
from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np

''' Temp
    x_cg                            [m]             Centre of Gravity - x-axis
'''

class Stability(Model):
    """Stability model
    
    Variables
    ---------
    x_np                            [m]             Neutral Point Position
    depsilon_dalpha                 [-]             Rate of Change of Downwash with AoA (@M0)       
    fuse_Cm                         [-]             Pitching Moment Coefficient of Fuselage
    Kn_on                           [-]             Static Margin (w/ thrust)
    adjusted_htail_cl               [-]             Pre-determined value to ease complexity in code
    dCM_dalpha                      [-]             Rate of change of Moment coefficient with AoA w.r.t to cg 

    """
    @parse_variables(__doc__, globals())
    def setup(self, fuselage, wing, engine, empennage):
        constraints     = self.constraints  = []

        self.fuselage   = fuselage
        self.wing       = wing
        self.empennage  = empennage

        # Importing parameters from aircraft components
        c_bar           = self.c            = wing.c
        x_ac            = self.x_ac         = wing.x_ac
        x_cg            = self.x_cg         = wing.x_cg
        S_ref           = self.S_ref        = wing.S_ref
        AR              = self.AR           = wing.AR
        x_qc            = self.x_qc         = wing.x_qc                         # wing quarter chord position
        b               = self.b            = wing.b                            # span
        lam             = self.lam          = wing.lam                          # sweep angle
        gam             = self.gam          = wing.gam                          # taper ratio
        CL_alpha        = self.CL_alpha     = wing.CL_alpha                     # wing lift curve slope
        eta_h           = self.eta_h        = empennage.tailplane.eta_h         # h.tailplane effic.
        CLalpha_h       = self.CLalpha_h    = empennage.tailplane.CLalpha_h     # h.tailplane lift curve slope
        S_h             = self.S_h          = empennage.tailplane.S_h           # h.tailplane area
        x_ac_h          = self.x_ac_h       = empennage.tailplane.x_ac_h        # h.tailplane aero. centre 
        l_f             = self.l            = fuselage.l                        # fuselage length 
        w_f             = self.w            = fuselage.w                        # fuselage width
        

        # K_f = self.Kf = Variable("K_f", "", "K_f")
        # K_f will be either a lookup function or a separate variable
        # [a,b,c] = [1,2,3] ---> polyfit stuffs, then a quick lambda function?

        
        # Taking Fuselage width to be the max width; c is c_bar
        # constraints.update({"Pitching Moment Coefficient Fuselage":
        self.fuse_Cm = (K_f * l_f * (w_f ** 2) / (c_bar * S_ref))            # ---> This syntax is 'legal'
        

        # following "Ks" are for calculating depsilon_dalpha
        K_a1        = 1.0 + AR ** 1.7
        K_a         = 1.0/AR - 1.0/K_a1
        K_lambda    = (10.0 - 3.0 * gam) / 7.0

        K_h = (1 - h_h / b ) / (2 * rel_tail_l / b)**(1/3)


        # constraints.update({"Rate of Change of Downwash with AoA: ":
        #     # taking the pre-determined value "k_", wing sweep, and compressiblity correction (TBD)
        #     depsilon_dalpha >= 4.44(K_a * K_lambda * K_h * np.sqrt(np.cos(lam))) ** (1.19) * compressibility_correction})

        depsilon_dalpha = 4.44 * (K_a * K_lambda * K_h * np.sqrt(np.cos(lam))) ** (1.19) * compressibility_correction





        constraints.update({"Adjusted Horizontal Tailplane CL":
            # taking values from empennage --> eta_h, hstabilizer_lift_curve_slope
            adjusted_htail_cl >= eta_h * CLalpha_h * (1-depsilon_dalpha) * (S_h/S_ref)})


        numerator = CL_alpha * x_ac / (c_bar) - fuse_Cm + adjusted_htail_Cl * (x_ac_h/c_bar)
        denominator = CL_alpha + adjusted_htail_Cl

        constraints.update({"Neutral Point":
            x_np == (numerator/denominator) * c_bar})
        





        constraints.update({"Rate of change of C_M with AoA":
            dCM_dalpha >= -CL_alpha * ((x_ac-x_cg) / c_bar) + fuse_Cm - adjusted_htail_cl * ((x_ac_h-x_cg)/c_bar)})
        ## Prolly need to add "if" statements to pass information if it's not negative (stable) 



        Kn_off =  (x_np - x_cg) / c_bar

        if engine.type         == "propeller":            Kn_on = Variable("Kn_on", Kn_off - 0.07, "Static Margin (w/ Thrust)")
        elif engine.location   == "underwing_mounted":    Kn_on = Variable("Kn_on", Kn_off - 0.02, "Static Margin (w/ Thrust)")
        elif engine.location   == "aft_mounted":          Kn_on = Variable("Kn_on", Kn_off + 0.015, "Static Margin (w/ Thrust)")        


        return [constraints]



"""
NOTES:

1. not sure if the above code are implemented correctly ---> reviewed and edited
2. will the trim analysis be on this script as well? (TBD) ---> nope, separate script for trim analysis, accessed by mission

"""