
'''
Aircraft class definition for PyAVD

- Inherits from superclasses Spec(), BaselineConfig() and Constraints()

'''

from libraries.Aircraft.Spec import Spec
from libraries.Aircraft.BaselineConfig import BaselineConfig as Config
from libraries.Aircraft.Constraints import Constraints


class Aircraft(Spec, Config, Constraints):

    def __init__(ac):
        # Initialize superclasses
        Spec.__init__(ac)
        Config.__init__(ac)
        Constraints.__init__(ac)

        # On first iteration, approximate aircraft W0 from Baseline Configuration
        ac.W0 = Config.W0_approx(ac)


    def iterate_W0(ac, n):
        '''
        Uses latest operating empty weight and fuel weight fractions to compute gross takeoff weight
        '''

        # Reassignment for clarity
        profile = Spec.profile
        LD_max = Config.LD_max_approx()
        SFC = Config.SFC_approx()

        # Iterate n times
        for i in range(n):

            # Equation S 1.1-3 - Note that weight fractions computed in the configuration class
            ac.W0 = ac.Spec.fixed_weight / (1 - ac.Config.WfW0(profile, LD_max, SFC) - ac.Config.WeW0(ac.W0))

