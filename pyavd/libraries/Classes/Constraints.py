from .. import ureg, sealevel
from ..Tools import Optimiser, mach_to_speed
from .Config import Config

import matplotlib.pyplot as plt
from scipy.optimize import minimize
import numpy as np
from ambiance import Atmosphere


class Constraints(Config, Optimiser):
    '''
    Aircraft Constraints class for PyAVD

    ---> Handles Airworthiness regulations (FAR25 for now) and performance constraints defined in Aircraft.Spec()
    '''

    def __init__(constraint, FieldLength, max_Vstall, Cl_max, Cl_clean):

        constraint.FL = FieldLength
        constraint.max_Vstall = max_Vstall

        # This Cl_max is the same as Cl max for landing
        constraint.Cl_max = Cl_max
        constraint.Cl_clean = Cl_clean

        # X-axis of constraint graph
        constraint.WS = np.array(np.linspace(1, 3000, 10000)) * ureg.Pa


        # Run constraint functions
        constraint.takeoff()
        constraint.landingRaymer(250 * ureg.meters, 1)
        constraint.landingRoskam()
        constraint.designPoint()

        constraint.plot_constraints()


    '''FIELD PERFORMANCE CONSTRAINTS'''


    def takeoff(constraint):
        """ 
        ROSKAM Method
        ---> S_takeoff = 37.5 * TOP (FAR25)
        """
        TOP = constraint.FL / (37.5 * (ureg.ft ** 3 / ureg.lb))
        ClmaxTakeoff = constraint.Cl_clean + 0.7 * (constraint.Cl_max - constraint.Cl_clean)

        # Calculate Thrust/Weight ratio as a function of wing loading
        constraint.TW_takeoff = constraint.WS / ((ClmaxTakeoff * 9.81 * TOP.to(ureg.kg / ureg.m**2)) / 1.21)
        print(f"TW_TO:{constraint.TW_takeoff.to_base_units()}")


    def landingRoskam(constraint):
        """ 
        ROSKAM Method 
        --->
        """
        constraint.V_stall =  ( (constraint.FL.to(ureg.ft)) / (0.5136 * ureg.ft / ureg.kts**2) ) ** 0.5
        constraint.wingLoadingMax_roskam = ( 0.5 * sealevel.density * ureg.kg/(ureg.m**3)  * (constraint.V_stall**2) * constraint.Cl_max ).to(ureg.N / ureg.m**2)
        constraint.wingLoadingMax_roskam_wet = constraint.wingLoadingMax_roskam/1.3


    def landingRaymer(constraint, Sa, KR):
        """
        RAYMER Method
            
        """

        # FAR25 requirement
        # TODO: put type of requirement (i.e. FAR25) and then some requirements like Sa are set automatically
        # TODO: put the type of aircraft (i.e. jet transport) and then some settings like AR, wetted ratio are set automatically
        ALD = constraint.FL * 3/5
        
        constraint.wingLoadingMax_raymer = (ALD - Sa)/(0.51 * (ureg.m**3 / ureg.N) * KR) * constraint.Cl_max


    def stallConstraint(constraint):
        """ 
        RAYMER Method
        """
        constraint.WS_maxStall = np.array(np.ones(10000)) * 0.5 * sealevel.density * (ureg.kg / ureg.m**3) * (constraint.max_Vstall**2) * constraint.Cl_max


    """POINT PERFORMANCE CONSTRAINTS - using thrust matching equations"""


    def thrustMatching(constraint, climb_rate, V_inf, alpha, alt, n=1):
        # All the parameters already come with units
        atmosphere = Atmosphere(alt.to(ureg.m).magnitude)
        rho = atmosphere.density * (ureg.kg / ureg.m**3)
        rho0 = sealevel.density * (ureg.kg / ureg.m**3)
        sigma = rho / rho0
        
        # Calculate beta
        if alt.to(ureg.m).magnitude <= 11000:
            beta = sigma ** 0.7
        
        else:
            beta = 1.439 * sigma

        term1 = (1.0 / V_inf) * climb_rate
        # Neglect term 2 of S 2.2.9        
        term3 = (0.5 * rho * ((V_inf)**2) * constraint.Cd0) / (alpha * constraint.WS)
        term4 = (alpha * (n**2) * constraint.WS) / (0.5 * rho * (V_inf**2) * np.pi * constraint.aspect_ratio * constraint.e)

        return (alpha / beta) * (term1 + term3 + term4)
        
    
    def climb(constraint, climb_gradient, V_inf, alpha): 
        # Convert climb gradient (%) into climb rate (dh/dt)
        climb_rate = (climb_gradient * V_inf.to(ureg.kts)).magnitude * ureg.ft / ureg.min
        climb_rate = climb_rate.to(ureg.m / ureg.s)

        # Cd0 and e affected by takeoff and landing flap settings during positive and negative climb.
        constraint.Cd0_takeoff = constraint.Cd0 + 0.02
        constraint.e_takeoff = constraint.e * 0.95

        return constraint.thrustMatching(climb_rate, V_inf, alpha, 0 * ureg.m)


    def go_around_climb(constraint, climb_gradient, V_inf, alpha):
        # Convert climb gradient (%) into climb rate (dh/dt)
        climb_rate = climb_gradient * V_inf.to(ureg.kts) #in ft/min

        constraint.Cd0_goaround = constraint.Cd0 + 0.07
        constraint.e_goaround = constraint.e * 0.9
        
        return constraint.thrustMatching(climb_rate, V_inf, alpha, 0 * ureg.m)


    def designPoint(constraint):
        '''Calculates the design point for the aircraft based on constraints provided'''

        x = constraint.WS[-1].magnitude
        y = constraint.TW_takeoff[-1].magnitude

        constraint.y_designPoint = y / x * constraint.wingLoadingMax_roskam_wet.magnitude
        constraint.x_designPoint = constraint.wingLoadingMax_roskam_wet.magnitude


    def plot_constraints(constraint):

        WS = constraint.WS

        # Cruise
        TW_cruise1 = constraint.thrustMatching(0 * ureg.m / ureg.s, mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.75), 0.98, 40000 * ureg.ft)
        constraint.TW_cruise_maxSpeed = constraint.thrustMatching(0 * ureg.m / ureg.s, mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.78), 0.94, 40000 * ureg.ft)
        TW_absCeiling = constraint.thrustMatching(0 * ureg.m / ureg.s, mach_to_speed((45000 * ureg.ft).to(ureg.m).magnitude, 0.6), 0.94, 45000 * ureg.ft)
        TW_cruise2 = constraint.thrustMatching(0 * ureg.m / ureg.s, 200 * ureg.kts, 0.5, 26000 * ureg.ft)
        
        # Climb
        TW_climb1 = constraint.climb(0.1, 1.1 * constraint.V_stall, 0.98) * 2.0
        TW_climb2 = constraint.climb(2.4, 1.1 * constraint.V_stall, 0.98) * 2.0
        TW_climb3 = constraint.climb(1.2, 1.25 * constraint.V_stall, 0.98) * 2.0
        TW_climb4 = constraint.climb(2.1, 1.5 * constraint.V_stall, 0.3) * 2.0
        TW_climb5 = constraint.climb(3.2, 1.3 * constraint.V_stall, 0.3)
        
        # Loiter
        TW_loiter = constraint.thrustMatching(0 * ureg.m / ureg.s, 150 * ureg.kts, 0.2, 5000 * ureg.ft)

        # Landing
        TW_line = np.linspace(0, 1, 10000)
        WS_maxLanding_Raymer = np.array(np.ones(10000)) * constraint.wingLoadingMax_raymer
        WS_maxLandingRoskam = np.array(np.ones(10000)) * constraint.wingLoadingMax_roskam
        WS_maxLandingRoskamWet = np.array(np.ones(10000)) * constraint.wingLoadingMax_roskam_wet

    

        constraint.fig_constraint = plt.figure()

        # Plot the functions
        plt.plot(WS, constraint.TW_takeoff, 'b', label='Takeoff', linewidth=3)
        plt.plot(WS_maxLandingRoskam,TW_line, 'r', label='Roskam Landing', linewidth=3)
        plt.plot(WS_maxLandingRoskamWet , TW_line, 'tab:orange', label='Roskam Landing (Wet runway)', linewidth=3) #wet runway
        # plt.plot(WS_maxLanding_Raymer,TW_line, 'r--', label='Raymer Landing', linewidth=0.5)
        plt.plot(WS,TW_cruise1,'k',label='Cruise 1')
        plt.plot(WS,TW_cruise2,'lime',label='Cruise 2')
        plt.plot(WS,constraint.TW_cruise_maxSpeed,'g',label='Cruise Max Speed', linewidth=3)
        plt.plot(WS,TW_absCeiling,'tab:pink',label='Absolute ceiling')
        plt.plot(WS,TW_loiter,'tab:cyan',label='Loiter')
        plt.plot(WS,TW_climb1,'y',label='Climb 1st Segment OEI')
        plt.plot(WS,TW_climb2,'m',label='Climb 2nd Segment OEI')
        plt.plot(WS,TW_climb3,'c',label='Climb 3rd Segment OEI')
        plt.plot(WS,TW_climb4,'tab:olive',label='Climb from approach OEI')
        plt.plot(WS,TW_climb5,'tab:brown',label='Climb from landing AEO')

        plt.plot(constraint.x_designPoint, constraint.y_designPoint,'r',marker = "o",label='Selected Design Point', markersize=10)
        plt.annotate("Design Point", (constraint.x_designPoint, constraint.y_designPoint),
                     xytext=(constraint.x_designPoint - 800, constraint.y_designPoint + 0.2),
                     arrowprops=dict(facecolor='black', shrink=0.05, width=2, headwidth=13, headlength=10))
         
        plt.xlabel(r"$\frac{W_0}{S_{ref}}$ ($N/m^2$)")
        plt.ylabel(r"$\frac{T_0}{W_0}$")
        plt.title("Aircraft Constraints")
        plt.legend(bbox_to_anchor=(1, 1))

        plt.grid()
        # show the plot
        plt.ylim([0, 1])
        plt.xlim([0, 3000])

        plt.fill_between(constraint.WS, constraint.WS * 0, constraint.TW_cruise_maxSpeed, color='lightgrey')
        plt.fill_between(constraint.WS, constraint.WS * 0, constraint.TW_takeoff, color='lightgrey')
        plt.fill_between(constraint.WS, WS_maxLandingRoskamWet, 3000 * np.ones(10000), color='lightgrey')
        plt.axvspan(WS_maxLandingRoskamWet.magnitude[0], 3000, facecolor='lightgrey', alpha=0.5)
