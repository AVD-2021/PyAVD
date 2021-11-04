from .Spec import Spec
from .Config import Config
from .Constraints import Constraints

from plotly import graph_objects as go
from matplotlib import pyplot as plt
import numpy as np


class Aircraft(Constraints):
    '''
    Aircraft class definition for PyAVD

    ---> Inherits from the Constraints superclass

    Attributes
    ----------
    
    Methods
    -------
    iterate_W0(self, n)
        Redcalculates the gross takeoff weight using Equation S 1.1-3
    '''

    def __init__(ac, pax, crew, mission_profile, AR, e, FieldLength, max_Vstall, Cl_max, Cl_clean, weight, n=10):

        Spec.__init__(ac, pax, crew, mission_profile)
        Config.__init__(ac, AR, e)
        Constraints.__init__(ac, FieldLength, max_Vstall, Cl_max, Cl_clean)

        # On first iteration, approximate aircraft W0 from baseline configuration
        Config.W0_approx(ac)
        ac.W0_histories = [ac.W0.magnitude]
        ac.weight_frac_histories = []

        # Iterate W0 until convergence!
        ac.iterate_S1(n)

        # Plot W0 history
        ac.plot_histories()


    def iterate_S1(ac, n):
        '''
        Uses latest operating empty weight and fuel weight fractions, computes gross takeoff weight
        
            Parameters:
                ac (Aircraft): aircraft object
                n (int): iteration number
                
            Returns:
                W0 (float): new gross takeoff weight
        '''

        # Iterate n times
        for _ in range(int(n)):

            # Equation S 1.1-3 - Note that weight fractions computed in the configuration class
            ac.W0 = ac.fixed_weight / (1.0 - ac.WfW0(ac.profile, [ac.SFC_cruise_approx, ac.SFC_loiter_approx], [ac.LD_cruise, ac.LD_loiter]) - ac.WeW0(ac.W0))
            ac.W0_histories.append(ac.W0.magnitude[0])
            

    def plot_histories(ac):
        '''
        Chart of the W0 histories for each iteration
        '''
        
        # Plotly
        ac.fig_W0_histories = go.Figure()
        ac.fig_W0_histories.add_trace(go.Scatter(x=np.arange(len(ac.W0_histories)), y=ac.W0_histories, mode='lines'))
        ac.fig_W0_histories.update_layout(title="Gross Takeoff Weight Estimation", xaxis_title="Iteration", yaxis_title='Total Weight (kg)')

        # # Matplotlib for the poster
        # ac.fig_W0_histories = plt.figure()
        # plt.plot(ac.W0_histories)
        # plt.xlabel("Iteration")
        # plt.ylabel("$W_0$ (kg)")
        # plt.title("$W_0$ vs Iteration")
        # plt.grid(True)
