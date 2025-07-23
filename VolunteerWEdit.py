import pandas as pd
import folium 
import streamlit as st
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import os

geolocator = Nominatim(user_agent="streamlit-volunteer-app")
CSV_PATH = "VolOpp2.csv"

# --- Initialize session state
if "full_df" not in st.session_state:
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        if "OriginalIndex" not in df.columns:
            df.reset_index(inplace=True)
            df.rename(columns={"index": "OriginalIndex"}, inplace=True)
        st.session_state.full_df = df
    else:
        st.session_state.full_df = pd.DataFrame(columns=[
            "Organization", "OrgURL", "VolunteerListing", "Region", "County", "City",
            "About", "Stewardship", "Education", "Citizen Science",
            "Wildlife", "Plants", "Birds", "Land Use",
            "latitude", "longitude", "OriginalIndex"
        ])

df = st.session_state.full_df.copy()

# --- UI Setup
st.set_page_config(layout="wide")
st.title("🗺️ Volunteer Opportunities")

# --- Sidebar Filters
with st.sidebar:
    st.header("🔍 Filter Options")

    text_inputs = {col: st.text_input(f"Search '{col}'") for col in ["Organization", "About"]}
    dropdown_inputs = {col: st.multiselect(f"Filter by '{col}'", sorted(df[col].dropna().unique()))
                       for col in ["Region", "County"]}
    checkbox_inputs = {col: st.checkbox(col, value=False) for col in ["Stewardship", "Education", "Citizen Science"]}

# --- Apply Filters
filtered_df = df.copy()
for col, val in text_inputs.items():
    if val:
        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(val, case=False, na=False)]

for col, selected in dropdown_inputs.items():
    if selected:
        filtered_df = filtered_df[filtered_df[col].isin(selected)]

for col, checked in checkbox_inputs.items():
    if checked:
        filtered_df = filtered_df[filtered_df[col] == True]

st.markdown(f"### {len(filtered_df)} matching organization(s)")

# --- Download
csv_download = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Filtered Results", data=csv_download, file_name="filtered_organizations.csv", mime="text/csv")

# --- View toggle
view_option = st.radio("Choose view:", ["Cards", "Map", "Data", "Add"], horizontal=True)

# --- MAP
if view_option == "Map":
    map_df = filtered_df.dropna(subset=["latitude", "longitude"])
    m = folium.Map(location=[44.5, -89.5], zoom_start=7)
    m.fit_bounds([[42.49, -92.89], [47.31, -86.25]])

    for _, row in map_df.iterrows():
        popup_html = f"""
        <div style="font-size: 14px;">
            <b>{row['Organization']}</b><br>
            <i>{row['City']}</i><br>
            <a href="{row['OrgURL']}" target="_blank">Visit Website</a>
        </div>
        """
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=250),
            icon=folium.Icon(icon='leaf', prefix='fa', color='darkgreen')
        ).add_to(m)

    st_folium(m, width=700, height=500)

# --- CARDS
elif view_option == "Cards":
    if filtered_df.empty:
        st.info("No matching organizations found.")
    else:
        for _, row in filtered_df.iterrows():
            with st.container():
                st.markdown("---")
                cols = st.columns([1, 2])
                with cols[0]:
                    st.subheader(row['Organization'])
                    st.caption(f"{row['City']}, {row['County']}")
                    if pd.notna(row['OrgURL']):
                        st.markdown(f"[🌐 Website]({row['OrgURL']})", unsafe_allow_html=True)
                    if pd.notna(row['VolunteerListing']):
                        st.markdown(f"[🤝 Volunteer Listing]({row['VolunteerListing']})", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"**About:** {row['About']}")
                    tags = [f"`{col}`" for col in checkbox_inputs if row.get(col)]
                    if tags:
                        st.markdown("**Focus Areas:** " + " ".join(tags))

# --- DATA
elif view_option == "Data":
    if "delete_pending" not in st.session_state:
        st.session_state.delete_pending = None

    full_df = st.session_state.full_df

    header_cols = st.columns([2, 1, 1, 2, 1])
    header_cols[0].markdown("**Organization**")
    header_cols[1].markdown("**City**")
    header_cols[2].markdown("**County**")
    header_cols[3].markdown("**Topics**")
    header_cols[4].markdown("**Action**")

    for _, row in full_df.iterrows():
        original_idx = int(row["OriginalIndex"])
        topics = " | ".join([t for t in checkbox_inputs if row.get(t)])

        cols = st.columns([2, 1, 1, 2, 1])
        cols[0].markdown(f"[{row['Organization']}]({row['VolunteerListing']})")
        cols[1].markdown(row['City'])
        cols[2].markdown(row['County'])
        cols[3].markdown(topics)

        if st.session_state.delete_pending != original_idx:
            if cols[4].button("🗑️", key=f"delete_{original_idx}"):
                st.session_state.delete_pending = original_idx
                st.rerun()
        else:
            with cols[4]:
                st.warning("Confirm?")
                if st.button("✅ Yes", key=f"confirm_{original_idx}"):
                    st.session_state.full_df = full_df[full_df["OriginalIndex"] != original_idx].reset_index(drop=True)
                    st.session_state.full_df.reset_index(inplace=True)
                    st.session_state.full_df.rename(columns={"index": "OriginalIndex"}, inplace=True)
                    st.session_state.full_df.to_csv(CSV_PATH, index=False)
                    st.session_state.delete_pending = None
                    st.success(f"Deleted {row['Organization']}")
                    st.rerun()
                if st.button("❌ Cancel", key=f"cancel_{original_idx}"):
                    st.session_state.delete_pending = None
                    st.rerun()

# --- ADD
elif view_option == "Add":
    AUTHORIZED_USERS = ["mary@eckmeier.com"]
    email = st.text_input("Enter your email to add a new listing")
    if email not in AUTHORIZED_USERS:
        st.warning("You are not authorized to add listings.")
        st.stop()

    with st.form("add_row_form"):
        st.header("Add New Volunteer Opportunity")
        full_df = st.session_state.full_df

        org = st.text_input("Organization (must be unique)")
        if org in full_df["Organization"].values:
            st.error("Organization already exists.")
            st.stop()

        org_url = st.text_input("Organization URL")
        listing_url = st.text_input("Volunteer Listing URL")
        region = st.selectbox("Region", ["South", "Southeast", "North", "Northeast"])
        county = st.selectbox("County", sorted(["Dane", "Barron", "Dunn"]))
        city = st.text_input("City")
        about = st.text_area("About", max_chars=1000)

        # Category checkboxes
        categories = {label: st.checkbox(label) for label in
                      ["Stewardship", "Education", "Citizen Science", "Wildlife", "Plants", "Birds", "Land Use"]}

        submitted = st.form_submit_button("Submit")
        if submitted:
            location = geolocator.geocode(f"{city}, {county}, Wisconsin")
            new_row = {
                "Organization": org,
                "OrgURL": org_url,
                "VolunteerListing": listing_url,
                "Region": region,
                "County": county,
                "City": city,
                "About": about,
                **categories
            }
            if location:
                new_row["latitude"] = location.latitude
                new_row["longitude"] = location.longitude

            full_df = pd.concat([full_df, pd.DataFrame([new_row])], ignore_index=True)
            full_df.reset_index(inplace=True)
            full_df.rename(columns={"index": "OriginalIndex"}, inplace=True)

            full_df.to_csv(CSV_PATH, index=False)
            st.session_state.full_df = full_df
            st.success("New listing added successfully!")
            st.rerun()
