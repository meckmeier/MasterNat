# volunteer_app/app.py
import streamlit as st
from views import show_view_tab, show_data_tab, show_add_tab
from utils import load_data, filter_data, save_data

CSV_PATH = "VolOpp2.csv"

# Load full dataset once
if "full_df" not in st.session_state:
    st.session_state.full_df = load_data(CSV_PATH)

# Filtered version for display only
filtered_df = filter_data(st.session_state.full_df)

# --- View Option Tabs ---
view_option = st.sidebar.radio("Choose view", ["View", "Data", "Add"])

if view_option == "View":
    show_view_tab(filtered_df)
elif view_option == "Data":
    show_data_tab(filtered_df, CSV_PATH)
elif view_option == "Add":
    show_add_tab(CSV_PATH)
