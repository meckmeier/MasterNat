import pandas as pd
import os

def load_data(csv_path):
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        if "OriginalIndex" not in df.columns:
            df.reset_index(inplace=True)
            df.rename(columns={"index": "OriginalIndex"}, inplace=True)
        return df
    else:
        return pd.DataFrame()  # handle gracefully

def save_data(df, csv_path):
    df.drop(columns=["OriginalIndex"], errors="ignore").to_csv(csv_path, index=False)

def filter_data(df):
    import streamlit as st
    region_filter = st.sidebar.multiselect("Region", df["Region"].unique())
    if region_filter:
        df = df[df["Region"].isin(region_filter)]
    # Add more filters here...
    return df
