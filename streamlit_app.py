import streamlit as st
import pandas as pd
import papermill as pm
import pickle
import os
import warnings

# Suppress DeprecationWarning from papermill date parsing
warnings.filterwarnings("ignore", category=DeprecationWarning, module="papermill")

# Streamlit page configuration
st.set_page_config(page_title="Doctor Finder", layout="wide")

# Custom CSS for purple gradient theme and layout
st.markdown("""
    <style>
    .main { background: linear-gradient(to bottom, #6b7280, #a78bfa); }
    .stSelectbox > div > select { font-size: 16px; padding: 10px; border-radius: 8px; }
    .stButton > button {
        background: linear-gradient(to right, #7c3aed, #c084fc);
        color: white; font-size: 18px; padding: 10px 20px; border-radius: 8px;
    }
    .stDataFrame { border: 2px solid #7c3aed; border-radius: 8px; }
    h1, h2, h3 { color: #ffffff; text-shadow: 1px 1px 2px #4b5563; }
    </style>
""", unsafe_allow_html=True)

# Load dataset for dropdowns
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("panel_data.xlsx")
        return df
    except FileNotFoundError:
        st.error("Error: panel_data.xlsx not found. Please ensure it is in the same directory.")
        return None

df = load_data()
if df is None:
    st.stop()

# Get unique specialties and regions
specialties = sorted(df['Speciality'].unique())
regions = sorted(df['Region'].unique())
regions = ['All Regions'] + regions

# Title
st.title("Doctor Finder")

# Input form
with st.form(key="doctor_search"):
    speciality = st.selectbox("Specialty (required)", specialties, placeholder="e.g., Cardiology")
    region = st.selectbox("Region (optional)", regions, placeholder="e.g., Northeast")
    submit_button = st.form_submit_button(label="Search")

# Execute notebook and display results
if submit_button:
    if not speciality:
        st.error("Please select a specialty.")
    else:
        # Prepare parameters for test1.ipynb
        params = {
            "speciality": speciality,
            "region": region if region != 'All Regions' else None
        }
        
        # Execute the notebook
        output_notebook = "output.ipynb"
        pickle_file = "output.pkl"
        try:
            pm.execute_notebook(
                "test1.ipynb",
                output_notebook,
                parameters=params,
                kernel_name="python3"
            )
            
            # Check for pickle file
            if os.path.exists(pickle_file):
                try:
                    with open(pickle_file, 'rb') as f:
                        regions_df_list, region_names = pickle.load(f)
                    
                    if not regions_df_list or not any(len(df) > 0 for df in regions_df_list):
                        st.warning(f"No doctors found for speciality: {speciality}" + 
                                  (f" and region: {region}" if region and region != 'All Regions' else ""))
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
                except Exception as e:
                    st.error(f"Error reading results: {str(e)}. Ensure test1.ipynb saves valid output.pkl.")
                finally:
                    # Clean up
                    if os.path.exists(pickle_file):
                        os.remove(pickle_file)
                    if os.path.exists(output_notebook):
                        os.remove(output_notebook)
            else:
                st.error("No results found. Ensure test1.ipynb saves output to output.pkl.")
        except pm.PapermillExecutionError as e:
            st.error(f"Notebook execution failed: {str(e)}. Check test1.ipynb for errors.")
        except FileNotFoundError:
            st.error("Error: test1.ipynb not found. Please ensure it is in the same directory.")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
