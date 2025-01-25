
import os
import pandas as pd
import streamlit as st
from io import BytesIO

# Load the data file
@st.cache_data
def load_data(file):
    try:
        data = pd.read_csv(file, encoding='ISO-8859-1', sep=';', on_bad_lines='skip')
        st.write("Data loaded successfully:")
        st.write(data.head())
        return data
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return pd.DataFrame()

# App configuration
st.set_page_config(page_title="Interactive Article Filter", layout="wide")

# Title
st.title("Interactive Article Filter")
st.markdown("Use the filters below to explore and segment the database interactively.")
st.markdown("---")

# Dynamic file upload
uploaded_file = st.file_uploader("Upload your CSV file here", type=["csv"])

# Load default data if no file is uploaded
if uploaded_file is not None:
    data = load_data(uploaded_file)
else:
    default_file = "default_data.csv"  # Replace with your default CSV file name
    if os.path.exists(default_file):
        data = load_data(default_file)
    else:
        st.warning("No file uploaded and default data file not found.")
        data = pd.DataFrame()

if not data.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Publication period filter
    publication_years = ["All", "None"] + sorted(data["Year"].dropna().unique().tolist())
    period_filter = st.sidebar.selectbox("Publication range:", publication_years, index=0)
    
    # Citations filter
    citation_ranges = ["All", "None"] + sorted(data["Cited by"].dropna().unique().tolist())
    citations_filter = st.sidebar.selectbox("Citations range:", citation_ranges, index=0)
    
    # Keywords filter
    keyword_categories = ["All", "None"] + sorted(data["Keywords"].dropna().unique().tolist())
    keywords_filter = st.sidebar.selectbox("Keywords:", keyword_categories, index=0)
    
    exact_match = st.sidebar.checkbox("Exact match", value=False)
    
    # JCR filter
    jcr_options = ["All", "None", "No Q", "Q1", "Q2", "Q3", "Q4"]
    jcr_filter = st.sidebar.selectbox("JCR range:", jcr_options, index=0)
    
    # Knowledge area group filter
    if "Knowledge area group" in data.columns:
        knowledge_group_filter = st.sidebar.selectbox("Knowledge area group:", ["All", "None"] + list(data["Knowledge area group"].dropna().unique()))
    else:
        knowledge_group_filter = st.sidebar.selectbox("Knowledge area group:", ["All", "None"])
        st.warning("The column 'Knowledge area group' was not found in the CSV file.")
    
    # Apply filters
    filtered_data = data.copy()
    
    # Filter by publication period
    if period_filter != "All" and period_filter != "None":
        filtered_data = filtered_data[filtered_data["Year"] == period_filter]
    
    # Filter by citations
    if citations_filter != "All" and citations_filter != "None":
        filtered_data = filtered_data[filtered_data["Cited by"] == citations_filter]
    
    # Filter by keywords
    if keywords_filter != "All" and keywords_filter != "None":
        keywords = [kw.strip() for kw in keywords_filter.split(",")]
        if exact_match:
            filtered_data = filtered_data[
                filtered_data["Keywords"].apply(lambda x: all(kw in x.split(",") for kw in keywords) if pd.notna(x) else False)
            ]
        else:
            filtered_data = filtered_data[
                filtered_data["Keywords"].str.contains('|'.join(keywords), case=False, na=False)
            ]
    
    # Filter by JCR
    if jcr_filter != "All" and jcr_filter != "None":
        filtered_data = filtered_data[filtered_data["JCR rank"] == jcr_filter]
    
    # Filter by knowledge area group
    if knowledge_group_filter != "All" and knowledge_group_filter != "None" and "Knowledge area group" in data.columns:
        filtered_data = filtered_data[filtered_data["Knowledge area group"] == knowledge_group_filter]
    
    # Results summary
    st.subheader("Results Summary")
    if filtered_data.empty:
        st.warning("No results found for the selected filters.")
    else:
        st.write(f"Total results: {len(filtered_data)}")
    
    # Display filtered table
    st.subheader("Filtered Table")
    st.dataframe(filtered_data)
else:
    st.info("Please upload a CSV file to get started.")
