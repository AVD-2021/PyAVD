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

import streamlit as st
from streamlit import session_state as sesh
from libraries import Aircraft, ureg, mach_to_speed
import numpy as np
import plotly.express as px


# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")

"""
# PyAVD
### By AVD Group 11, Department of Aeronautics, Imperial College London
"""

with st.sidebar:
  with st.expander("Initial Sizing", expanded=True):
    passengers = st.number_input("Number of passengers", value=4, min_value=1, max_value=1000)
    crew = st.number_input("Number of crew", value=2, min_value=1, max_value=1000)
    num_iters = st.number_input("Number of iterations", value=10, min_value=0)
    aspect_ratio = st.number_input("Aspect Ratio", value=7.5, min_value=0.0)

    st.markdown("## Target Flight Profile")
    # flight_profile = st.multiselect("Flight profile", ["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"],
    #                                         default=["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"])


  with st.expander("Design Constraints"):
    oswald = st.number_input("Oswald Efficiency", value=0.9, min_value=0.0, max_value=1.0)     
    field_length = st.number_input("Field Length (meters)", value = 1200, min_value=0) * ureg.m
    cl_max = st.number_input("Cl Max", value=2.1)
    cl_clean = st.number_input("Cl Clean", value=1.5)
    max_Vstall = st.number_input("Max V_Stall (kts)", value=100) * ureg.kts


# Initialise the target flight profile
if 'flight_profile' not in sesh:
  sesh.flight_profile = [["Takeoff"],
                          "Climb",
                          ["Cruise", {"Speed": 221.320287 * ureg.m / ureg.s, "Range": 2500.0 * ureg.km, "Altitude": 40000.0 * ureg.ft}],
                          # ["Cruise", {"Speed": mach_to_speed((40000 * ureg.ft).to(ureg.m).magnitude, 0.75), "Range": 2500.0 * ureg.km, "Altitude": 40000.0 * ureg.ft}],
                          "Descent",
                          "Climb",
                          ["Cruise", {"Speed": 200 * ureg.kts, "Range": 370.0 * ureg.km, "Altitude": 26000.0 * ureg.ft}],
                          ["Loiter", {"Endurance": 45 * ureg.min, "Altitude": 5000 * ureg.ft, "Speed": 150 * ureg.kts}],
                          "Descent",
                          ["Landing"]]


col1, col2, col3, col4 = st.columns(4)

with col1:
  add_climb = st.button("Add Climb")

  if add_climb:
    sesh.flight_profile.insert(-1, "Climb")

# Needs Breguet range
with col2:
  add_cruise = st.button("Add Cruise")

  if add_cruise:
    altitude = float(input("Cruise altitude (ft): ")) * ureg.ft
    mach = float(input("Cruise speed (Mach): "))
    speed = mach_to_speed(altitude.to(ureg.m).magnitude, mach)
    segment_range = float(input("Cruise range (km): ")) * ureg.km
    sesh.flight_profile.insert(-1, ["Cruise", {"Speed": speed, "Range": segment_range, "Altitude": altitude}])

# Needs Breguet endurance
with col3:
  add_loiter = st.button("Add Loiter")

  if add_loiter:
    endurance = float(input("Endurance (min): ")) * ureg.min
    altitude = float(input("Loiter altitude (ft): ")) * ureg.ft
    mach = float(input("Loiter speed (Mach): ")) 
    speed = mach_to_speed(altitude.to(ureg.m).magnitude, mach)
    sesh.flight_profile.insert(-1, ["Loiter", {"Endurance": endurance, "Altitude": altitude, "Speed": speed}])

with col4:
  add_descent = st.button("Add Descent")
  if add_descent:
    sesh.flight_profile.insert(-1, "Descent")


with st.expander("Raw Flight Profile"):
  a = st.write(sesh.flight_profile)


'''
# S1 - Initial Sizing

'''

# Creating a new Aircraft instance
ac = Aircraft(passengers, crew, sesh.flight_profile, aspect_ratio, oswald, field_length, max_Vstall, cl_max, cl_clean, num_iters)


# st.header("$W_0$ vs Iteration")
st.line_chart(ac.W0_histories) # TODO: Add labels

st.plotly_chart(ac.fig_W0_histories)

# TODO: do other method of S1

st.write(ac.weight_frac_histories)


'''
# S2 - Constraints

'''


st.write(ac.fig_constraint)