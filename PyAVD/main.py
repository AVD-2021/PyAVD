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
from libraries import Aircraft, ureg
from libraries.Tools import speed_of_sound
import pandas as pd
import plotly

# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")

"""
# PyAVD
### By AVD Group 11, Department of Aeronautics, Imperial College London.
"""

with st.sidebar:
  st.markdown("## Number of passengers")
  passengers = st.number_input("Number of passengers", value=4, min_value=1, max_value=1000)

  st.markdown("## Number of crew")
  crew = st.number_input("Number of crew", value=2, min_value=1, max_value=1000)

  # Build a flight profile with multiselect - takeoff, climb, cruise, descent, landing, loiter
  st.markdown("## Number of iterations")
  num_iters = st.number_input("Number of iterations", value=10, min_value=0)

  st.markdown("## Target Flight Profile")
  # flight_profile = st.multiselect("Flight profile", ["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"],
  #                                         default=["Takeoff + Climb", "Cruise 1", "Descent 1", "Climb + Divert", "Cruise 2", "Loiter", "Descent 2", "Landing"])


# Initialise the target flight profile
if 'flight_profile' not in sesh:
  #sesh.flight_profile = [["Takeoff"], ["Landing"]]

  sesh.flight_profile = [["Takeoff"], 
                          "Climb",
                          ["Cruise", {"Speed": 221.320287 * ureg.meter / ureg.second, "Range": 2500.0 * ureg.km, "Altitude": 40000.0 * ureg.ft}],
                          "Descent",
                          "Climb",
                          ["Cruise", {"Speed": 200 * ureg.kts, "Range": 370.0 * ureg.km, "Altitude": 22000.0 * ureg.ft}],
                          ["Loiter", {"Endurance": 45 * ureg.min, "Altitude": 5000 * ureg.ft, "Speed": 150 * ureg.kts}],
                          "Descent",
                          ["Landing"]]

c = st.empty() # placeholder

add_climb = st.button("Add Climb")
if add_climb:
  sesh.flight_profile.insert(-1, "Climb")


# Needs Breguet range
add_cruise = st.button("Add Cruise")
if add_cruise:
  # Streamlit number input for cruise speed
  # speed = c.number_input("Cruise speed (kts)", value=0, min_value=0, max_value=1000)
  altitude = float(input("Cruise altitude (ft): ")) * ureg.ft
  speed = (float(input("Cruise speed (Mach): ")) * speed_of_sound(altitude)).to(ureg.meter / ureg.second)
  segment_range = float(input("Cruise range (km): ")) * ureg.km


  sesh.flight_profile.insert(-1, ["Cruise", {"Speed": speed, "Range": segment_range, "Altitude": altitude}])


# Needs Breguet endurance
add_loiter = st.button("Add Loiter")
if add_loiter:

  endurance = float(input("Endurance (min): ")) * ureg.min
  altitude = float(input("Loiter altitude (ft): ")) * ureg.ft
  speed = float(input("Loiter speed (Mach): "))

  sesh.flight_profile.insert(-1, ["Loiter", {"Endurance": endurance, "Altitude": altitude, "Speed": speed}])


add_descent = st.button("Add Descent")
if add_descent:
  sesh.flight_profile.insert(-1, "Descent")


a = st.write(sesh.flight_profile)


# Create dataframe with the flight profile
# df = pd.DataFrame({"Flight Regime": st.session_state.b[:][:][0]})
# df = pd.DataFrame({""})

# st.dataframe(df)

# Creating a new Aircraft instance
ac = Aircraft(passengers, crew, sesh.flight_profile, num_iters)

st.line_chart(ac.W0_histories)

# "Speed":"<Quantity(221.320287, 'meter / second')>"
# "Range":"<Quantity(2500.0, 'kilometer')>"
# "Altitude":"<Quantity(40000.0, 'foot')>"# [
