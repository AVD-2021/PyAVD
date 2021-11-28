from logging import WARNING

from numpy.lib.shape_base import dstack
from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np
import sympy as sym

from pyavd.Models.Components.Aircraft import Aircraft


class Performance(Model):
    """Performance model
    
    Variables
    ---------
    
    """
    @parse_variables(__doc__, globals())
    def setup(self, fuselage, wing, aircraft, engine, empennage, regulations):
        constraints     = self.constraints  = []
        


        self.V_lof = (1.1 * aircraft.stall_speed_To).to(u.meters / u.second)
        self.V_td = (1.15 * aircraft.stall_speed_Ld).to(u.meters / u.second)


        self.S_g = self.get_Sg(aircraft, wing)
        self.S_r = self.get_Sr(aircraft, wing)
        self.S_tr, self.S_cl = self.get_Str_Scl(aircraft, wing, regulations)

        self.S_b = self.get_Sb(aircraft, wing)
        self.S_fr = self.get_Sfr()
        self.S_f, self.h_f = self.get_Sf_hf(aircraft)
        self.S_a = self.get_Sa(aircraft, regulations)

        self.S_To_act = (self.S_g + self.S_cl + self.S_tr) # already accounts for safety factor
        self.S_Ld_act = (self.Sa + self.S_f + self.S_fr + self.S_b) # already accounts for safety factor

        self.S_to_req = 1.15 * self.S_To_act
        self.S_Ld_req = 1.666 * self.S_Ld_act

        return [constraints]



    def get_Sg(self, aircraft, wing):

        mu = 0.03 # assuming dry concrete

        K_A  = (raihaan.rho / (2 * aircraft.W0_S)) * (mu * aircraft.CL_ground  - aircraft.CD0 - aircraft.CL_ground**2 / (np.pi * wing.AR * wing.e))
        K_T = aircraft.T0_W0 - mu

        S_g = (1.0 / (2.0 * aircraft.g.to(u.meters / u.second**2) * K_A)) * np.log((K_T + K_A * self.V_lof**2)/(K_T))
        
        return S_g

    def get_Sr(self, aircraft):

        dtheta_dt = 3 * (u.degree / u.second) 
        S_r = self.V_lof * ( (aircraft.aoa_To.to(u.radians) - aircraft.aoa_g.to(u.radians)) / dtheta_dt.to(u.radians / u.second))

        return S_r

    def get_Str_Scl(self, aircraft, regulations):
        
        V_tr = (1.15 * aircraft.stall_speed_To).to(u.meters / u.second)
        
        # Assumed load factor
        n = 1.2

        R = V_tr ** 2 / ((n - 1) * aircraft.g.to(u.meters / u.second**2))

        
        gamma_CL = np.arcsin(aircraft.T0_W0 - 1/aircraft.LD_To)

        h_tr = R * (1 - np.cos(gamma_CL))

        if h_tr > regulations.h_obs.to(u.meters):
            S_tr = np.sqrt(R**2 - (R-regulations.h_obs.to(u.meters)) ** 2)
            S_cl = 0

        else:
            S_tr = R * np.sin(gamma_CL)
            S_cl = (regulations.h_obs.to(u.meters)-h_tr) / np.tan(gamma_CL)

        return S_tr, S_cl

    

    def get_BFL(self, aircraft, engine, regulations):
        
        # Raymer 17.114
        T_av = 0.75 * aircraft.T_stat_To * (5 + engine.BPR) / (4 + engine.bpr)

        gamma_cl = np.arcsin(((aircraft.n_engines-1)/aircraft.n_engine) * aircraft.T0_W0 - aircraft.D_oei_vcl / aircraft.W0)
        
        if aircraft.n_engines == 2:
            gamma_min = 0.024
        elif aircraft.n_engines == 3:
            gamma_min = 0.027
        elif aircraft.n_engines == 4:
            gamma_min = 0.030

        G = gamma_cl - gamma_min
     
        # 0.02 if we have typical flaps
        U = 0.01 * aircraft.CL_max_clean + 0.02
        
        sigma = raihaan.rho / raihaan.rho_SL

        BFL = (0.863/(1 + 2.3 * G)) * ((aircraft.W_S) / (raihaan.rho * aircraft.g.to(u.feet / u.second**2) * aircraft.CL_climb) + regulations.h_obs.to(u.feet)) * (1/(T_av/aircraft.W0 - U) + 2.7) + 655/np.sqrt(sigma)

        return BFL.to(u.meters)


    
    def get_Sb(self, aircraft, wing):

        
        if (aircraft.rev_thrust):
            T_breaking = - aircraft.T_max * 0.4 # most conservative of -0.4 to -0.5
        else:
            T_breaking = aircraft.T_max * 0.15 # most conservative of 0.10 to 0.15        

        if (aircraft.wheel_breaking):
            mu = 0.3 # conservative of 0.3 to 0.5
        else:
            mu = 0.03


        K_A = (raihaan.rho / (2.0  * aircraft.WS_landing)) * (mu * aircraft.CL_landing - aircraft.CD0 - aircraft.CL_landing**2 / (np.pi * wing.AR * wing.e))

        K_T = T_breaking / aircraft.W_landing - mu

        S_b = (1/(2 * aircraft.g * K_A)) * np.log(K_T / (K_T + K_A * self.V_td ** 2))
        
        return S_b


    def get_Sfr(self):
        
        t_fr = 3 # assuming the worse scenario (1-3 secs)

        S_fr = self.V_td * t_fr
        
        return S_fr


    def get_Sf_hf(self, aircraft):
        
        gamma_a = (3 * u.degrees).to(u.radians)

        V_f = 1.23 * aircraft.stall_speed_Ld

        # Loading factor
        n = 1.2

        R = V_f ** 2 / ((n-1)*aircraft.g)

        h_f = R(1-np.cos(gamma_a))

        S_f = R * np.sin(gamma_a)

        return S_f, h_f


    def get_Sa(self, aircraft, regulations):

        gamma_a = (3 * u.degrees).to(u.radians)

        #V_a = 1.3 * aircraft.stall_speed_Ld

        S_a = (regulations.h_obs.to(u.meter) - self.h_f) / np.tan(gamma_a)

        return S_a





"""
list of variable we need:

1. aircraft stall speed at take off config.                        --> aircraft.stall_speed_To
2. density                                                         --> raihaan.rho
3. Lift coefficient at takeoff config. (@ ground angle of attack)  --> aircraft.CL_ground 
4. AoA at take off                                                 --> aircraft.aoa_To
5. AoA at ground                                                   --> aircraft.aoa_g
6. lift to drag ratio at takeoff                                   --> aircraft.LD_T0
7. obstable height                                                 --> regulations.h_obs
8. number of engines                                               --> aircraft.n_engines
9. static thrust of the engine at takeoff                          --> aircraft.T_stat_To
10. Engine bypass ratio                                            --> Engine.bpr
11. Drag at OEI case evaluated at V_cl                             --> aircraft.D_oei_vcl 
12. CL max of clean configuration                                  --> aircraft.CL_max_clean
13. CL at climb                                                    --> aicraft.CL_climb
14. rho_SL                                                         --> sea level rho
15. aircraft stall speed at landing configuration                  --> aircraft.stall_speed_Ld       
16. do we have wheel braking?   
17. do we have reverse thrust?
18. maximum thrust                                                 --> aircraft.T_max
19. Breaking Thrust                                                --> aircraft.T_breaking
20. landing weight                                                 --> aircraft.W_landing
21. landing Wing loading                                           --> aircraft.WS_landing
22. CL at the landing config                                       --> aircraft.CL_landing

"""


