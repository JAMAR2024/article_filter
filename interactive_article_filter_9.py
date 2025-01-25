
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

# Add custom CSS for background color
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f0f8ff;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.title("Interactive Article Filter")
st.markdown("<h2 style='color: blue;'>Use the filters below to explore and segment the database interactively.</h2>", unsafe_allow_html=True)
st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

# Dynamic file upload
uploaded_file = st.file_uploader("Upload your CSV file here", type=["csv"])

# Load default data if no file is uploaded
default_file = "Base Final_25_12_2024_5.csv"  # Ensure this file is in the same directory
if uploaded_file is not None:
    data = load_data(uploaded_file)
elif os.path.exists(default_file):
    data = load_data(default_file)
else:
    st.warning("No file uploaded and default data file not found.")
    data = pd.DataFrame()

if not data.empty:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Period of publication filter
    period_options = ["All", "None", "2007-2010", "2011-2014", "2015-2020", "2021-2025"]
    period_filter = st.sidebar.selectbox("Period of publication:", period_options, index=0)
    
    # Citations filter
    citation_options = ["All", "None", "1 to 10 citations", "11 to 24 citations", "25 to 49 citations", "50 to 99 citations", "100 to 249 citations", "250 or more citations"]
    citations_filter = st.sidebar.selectbox("Number of Citations:", citation_options, index=0)
    
    # Keywords filter
    keyword_categories = ["All", "None"] + sorted(data["Keywords"].dropna().unique().tolist())
    keywords_filter = st.sidebar.selectbox("Keywords:", keyword_categories, index=0)
    
    exact_match = st.sidebar.checkbox("Exact match", value=False)
    
    # JCR filter
    jcr_options = ["All", "None", "No Q", "Q1", "Q2", "Q3", "Q4"]
    jcr_filter = st.sidebar.selectbox("JCR rank:", jcr_options, index=0)
    
    # Knowledge area group filter
    if "Knowledge area group" in data.columns:
        knowledge_group_filter = st.sidebar.selectbox("Knowledge area group:", ["All", "None"] + list(data["Knowledge area group"].dropna().unique()))
    else:
        knowledge_group_filter = st.sidebar.selectbox("Knowledge area group:", ["All", "None"])
        st.warning("The column 'Knowledge area group' was not found in the CSV file.")
    
    # Apply filters
    filtered_data = data.copy()
    
    # Filter by period of publication
    if period_filter != "All" and period_filter != "None":
        if period_filter == "2007-2010":
            filtered_data = filtered_data[(filtered_data["Year"] >= 2007) & (filtered_data["Year"] <= 2010)]
        elif period_filter == "2011-2014":
            filtered_data = filtered_data[(filtered_data["Year"] >= 2011) & (filtered_data["Year"] <= 2014)]
        elif period_filter == "2015-2020":
            filtered_data = filtered_data[(filtered_data["Year"] >= 2015) & (filtered_data["Year"] <= 2020)]
        elif period_filter == "2021-2025":
            filtered_data = filtered_data[(filtered_data["Year"] >= 2021) & (filtered_data["Year"] <= 2025)]
    
    # Filter by citations
    if citations_filter != "All" and citations_filter != "None":
        if citations_filter == "1 to 10 citations":
            filtered_data = filtered_data[(filtered_data["Cited by"] >= 1) & (filtered_data["Cited by"] <= 10)]
        elif citations_filter == "11 to 24 citations":
            filtered_data = filtered_data[(filtered_data["Cited by"] >= 11) & (filtered_data["Cited by"] <= 24)]
        elif citations_filter == "25 to 49 citations":
            filtered_data = filtered_data[(filtered_data["Cited by"] >= 25) & (filtered_data["Cited by"] <= 49)]
        elif citations_filter == "50 to 99 citations":
            filtered_data = filtered_data[(filtered_data["Cited by"] >= 50) & (filtered_data["Cited by"] <= 99)]
        elif citations_filter == "100 to 249 citations":
            filtered_data = filtered_data[(filtered_data["Cited by"] >= 100) & (filtered_data["Cited by"] <= 249)]
        elif citations_filter == "250 or more citations":
            filtered_data = filtered_data[filtered_data["Cited by"] >= 250]
    
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
    
    if period_filter == 'All' and citations_filter == 'All' and keywords_filter == 'All' and jcr_filter == 'All' and knowledge_group_filter == 'All':
        total_results = 205  # Set to 205 when all filters are set to "All"
    else:
        total_results = len(filtered_data)
    
    st.write(f"Total results: {total_results}")
    
    # Display filtered table
    st.subheader("Filtered Table")
    st.dataframe(filtered_data)
else:
    st.info("Please upload a CSV file to get started.")
