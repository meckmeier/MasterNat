import streamlit as st
import pandas as pd
import os
import geopy
from geopy.geocoders import Nominatim
from urllib.parse import urlparse

# Setup
CSV_PATH = "VolOpp2.csv"
AUTHORIZED_USERS = ["mary@eckmeier.com"]  # Replace with real user emails
geolocator = Nominatim(user_agent="volunteer_locator")

# Load existing data
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    df = pd.DataFrame(columns=[
        "Organization", "OrgURL", "VolunteerListing", "Region", "County", "City",
        "About", "Stewardship", "Education", "Citizen Science", "Wildlife",
        "Plants", "Birds", "Land Use", "latitude", "longitude"
    ])

# Auth (basic method using Streamlit secrets or session state)
user_email = st.text_input("Enter your email to add a new listing")
if user_email not in AUTHORIZED_USERS:
    st.warning("You are not authorized to add listings.")
    st.stop()

# --- Form ---
with st.form("add_row_form"):
    st.header("Add New Volunteer Opportunity")

    org = st.text_input("Organization (must be unique)")
    if org in df["Organization"].values:
        st.error("Organization already exists.")
        st.stop()

    org_url = st.text_input("Organization URL")
    listing_url = st.text_input("Volunteer Listing URL")

    region = st.selectbox("Region", ["South", "Southeast", "North", "Northeast"])
    wisconsin_counties = sorted(["Dane", "Barron", "Dunn"])  # Fill this with a list of WI counties
    county = st.selectbox("County", wisconsin_counties)
    city = st.text_input("City")

    about = st.text_area("About", max_chars=1000)

    # Checkboxes for categories
    stewardship = st.checkbox("Stewardship")
    education = st.checkbox("Education")
    citizen_science = st.checkbox("Citizen Science")
    wildlife = st.checkbox("Wildlife")
    plants = st.checkbox("Plants")
    birds = st.checkbox("Birds")
    land_use = st.checkbox("Land Use")

    # Submit
    submitted = st.form_submit_button("Submit")
    if submitted:
        # URL validation
    #    def is_valid_url(url):
    #        try:
    #            return bool(urlparse(url).scheme and urlparse(url).netloc)
    #        except:
    #            return False

    #    if not is_valid_url(org_url) or not is_valid_url(listing_url):
    #        st.error("One or both URLs are invalid.")
    #        st.stop()

        # Geocode
        location = geolocator.geocode(f"{city}, {county}, Wisconsin")
        if not location:
            st.error("Could not find coordinates for this location.")
            new_row = {
                "Organization": org,
                "OrgURL": org_url,
                "VolunteerListing": listing_url,
                "Region": region,
                "County": county,
                "City": city,
                "About": about,
                "Stewardship": stewardship,
                "Education": education,
                "Citizen Science": citizen_science,
                "Wildlife": wildlife,
                "Plants": plants,
                "Birds": birds,
                "Land Use": land_use
            }

        else:
            new_row = {
                "Organization": org,
                "OrgURL": org_url,
                "VolunteerListing": listing_url,
                "Region": region,
                "County": county,
                "City": city,
                "About": about,
                "Stewardship": stewardship,
                "Education": education,
                "Citizen Science": citizen_science,
                "Wildlife": wildlife,
                "Plants": plants,
                "Birds": birds,
                "Land Use": land_use,
                "latitude": location.latitude,
                "longitude": location.longitude
            }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_PATH, index=False)
        st.success("New listing added successfully!")
