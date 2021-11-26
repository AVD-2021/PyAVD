import matplotlib.pyplot as plt
import numpy as np

# This is just some simple calculations to help with avd

# Parameters of the aircraft 

height_40 = {"density": 0.302748958,
             "a": 294.9, 
             "dynamic_viscosity": 1.43e-5,
             "gravity": 9.7691448}

mach = 0.78
length_scale = 0
payload_mass = 692
fuel_mass = 1351
empty_mass = 3021
aspect_ratio = 9 #! note that the addition of winglets will change the effective aspect ratio
CL = 0.3 #! note that this should probably change at when the exact aerofoil is chosen
wing_loading = 2227


weight_full_mass = (payload_mass + fuel_mass + empty_mass)*height_40["gravity"]
weight_cruise_start = (payload_mass + ((fuel_mass*0.970)*0.985) + empty_mass)*height_40["gravity"]
velocity = mach*height_40["a"]

wing_area_full_mass = weight_cruise_start / (0.5*height_40["density"]*velocity**2 * CL)
wing_area_cruise_start = weight_full_mass / (0.5*height_40["density"]*velocity**2 * CL)
wing_area_wing_loading_full_mass = weight_full_mass/wing_loading
wing_area_wing_loading_cruise_start = weight_cruise_start / wing_loading

wing_span_full_mass = (wing_area_full_mass*aspect_ratio)**(0.5)
wing_span_cruise_start = (wing_area_cruise_start*aspect_ratio)**(0.5)

reynolds_full_mass = (height_40["density"]*velocity*wing_span_full_mass)/ height_40["dynamic_viscosity"]
reynolds_cruise_start = (height_40["density"]*velocity*wing_span_cruise_start)/ height_40["dynamic_viscosity"]


CL_wing_area_wing_loading_full_mass = weight_full_mass/(0.5*height_40["density"]*velocity**2 * wing_area_wing_loading_full_mass)
CL_wing_area_wing_loading_cruise_start = weight_cruise_start/(0.5*height_40["density"]*velocity**2 *wing_area_wing_loading_cruise_start)



