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

from libraries import Aircraft, mach_to_speed
from libraries import ureg as u

import streamlit as st
from streamlit import session_state as sesh
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# Set up the page config
st.set_page_config(page_title="PyAVD",
                    page_icon="https://ichef.bbci.co.uk/news/976/cpsprodpb/117D1/production/_98633617_mediaitem98633616.jpg",
                    layout="centered")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            footer:after {
            content:'Aerospace Vehicle Design 2021 - Department of Aeronautics - Imperial College London'; 
            visibility: visible;
            display: block;
            position: relative;
            #background-color: red;
            padding: 5px;
            top: 2px;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


"""
# PyAVD - The *Cool* Aircraft Designer

---

## What is PyAVD?

PyAVD, or *Pythonic Aerospace Vehicle Designer* is a Python app designed to guide you through the aircraft design process at a conceptual level (and eventually scale to higher fidelity methods).

This is part of the Imperial Aeronautics AVD project submission for Group 11.

### Authors
"""

with st.expander("Click to Expand"):
    st.markdown("<i><p style='text-align: center; color: white;'>Raihaan Usman - Luis Marques - Gabisanth Seyon - Ruairidh Scott-Brown - Chung-Hsun Chang Chien - Adem Bououdine</p></i>", unsafe_allow_html=True)

"""
---
## Designing an Aircraft - The Process
"""

with st.expander("Click to Expand"):
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

  with st.expander("Click to Expand"):
    passengers = st.number_input("Passengers", value=4, min_value=1, max_value=1000)
    crew = st.number_input("Crew", value=2, min_value=1, max_value=1000)
    sesh.num_iters = st.number_input("Iterations", value=10, min_value=0)
    aspect_ratio = st.number_input("Aspect Ratio", value=7.5, min_value=0.0)
    winglets_bool = st.checkbox('Winglets?', value=True)

  st.header("Design Constraints")
  with st.expander("Click to Expand"):
    oswald = st.number_input("Oswald Efficiency", value=0.9, min_value=0.0, max_value=1.0)     
    field_length = st.number_input("Field Length (meters)", value = 1200, min_value=0) * u.m
    cl_max = st.number_input("Cl Max", value=2.1)
    cl_clean = st.number_input("Cl Clean", value=1.5)
    max_Vstall = st.number_input("Max V_Stall (kts)", value=100) * u.kts

  st.header("Optimise Design Point")
  with st.expander("Click to Expand", expanded=True):
    dp_factor = st.number_input("Design Point Percentage", value=0.4)
    st.warning("Still in development!")
    weight = st.slider("Weighting", value=0.0, min_value=0.0, max_value=1.0)
    st.write("Objective Function:")
    st.write(r"$min$(" + str(weight) + r"$\cdot\frac{S_{ref}}{W_0}$ + " + str(round(1.0-weight, 2)) + r"$\cdot\frac{T_0}{W_0})$")


# Hardcoding at the moment
if 'flight_profile' not in sesh:
  sesh.flight_profile = [["Takeoff"],
                          ["Climb"],
                          #["Cruise", {"Speed": 221.320287 * u.m / u.s, "Range": 2500.0 * u.km, "Altitude": 40000.0 * u.ft}],
                          ["Cruise", {"Speed": mach_to_speed((40000 * u.ft).to(u.m).magnitude, 0.75), "Range": 2500.0 * u.km, "Altitude": 40000.0 * u.ft}],
                          ["Descent"],
                          ["Climb"],
                          #["Cruise", {"Speed": 200 * u.kts, "Range": 370.0 * u.km, "Altitude": 26000.0 * u.ft}],
                          ["Cruise", {"Speed": mach_to_speed((26000 * u.ft).to(u.m).magnitude, 0.4), "Range": 370.0 * u.km, "Altitude": 26000.0 * u.ft}],
                          ["Loiter", {"Endurance": 45 * u.min, "Altitude": 5000 * u.ft, "Speed": 150 * u.kts}],
                          ["Descent"],
                          ["Landing"]]

  # # Cessna Citation Mustang
  # sesh.flight_profile = [["Takeoff"],
  #                         ["Climb"],
  #                         #["Cruise", {"Speed": 221.320287 * u.m / u.s, "Range": 2500.0 * u.km, "Altitude": 40000.0 * u.ft}],
  #                         ["Cruise", {"Speed": mach_to_speed((41000 * u.ft).to(u.m).magnitude, 0.59), "Range": 2161.0 * u.km, "Altitude": 41000.0 * u.ft}],
  #                         ["Descent"],
  #                         ["Climb"],
  #                         #["Cruise", {"Speed": 200 * u.kts, "Range": 370.0 * u.km, "Altitude": 26000.0 * u.ft}],
  #                         ["Cruise", {"Speed": mach_to_speed((26000 * u.ft).to(u.m).magnitude, 0.5), "Range": 370.0 * u.km, "Altitude": 26000.0 * u.ft}],
  #                         ["Loiter", {"Endurance": 45 * u.min, "Altitude": 5000 * u.ft, "Speed": 150 * u.kts}],
  #                         ["Descent"],
  #                         ["Landing"]]



# col1, col2, col3, col4 = st.columns(4)

# with col1:
#   add_climb = st.button("Add Climb")

#   if add_climb:
#     sesh.flight_profile.insert(-1, "Climb")

# # Needs Breguet range
# with col2:
#   add_cruise = st.button("Add Cruise")

#   if add_cruise:
#     altitude = float(input("Cruise altitude (ft): ")) * u.ft
#     mach = float(input("Cruise speed (Mach): "))
#     speed = mach_to_speed(altitude.to(u.m).magnitude, mach)
#     segment_range = float(input("Cruise range (km): ")) * u.km
#     sesh.flight_profile.insert(-1, ["Cruise", {"Speed": speed, "Range": segment_range, "Altitude": altitude}])

# # Needs Breguet endurance
# with col3:
#   add_loiter = st.button("Add Loiter")

#   if add_loiter:
#     endurance = float(input("Endurance (min): ")) * u.min
#     altitude = float(input("Loiter altitude (ft): ")) * u.ft
#     mach = float(input("Loiter speed (Mach): ")) 
#     speed = mach_to_speed(altitude.to(u.m).magnitude, mach)
#     sesh.flight_profile.insert(-1, ["Loiter", {"Endurance": endurance, "Altitude": altitude, "Speed": speed}])

# with col4:
#   add_descent = st.button("Add Descent")
#   if add_descent:
#     sesh.flight_profile.insert(-1, "Descent")


fp.write(sesh.flight_profile)


'''
---
## S1 - Initial Sizing
'''

# Creating a new Aircraft instance
ac = Aircraft(passengers, crew, sesh.flight_profile, aspect_ratio, oswald, field_length, max_Vstall, cl_max, cl_clean, weight, dp_factor, winglets_bool, sesh.num_iters)

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


# TODO: use LATEX
st.write("L/D max = " + str(np.round(ac.LDmax,1)))
st.write(f"Effective AR = {np.round(ac.aspect_ratio,1)}")

ac_pie_labels = 'Payload', 'Empty', 'Fuel'
ac_pie_sizes = [(ac.Wcrew.magnitude + ac.Wpax.magnitude + ac.Wpay.magnitude), (ac.W0.magnitude * ac.empty_weight_fraction.magnitude[0]), (ac.W0 * ac.fuel_weight_fraction[0]).magnitude]
ac_pie_fig, ac_pie_ax = plt.subplots()

ac_pie_ax.pie(ac_pie_sizes, labels=ac_pie_labels, autopct='%1.1f%%', shadow=True, startangle=90)
ac_pie_ax.axis('equal')

st.pyplot(ac_pie_fig)
st.write(f"Payload weight fraction = {np.round((1-ac.fuel_weight_fraction - ac.empty_weight_fraction).magnitude,4)[0]}, Empty weight fraction = {np.round(ac.empty_weight_fraction.magnitude,4)[0]}, Fuel weight fraction = {np.round(ac.fuel_weight_fraction.magnitude,4)[0]}")
st.write(f"Payload weight = {ac.Wcrew.magnitude + ac.Wpax.magnitude + ac.Wpay.magnitude} kg, Empty weight = {np.round(ac.W0.magnitude * ac.empty_weight_fraction.magnitude,2)[0]} kg, Fuel Weight = {np.round(ac.W0 * ac.fuel_weight_fraction.magnitude,2)[0]} kg")

'''
## S2 - Constraints

'''

st.pyplot(ac.fig_constraint, dpi=500)
ac.fig_constraint.savefig("constraint.png", dpi=500, bbox_inches='tight')
st.write("Design Point: W/S = " + str(int(np.round(ac.x_designPoint[0]))) + " & T/W = " + str(np.round(ac.y_designPoint[0],2)))
