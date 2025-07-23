import streamlit as st
import pandas as pd
from utils import save_data

def show_view_tab(filtered_df):
    st.subheader("Volunteer Opportunities")
    for _, row in filtered_df.iterrows():
        st.markdown(f"### [{row['Organization']}]({row['VolunteerListing']})")
        st.text(f"{row['City']}, {row['County']}")
        st.write(row['About'])
        st.markdown("---")

def show_data_tab(filtered_df, csv_path):
    df = st.session_state.full_df

    if "delete_pending" not in st.session_state:
        st.session_state.delete_pending = None

    st.subheader("Manage Opportunities")

    for i, row in filtered_df.iterrows():
        original_idx = int(row["OriginalIndex"])
        cols = st.columns([3, 1])
        cols[0].markdown(f"**{row['Organization']}** — {row['City']}, {row['County']}")
        if st.session_state.delete_pending != original_idx:
            if cols[1].button("🗑️ Delete", key=f"delete_{original_idx}"):
                st.session_state.delete_pending = original_idx
                st.rerun()
        else:
            with cols[1]:
                st.warning("Confirm delete?")
                if st.button("✅ Yes", key=f"confirm_{original_idx}"):
                    df = df[df["OriginalIndex"] != original_idx].reset_index(drop=True)
                    st.session_state.full_df = df
                    save_data(df, csv_path)
                    st.session_state.delete_pending = None
                    st.success("Deleted")
                    st.rerun()
                if st.button("❌ Cancel", key=f"cancel_{original_idx}"):
                    st.session_state.delete_pending = None
                    st.rerun()

def show_add_tab(csv_path):
    df = st.session_state.full_df
    st.subheader("Add Opportunity")
    with st.form("add_form"):
        org = st.text_input("Organization (must be unique)")
        org_url = st.text_input("Organization URL")
        listing_url = st.text_input("Volunteer Listing URL")
        city = st.text_input("City")
        county = st.text_input("County")
        region = st.selectbox("Region", ["South", "Southeast", "North", "Northeast"])
        about = st.text_area("About")

        stewardship = st.checkbox("Stewardship")
        education = st.checkbox("Education")
        citizen_science = st.checkbox("Citizen Science")

        submitted = st.form_submit_button("Add Listing")

        if submitted:
            if org in df["Organization"].values:
                st.error("Organization already exists.")
                return

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
                "Citizen Science": citizen_science
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.reset_index(inplace=True)
            df.rename(columns={"index": "OriginalIndex"}, inplace=True)
            st.session_state.full_df = df
            save_data(df, csv_path)
            st.success("Listing added!")
            st.rerun()
