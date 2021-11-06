from numpy.lib.shape_base import column_stack
from .. import ureg as u
from .. import sealevel
from ..Tools import Optimiser, mach_to_speed
from .Config import Config

import matplotlib.pyplot as plt
import numpy as np
from ambiance import Atmosphere


class Constraints(Config, Optimiser):
    '''
    Aircraft Constraints class for PyAVD

    ---> Handles Airworthiness regulations (FAR25 for now) and performance constraints defined in Aircraft.Spec()
    '''

    def __init__(constraint, FieldLength, max_Vstall, Cl_max, Cl_clean, dp_factor):

        constraint.FL = FieldLength
        constraint.max_Vstall = max_Vstall

        # This Cl_max is the same as Cl max for landing
        constraint.Cl_max = Cl_max
        constraint.Cl_clean = Cl_clean

        # X-axis of constraint graph
        constraint.WS = np.array(np.linspace(1, 3000, 10000)) * u.Pa

        constraint.dp_factor = dp_factor

        # Run constraint functions
        constraint.takeoff()
        constraint.landingRaymer(250 * u.meters, 1)
        constraint.landingRoskam()

        constraint.calculate_constraints()
        constraint.designPoint()
        constraint.plot_constraints()


    '''FIELD PERFORMANCE CONSTRAINTS'''


    def takeoff(constraint):
        """ 
        ROSKAM Method
        ---> S_takeoff = 37.5 * TOP (FAR25)
        """
        TOP = constraint.FL / (37.5 * (u.ft ** 3 / u.lb))
        constraint.ClmaxTakeoff = constraint.Cl_clean + 0.7 * (constraint.Cl_max - constraint.Cl_clean)

        # Calculate Thrust/Weight ratio as a function of wing loading
        constraint.TW_takeoff = constraint.WS / ((constraint.ClmaxTakeoff * 9.81 * TOP.to(u.kg / u.m**2)) / 1.21)
        print(f"TW_TO:{constraint.TW_takeoff.to_base_units()}")


    def landingRoskam(constraint):
        """ 
        ROSKAM Method 
        --->
        """
        constraint.V_stall =  ( (constraint.FL.to(u.ft)) / (0.5136 * u.ft / u.kts**2) ) ** 0.5
        constraint.wingLoadingMax_roskam = ( 0.5 * sealevel.density * u.kg/(u.m**3)  * (constraint.V_stall**2) * constraint.Cl_max ).to(u.N / u.m**2)
        constraint.wingLoadingMax_roskam_wet = constraint.wingLoadingMax_roskam/1.3


    def landingRaymer(constraint, Sa, KR):
        """
        RAYMER Method
            
        """

        # FAR25 requirement
        # TODO: put type of requirement (i.e. FAR25) and then some requirements like Sa are set automatically
        # TODO: put the type of aircraft (i.e. jet transport) and then some settings like AR, wetted ratio are set automatically
        ALD = constraint.FL * 3/5
        
        constraint.wingLoadingMax_raymer = (ALD - Sa)/(0.51 * (u.m**3 / u.N) * KR) * constraint.Cl_max


    def stallConstraint(constraint):
        """ 
        RAYMER Method
        """
        constraint.WS_maxStall = np.array(np.ones(10000)) * 0.5 * sealevel.density * (u.kg / u.m**3) * (constraint.max_Vstall**2) * constraint.Cl_max


    """POINT PERFORMANCE CONSTRAINTS - using thrust matching equations"""


    def thrustMatching(constraint, climb_rate, V_inf, alpha, alt, n=1):
        # All the parameters already come with units
        atmosphere = Atmosphere(alt.to(u.m).magnitude)
        rho = atmosphere.density * (u.kg / u.m**3)
        rho0 = sealevel.density * (u.kg / u.m**3)
        sigma = rho / rho0
        
        # Calculate beta
        if alt.to(u.m).magnitude <= 11000:
            beta = sigma ** 0.7
        
        else:
            beta = 1.439 * sigma

        term1 = (1.0 / V_inf) * climb_rate
        # Neglect term 2 of S 2.2.9        
        term3 = (0.5 * rho * ((V_inf)**2) * constraint.Cd0) / (alpha * constraint.WS)
        term4 = (alpha * (n**2) * constraint.WS) / (0.5 * rho * (V_inf**2) * np.pi * constraint.aspect_ratio * constraint.e)

        return (alpha / beta) * (term1 + term3 + term4)
        
    
    def climb(constraint, climb_gradient, V_inf, dCd0, pe): # pe is the percentage factor change in Oswald efficiency factor.
        # # Convert climb gradient (%) into climb rate (dh/dt)
        # climb_rate = (climb_gradient * V_inf.to(u.kts)).magnitude * u.ft / u.min
        # climb_rate = climb_rate.to(u.m / u.s)

        # # Cd0 and e affected by takeoff and landing flap settings during positive and negative climb.
        # constraint.Cd0_takeoff = constraint.Cd0 + 0.02
        # constraint.e_takeoff = constraint.e * 0.95

        # return constraint.thrustMatching(climb_rate, V_inf, alpha, 0 * u.m)

        constraint.Cd0_takeoff = constraint.Cd0 + dCd0
        constraint.e_takeoff = constraint.e * pe
        Cl = constraint.ClmaxTakeoff*(constraint.max_Vstall/V_inf)**2

        LD = Cl/(constraint.Cd0_takeoff + ((Cl)**2)/(np.pi*constraint.aspect_ratio*constraint.e))
        TW = (1/LD) + climb_gradient/100
        return constraint.WS.magnitude *0 + TW


    def go_around_climb(constraint, climb_gradient, V_inf, dCd0, pe, alpha):
        # # Convert climb gradient (%) into climb rate (dh/dt)
        # climb_rate = climb_gradient * V_inf.to(u.kts) #in ft/min

        # constraint.Cd0_goaround = constraint.Cd0 + 0.07
        # constraint.e_goaround = constraint.e * 0.9
        
        # return constraint.thrustMatching(climb_rate, V_inf, alpha, 0 * u.m)

        constraint.Cd0_goaround = constraint.Cd0 + dCd0
        constraint.e_goaround = constraint.e * pe
        Cl = constraint.Cl_max*(constraint.max_Vstall/V_inf)**2

        LD = Cl/(constraint.Cd0_takeoff + ((Cl)**2)/(np.pi*constraint.aspect_ratio*constraint.e))
        TW = ((1/LD) + climb_gradient/100)*alpha

        return constraint.WS.magnitude*0 + TW




    def designPoint(constraint):
        '''Calculates the design point for the aircraft based on constraints provided'''
        
        x2 = constraint.WS[-1].magnitude
        y2 = constraint.TW_takeoff[-1].magnitude

        takeoff_slope = y2/x2
        
        for index, value in enumerate(constraint.WS):
            
            curr_constraints = [constraint.TW_cruise1[index], constraint.TW_cruise2[index],
                                constraint.TW_cruise_maxSpeed[index], constraint.TW_absCeiling[index],
                                constraint.TW_climb1[index], constraint.TW_climb2[index],
                                constraint.TW_climb3[index], constraint.TW_climb4[index],
                                constraint.TW_climb5[index], constraint.TW_loiter[index]]


            if ((value.magnitude)*takeoff_slope > max(curr_constraints)):
                constraint.DP_min_x = value.magnitude
                constraint.DP_min_y = value.magnitude * takeoff_slope
                break

        constraint.DP_max_y = takeoff_slope * constraint.wingLoadingMax_roskam.magnitude
        constraint.DP_max_x = constraint.wingLoadingMax_roskam.magnitude

        constraint.x_designPoint = constraint.DP_min_x + constraint.dp_factor*(constraint.DP_max_x - constraint.DP_min_x) 
        constraint.y_designPoint = constraint.DP_min_y + constraint.dp_factor*(constraint.DP_max_y - constraint.DP_min_y)
        


    def calculate_constraints(constraint):
        WS = constraint.WS

        # Cruise
        constraint.TW_cruise1 = constraint.thrustMatching(0 * u.m / u.s, mach_to_speed((40000 * u.ft).to(u.m).magnitude, 0.75), 0.98, 40000 * u.ft)
        constraint.TW_cruise_maxSpeed = constraint.thrustMatching(0 * u.m / u.s, mach_to_speed((40000 * u.ft).to(u.m).magnitude, 0.78), 0.94, 40000 * u.ft)
        constraint.TW_absCeiling = constraint.thrustMatching(0 * u.m / u.s, mach_to_speed((45000 * u.ft).to(u.m).magnitude, 0.6), 0.94, 45000 * u.ft)
        constraint.TW_cruise2 = constraint.thrustMatching(0 * u.m / u.s, 200 * u.kts, 0.5, 26000 * u.ft)
        
        # # Climb
        # TW_climb1 = constraint.climb(0.1, 1.1 * constraint.V_stall, 0.98) * 2.0
        # TW_climb2 = constraint.climb(2.4, 1.1 * constraint.V_stall, 0.98) * 2.0
        # TW_climb3 = constraint.climb(1.2, 1.25 * constraint.V_stall, 0.98) * 2.0
        # TW_climb4 = constraint.climb(2.1, 1.5 * constraint.V_stall, 0.3) * 2.0
        # TW_climb5 = constraint.climb(3.2, 1.3 * constraint.V_stall, 0.3)

        ## New Climb
        constraint.TW_climb1 = constraint.climb(0.1,1.1 * constraint.V_stall,0.04,0.95) * 2.0
        constraint.TW_climb2 = constraint.climb(2.4, 1.1 * constraint.V_stall,0.02,0.95) * 2.0
        constraint.TW_climb3 = constraint.climb(1.2, 1.25 * constraint.V_stall, 0, 1) * 2.0
        constraint.TW_climb4 = constraint.go_around_climb(2.1, 1.5 * constraint.V_stall,0.05,0.9,0.3) * 2.0
        constraint.TW_climb5 = constraint.go_around_climb(3.2, 1.3 * constraint.V_stall, 0.07,0.9,0.3)

        
        # Loiter
        constraint.TW_loiter = constraint.thrustMatching(0 * u.m / u.s, 150 * u.kts, 0.2, 5000 * u.ft)

        # Landing
        constraint.TW_line = np.linspace(0, 1, 10000)
        constraint.WS_maxLanding_Raymer = np.array(np.ones(10000)) * constraint.wingLoadingMax_raymer
        constraint.WS_maxLandingRoskam = np.array(np.ones(10000)) * constraint.wingLoadingMax_roskam
        constraint.WS_maxLandingRoskamWet = np.array(np.ones(10000)) * constraint.wingLoadingMax_roskam_wet


    def plot_constraints(constraint):
    
        constraint.fig_constraint = plt.figure()

        # Plot the functions
        plt.plot(constraint.WS, constraint.TW_takeoff, 'b', label='Takeoff', linewidth=3)
        plt.plot(constraint.WS_maxLandingRoskam,constraint.TW_line, 'r', label='Roskam Landing', linewidth=3)
        #plt.plot(WS_maxLandingRoskamWet , TW_line, 'tab:orange', label='Roskam Landing (Wet runway)', linewidth=3) #wet runway
        #plt.plot(WS_maxLanding_Raymer,TW_line, 'r--', label='Raymer Landing', linewidth=0.5)
        plt.plot(constraint.WS,constraint.TW_cruise1,'k',label='Cruise 1')
        plt.plot(constraint.WS,constraint.TW_cruise2,'lime',label='Cruise 2')
        plt.plot(constraint.WS,constraint.TW_cruise_maxSpeed,'g',label='Cruise Max Speed', linewidth=3)
        plt.plot(constraint.WS,constraint.TW_absCeiling,'tab:pink',label='Absolute ceiling')
        plt.plot(constraint.WS,constraint.TW_loiter,'tab:cyan',label='Loiter')

        plt.plot(constraint.WS,constraint.TW_climb1,'y',label='Climb 1st Segment OEI')
        plt.plot(constraint.WS,constraint.TW_climb2,'m',label='Climb 2nd Segment OEI')
        plt.plot(constraint.WS,constraint.TW_climb3,'c',label='Climb 3rd Segment OEI')
        plt.plot(constraint.WS,constraint.TW_climb4,'tab:olive',label='Climb from approach OEI')
        plt.plot(constraint.WS,constraint.TW_climb5,'tab:brown',label='Climb from landing AEO')


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

        plt.axvspan(constraint.WS_maxLandingRoskam.magnitude[0], 3000, facecolor='lightgrey', alpha=0.5)

        
        constraint_list = [constraint.TW_cruise1, constraint.TW_cruise2,
                            constraint.TW_cruise_maxSpeed, constraint.TW_absCeiling,
                            constraint.TW_climb1, constraint.TW_climb2,
                            constraint.TW_climb3, constraint.TW_climb4,
                            constraint.TW_climb5, constraint.TW_loiter]
        for const in constraint_list:
            plt.fill_between(constraint.WS, constraint.WS * 0, const, color='lightgrey')

        plt.fill_between(constraint.WS, constraint.WS * 0, constraint.TW_takeoff , color='lightgrey')