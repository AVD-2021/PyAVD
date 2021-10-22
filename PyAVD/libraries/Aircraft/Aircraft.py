from .Spec import Spec
from .BaselineConfig import BaselineConfig as Config
from .Constraints import Constraints


class Aircraft(Spec, Config, Constraints):
    '''
    Aircraft class definition for PyAVD
    ---> Inherits from the Spec, BaselineConfig and Constraints superclasses

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

    def __init__(ac, pax, crew, mission_profile):
        Spec.__init__(ac, pax, crew, mission_profile)
        Config.__init__(ac)

        # Constraints.__init__(ac)

        # On first iteration, approximate aircraft W0 from baseline configuration
        ac.W0 = Config.W0_approx(ac)
        ac.s1_iterate_W0(10)


    def s1_iterate_W0(ac, n):
        '''
        Uses latest operating empty weight and fuel weight fractions, computes gross takeoff weight
        
            Parameters:
                ac (Aircraft): aircraft object
                n (int): iteration number
                
            Returns:
                W0 (float): new gross takeoff weight
        '''

        # Reassignment for clarity
        profile = ac.profile
        LD_max = ac.LD_max_approx
        SFC = ac.SFC_approx

        # Iterate n times
        for i in range(n):

            # Equation S 1.1-3 - Note that weight fractions computed in the configuration class
            ac.W0 = ac.fixed_weight / (1 - ac.WfW0(ac.profile, ac.LD_max_approx, ac.SFC_approx) - ac.WeW0(ac.W0))
