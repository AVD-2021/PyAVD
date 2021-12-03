from logging import WARNING

from gpkit import Model, Variable, VectorVariable, Vectorize, parse_variables
from gpkit.constraints.tight import Tight
from gpkit import ureg as u
import numpy as np
import sympy as sym

# from pyavd.Models.Components.Aircraft import Aircraft


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
        
        sigma = state.rho / state.rho0

        BFL = (0.863/(1 + 2.3 * G)) * ((aircraft.W_S) / (state.rho * aircraft.g.to(u.feet / u.second**2) * aircraft.CL_climb) + regulations.h_obs.to(u.feet)) * (1/(T_av/aircraft.W0 - U) + 2.7) + 655/np.sqrt(sigma)

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


        K_A = (state.rho / (2.0  * aircraft.WS_landing)) * (mu * aircraft.CL_landing - aircraft.CD0 - aircraft.CL_landing**2 / (np.pi * wing.AR * wing.e))

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


######
## Mission Performance
####


    def Breguet_range(self, range, speed, SFC, LD):
        '''Evaluates weight fraction for a given flight regime'''

        # Equation S 1.3-2 - Breguet range
        return np.exp(- range * SFC / (speed * LD))
    
    def Breguet_endurance(self, endurance, SFC, LD):
        return np.exp(- endurance * SFC / LD )

    def mission_profile(self, mission_profile, aircraft):
        
        if (current aircraft.We is close to old approx from poster):

            # Equation S 1.3-1 - Fuel weight fraction
            aggregate_fuel_frac = 1
            fuel_fracs = []

            # 0-1 segment (takeoff)
            aggregate_fuel_frac *= 0.970

            # 1-2 segment (climb)
            aggregate_fuel_frac *= 0.985

            # 3-4 segment (descent)
            aggregate_fuel_frac *= 0.99

            # 4-5 (climb) 
            aggregate_fuel_frac *= 0.985

            # 5-6 (2nd cruise)
            aggregate_fuel_frac *= self.Breguet_range(370000 * u.m, poster_speed * u.meters, SFC_2ndcruise, adem.LD_2ndcruise)

            # 7-8 (loiter)
            aggregate_fuel_frac *= self.Breguet_endurance(45 * u.min, ruaridth.SFC_loiter, adem.LD_loiter)

            # 8-9 (descent) 
            aggregate_fuel_frac *= 0.99
            # TODO: is decent a part of landing????? question mark ?

            # 9-10 (landing)
            aggregate_fuel_frac *= 0.995

            # repeat belof for various payload and weight fuels and make plot like in nuclino

            W10_W0 = (aircraft.W0 - aircraft.Wf) / aircraft.W0

            W2_W3 = W10_W0 / aggregate_fuel_frac

            cruise_range = np.log(W2_W3) * aircraft.LD_at_cruise * aircraft.cruise_speed / ruaridth.SFC_cruise

        else:
            # re-estimate cruise and loiter weight fractions 
            


        # for i in range(len(mission_profile)):
        #     if mission_profile[i][0].lower() == "takeoff":
        #         aggregate_fuel_frac *= 0.97
        #         fuel_fracs.append(["Takeoff", 0.970])
                
        #     elif mission_profile[i][0].lower() == "climb":
        #         aggregate_fuel_frac *= 0.985
        #         fuel_fracs.append(["Climb", 0.985])
                
        #     elif mission_profile[i][0].lower() == "landing":
        #         aggregate_fuel_frac *= 0.995
        #         fuel_fracs.append(["Landing", 0.995])

        #     elif mission_profile[i][0].lower() == "cruise":
        #         cruise_frac = self.Breguet_range(mission_profile[i][1], SFC[0], LD[0])
        #         aggregate_fuel_frac *= cruise_frac
        #         fuel_fracs.append(["Cruise", np.round(cruise_frac.magnitude[0], 3)])

        #     elif mission_profile[i][0].lower() == "descent":
        #         aggregate_fuel_frac *= 0.99
        #         fuel_fracs.append(["Descent", 0.99])

        #     elif mission_profile[i][0].lower() == "loiter":
        #         loiter_frac = self.__Breguet_endurance(mission_profile[i][1], SFC[1], LD[1])
        #         aggregate_fuel_frac *= loiter_frac
        #         fuel_fracs.append(["Loiter", np.round(loiter_frac.magnitude, 3)])


            Wf_W0 = 1.01 * (1-aggregate_fuel_frac)


####
# Point Performance
###

    def rate_of_climb(self):

        # INSERT
        T = None 
        D = None

        # evaluate this at the weight of both climbs we do (get weight there using weight frac)
        W = None
    
        gamma = np.arcsin((T-D)/W)
        
        # for velocity at which we will climb (both climbs)
        V = None

        V_v = V * np.sin(gamma)

        # from this function want to get service ceiling (V_v = 500 ft/min), absolute ceiling (V_v = 0), and check that we meed gradient FAR25 req.


    def mission_envelope(self, wing):

        for altitude in ...:

            rho = fn(alt)
            speed_of_sound = fn(alt)

            V_s = np.sqrt(2 * (aircraft.WS_cruise) / (rho * aircraft.CL_max_clean))

            V_max = aircraft.T_max / (0.5 * rho * wing.S * aircraft.CD_cruise)

            M_max = V_max / speed_of_sound



            # make specific excess power contour plot



"""
list of variable we need:

1. aircraft stall speed at take off config.                        --> aircraft.stall_speed_To      --> (NOT defined, without value)


3. Lift coefficient at takeoff config. (@ ground angle of attack)  --> aircraft.CL_ground           --> (NOT defined without value)

4. AoA at take off                                                 --> aircraft.aoa_To              --> (NOT defined, without value)
5. AoA at ground                                                   --> aircraft.aoa_g               --> (NOT defined, without value)
6. lift to drag ratio at takeoff                                   --> aircraft.LD_T0               --> (NOT defined, without value)
   
9. static thrust of the engine at takeoff                          --> aircraft.T_stat_To           --> (Defined, without value)
10. Engine bypass ratio                                            --> Engine.bpr                   --> (Defined, without value)
11. Drag at OEI case evaluated at V_cl                             --> aircraft.D_oei_vcl           --> (NOT defined, without value)
12. CL max of clean configuration                                  --> aircraft.CL_max_clean        --> (NOT defined, without value)
13. CL at climb                                                    --> aicraft.CL_climb             --> (NOT defined, without value)
15. aircraft stall speed at landing configuration                  --> aircraft.stall_speed_Ld      --> (NOT defined, without value)

16. do we have wheel braking?                                                                       --> (Defined, without value)
17. do we have reverse thrust?                                                                      --> (Defined, without value)

18. maximum thrust                                                 --> aircraft.T_max               --> (Defined, without value)
20. landing weight                                                 --> aircraft.W_landing           --> (NOT defined, without value)
21. landing Wing loading                                           --> aircraft.WS_landing          --> (NOT defined, without value) -- segment
22. CL at the landing config                                       --> aircraft.CL_landing          --> (NOT defined, without value) 

23. fuel weight (W_f)                                              --> (NOT defined, without value) 
24. CD cruise                                                      --> (NOT defined, without value) 

1. SFC for loiter cruise and 2nd cruise                         --> (NOT defined, without value) -- segment 
2. L/D for loiter, cruise, and 2nd cruise                       --> (NOT defined, without value) -- segment
3. flight speed for 2nd cruise                                  --> (NOT defined, without value) -- segment


4. why did errikos no like our weight fracs?? correct them according to his poster feedback!!
5. empty weight? is it similar to poster prediction??? !!!!(LAST VERIFICATION)


1. equation for T as a function of flight speed, height              --> T = fn(v,h) !!
2. equation for D as a function of flight speed, height and weight   --> D = fn(v,h,W) !!
"""