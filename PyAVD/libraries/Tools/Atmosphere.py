from ambiance import Atmosphere
from .. import ureg

def mach_to_speed(altitude, mach):
    """
    Converts Mach number to speed as a function of altitude (m).
    """
    print(Atmosphere(altitude).speed_of_sound)
    return Atmosphere(altitude).speed_of_sound * (ureg.m/ureg.s) * mach