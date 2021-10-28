"""
  _____           __      _______  
 |  __ \         /\ \    / /  __ \ 
 | |__) |   _   /  \ \  / /| |  | |
 |  ___/ | | | / /\ \ \/ / | |  | |
 | |   | |_| |/ ____ \  /  | |__| |
 |_|    \__, /_/    \_\/   |_____/           |
         __/ |                               |
        |___/                                |
                                           .-'-.
                                          ' ___ '
                                ---------'  .-.  '---------
                _________________________'  '-'  '_________________________
                 ''''''-|---|--/    \==][^',_m_,'^][==/    \--|---|-''''''
                               \    /  ||/   H   \||  \    /
                                '--'   OO   O|O   OO   '--'

PyAVD - A Python package to pretty much -solve- aircraft conceptual design!


AVD Group 11, Department of Aeronautics, Imperial College London.

"""

from libraries import Aircraft, ureg, mach_to_speed

import streamlit as st
from streamlit import session_state as sesh
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")


"""
# PyAVD - A Cool Aircraft Designer

---

## What is PyAVD?

PyAVD, or *Pythonic Aerospace Vehicle Designer* is a Python app designed to guide you through the aircraft design process at a conceptual level (and eventually scale to higher fidelity methods).

This is part of the Imperial Aeronautics AVD project submission for Group 11.
> *Raihaan Usman, Luis Marques, Ruairidh Scott-Brown, Gabisanth Seyon, Adem Bououdine*

---
## Designing an Aircraft - The Process
"""

with st.expander("Click to expand"):
    """
    TODO
    """

"""
---
## SPEC - Specification
"""

with st.expander("Parsed Flight Profile"):
  fp = st.empty()


with st.sidebar:
  st.header("Initial Sizing")

  with st.expander("Click to Expand", expanded=True):
    passengers = st.number_input("Passengers", value=4, min_value=1, max_value=1000)
    crew = st.number_input("Crew", value=2, min_value=1, max_value=1000)
    num_iters = st.number_input("Iterations", value=10, min_value=0)
    aspect_ratio = st.number_input("Aspect Ratio", value=7.5, min_value=0.0)

  st.header("Design Constraints")
  with st.expander("Click to Expand"):
    oswald = st.number_input("Oswald Efficiency", value=0.9, min_value=0.0, max_value=1.0)     
    field_length = st.number_input("Field Length (meters)", value = 1200, min_value=0) * ureg.m
    cl_max = st.number_input("Cl Max", value=2.1)
    cl_clean = st.number_input("Cl Clean", value=1.5)
    max_Vstall = st.number_input("Max V_Stall (kts)", value=100) * ureg.kts

# Hardcoding for the moment
if 'flight_profile' not in sesh:
  sesh.flight_profile = [["Takeoff"],
                          ["Climb"],
                          #["Cruise", {"Speed": 221.320287 * ureg.m / ureg.s, "Range": 2500.0 * ureg.km, "Altitude": 40000.0 * ureg.ft}],
                          ["Cruise", {"Speed": mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.75), "Range": 2500.0 * ureg.km, "Altitude": 40000.0 * ureg.ft}],
                          ["Descent"],
                          ["Climb"],
                          #["Cruise", {"Speed": 200 * ureg.kts, "Range": 370.0 * ureg.km, "Altitude": 26000.0 * ureg.ft}],
                          ["Cruise", {"Speed": mach_to_speed((26000 * ureg.ft).to(ureg.m).magnitude, 0.5), "Range": 370.0 * ureg.km, "Altitude": 26000.0 * ureg.ft}],
                          ["Loiter", {"Endurance": 45 * ureg.min, "Altitude": 5000 * ureg.ft, "Speed": 150 * ureg.kts}],
                          ["Descent"],
                          ["Landing"]]

# col1, col2, col3, col4 = st.columns(4)

# with col1:
#   add_climb = st.button("Add Climb")

#   if add_climb:
#     sesh.flight_profile.insert(-1, "Climb")

# # Needs Breguet range
# with col2:
#   add_cruise = st.button("Add Cruise")

#   if add_cruise:
#     altitude = float(input("Cruise altitude (ft): ")) * ureg.ft
#     mach = float(input("Cruise speed (Mach): "))
#     speed = mach_to_speed(altitude.to(ureg.m).magnitude, mach)
#     segment_range = float(input("Cruise range (km): ")) * ureg.km
#     sesh.flight_profile.insert(-1, ["Cruise", {"Speed": speed, "Range": segment_range, "Altitude": altitude}])

# # Needs Breguet endurance
# with col3:
#   add_loiter = st.button("Add Loiter")

#   if add_loiter:
#     endurance = float(input("Endurance (min): ")) * ureg.min
#     altitude = float(input("Loiter altitude (ft): ")) * ureg.ft
#     mach = float(input("Loiter speed (Mach): ")) 
#     speed = mach_to_speed(altitude.to(ureg.m).magnitude, mach)
#     sesh.flight_profile.insert(-1, ["Loiter", {"Endurance": endurance, "Altitude": altitude, "Speed": speed}])

# with col4:
#   add_descent = st.button("Add Descent")
#   if add_descent:
#     sesh.flight_profile.insert(-1, "Descent")


fp.write(sesh.flight_profile)

'''
## S1 - Initial Sizing

'''

# Creating a new Aircraft instance
ac = Aircraft(passengers, crew, sesh.flight_profile, aspect_ratio, oswald, field_length, max_Vstall, cl_max, cl_clean, num_iters)

# Plotting W0 convergence
st.plotly_chart(ac.fig_W0_histories)
print(ac.W0_histories)

# # Matplotlib version for the poster
# st.pyplot(ac.fig_W0_histories)
# ac.fig_W0_histories.savefig("iters.png", dpi=500, bbox_inches='tight')
# st.write(f"$W_0$ converged to {np.round(ac.W0[0], 2)}.")

# Fuel fraction breakdown
with st.expander("Fuel Fraction Breakdown"):
  fuel_frac_2d = [ [j[0], ac.fuel_fracs[i]] for i, j in enumerate(sesh.flight_profile) ]
  st.dataframe( pd.DataFrame(fuel_frac_2d, index=np.arange(1,len(fuel_frac_2d)+1), columns=['Flight Regime','Fuel Fraction']) )


'''
## S2 - Constraints

'''

st.pyplot(ac.fig_constraint, dpi=500)
ac.fig_constraint.savefig("constraint.png", dpi=500, bbox_inches='tight')
