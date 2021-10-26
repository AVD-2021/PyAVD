from .Spec import Spec
from .Config import Config
from .Constraints import Constraints
from ..Tools import debug
from plotly import graph_objects as go
import numpy as np

class Aircraft(Constraints):
    '''
    Aircraft class definition for PyAVD
    ---> Inherits from the Constraints superclass

    Attributes
    ----------
    name : str
        Name of the aircraft
    
    Methods
    -------
    __init__(self, name)
        Initialize the class

    iterate_W0(self, n)
        Redcalculates the gross takeoff weight using Equation S 1.1-3
    '''

    def __init__(ac, pax, crew, mission_profile, AR, e, FieldLength, max_Vstall, Cl_max, Cl_clean, n):

        Spec.__init__(ac, pax, crew, mission_profile)
        Config.__init__(ac, AR, e)
        Constraints.__init__(ac, FieldLength, max_Vstall, Cl_max, Cl_clean)

        # On first iteration, approximate aircraft W0 from baseline configuration
        Config.W0_approx(ac)
        ac.W0_histories = [ac.W0.magnitude]

        # Iterate W0 until convergence!
        ac.iterate_S1(n)

        # Plot W0 history
        ac.plot_histories()


    @debug
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
        for i in range(n):

            # Equation S 1.1-3 - Note that weight fractions computed in the configuration class
            ac.W0 = ac.fixed_weight / (1.0 - ac.WfW0(ac.profile, [ac.SFC_cruise_approx, ac.SFC_loiter_approx], [ac.LD_cruise, ac.LD_loiter]) - ac.WeW0(ac.W0))
            ac.W0_histories.append(ac.W0.magnitude)
            

    def plot_histories(ac):
        '''
        Plotly line chart of the W0 histories for each iteration
        '''
        
        ac.fig_W0_histories = go.Figure()
        ac.fig_W0_histories.add_trace(go.Scatter(x=np.arange(len(ac.W0_histories)), y=ac.W0_histories, mode='lines'))
        ac.fig_W0_histories.update_layout(title="W0 Estimation", xaxis_title="Iterations", yaxis_title='W0', legend_title="estimated W0 value")