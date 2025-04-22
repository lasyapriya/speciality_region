import streamlit as st
import pandas as pd

# Streamlit page configuration
st.set_page_config(page_title="Doctor Finder", layout="wide")

# Custom CSS for purple gradient theme and layout
st.markdown("""
    <style>
    .main { background: linear-gradient(to bottom, #6b7280, #a78bfa); }
    .stTextInput > div > input { font-size: 16px; padding: 10px; border-radius: 8px; }
    .stSelectbox > div > select { font-size: 16px; padding: 10px; border-radius: 8px; }
    .stButton > button {
        background: linear-gradient(to right, #7c3aed, #c084fc);
        color: white; font-size: 18px; padding: 10px 20px; border-radius: 8px;
    }
    .stDataFrame { border: 2px solid #7c3aed; border-radius: 8px; }
    h1, h2 { color: #ffffff; text-shadow: 1px 1px 2px #4b5563; }
    </style>
""", unsafe_allow_html=True)

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_excel("panel_data.xlsx")
    return df

df = load_data()

# Get unique specialties and regions
specialties = sorted(df['Speciality'].unique())
regions = sorted(df['Region'].unique())
regions = ['All Regions'] + regions  # Add option for no region filter

# Title
st.title("Doctor Finder")

# Input form
with st.form(key="doctor_search"):
    specialty = st.selectbox("Specialty (required)", specialties, placeholder="e.g., Cardiology")
    region = st.selectbox("Region (optional)", regions, placeholder="e.g., Northeast")
    submit_button = st.form_submit_button(label="Search")

# Function to filter doctors
def filter_doctors(specialty, region=None):
    speciality_df = df.loc[df['Speciality'] == specialty]
    if not region or region == 'All Regions':
        regions_df_list = [speciality_df.loc[speciality_df['Region'] == r] for r in sorted(speciality_df['Region'].unique())]
        return regions_df_list, sorted(speciality_df['Region'].unique())
    else:
        region_df = speciality_df.loc[speciality_df['Region'] == region]
        return [region_df], [region]

# Display results
if submit_button:
    if not specialty:
        st.error("Please select a specialty.")
    else:
        regions_df_list, region_names = filter_doctors(specialty, region)
        if not any(len(df) > 0 for df in regions_df_list):
            st.warning("No doctors found for the given criteria.")
        else:
            st.subheader("Matching Doctors")
            for reg_df, reg_name in zip(regions_df_list, region_names):
                if len(reg_df) > 0:
                    st.markdown(f"### {reg_name}")
                    st.dataframe(
                        reg_df[['NPI', 'State', 'Usage Time (mins)', 'Region', 'Speciality']],
                        use_container_width=True,
                        column_config={
                            "NPI": st.column_config.NumberColumn(format="%d"),
                            "Usage Time (mins)": st.column_config.NumberColumn(format="%d mins")
                        }
                    )