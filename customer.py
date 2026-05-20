import streamlit as st
import pandas as pd

st.set_page_config(page_title="Customers", layout="wide")

st.title("👥 Customer Dashboard")

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    return pd.read_csv("customers.csv")

customer_df = load_data()

# =========================
# SEARCH + FILTERS
# =========================
st.subheader("🔍 Search & Filters")

col1, col2, col3 = st.columns(3)

with col1:
    search_name = st.text_input("Search Customer Name")

with col2:
    search_mobile = st.text_input("Search Mobile Number")

with col3:
    min_purchase = st.number_input(
        "Minimum Purchase Amount",
        min_value=0,
        value=0
    )

# =========================
# FILTER LOGIC
# =========================
filtered_df = customer_df.copy()

# Name filter
if search_name:
    filtered_df = filtered_df[
        filtered_df["Customer Name"]
        .astype(str)
        .str.contains(search_name, case=False, na=False)
    ]

# Mobile filter
if search_mobile:
    filtered_df = filtered_df[
        filtered_df["Contact Number"]
        .astype(str)
        .str.contains(search_mobile, case=False, na=False)
    ]

# Purchase filter
if "Total Purchase" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["Total Purchase"] >= min_purchase
    ]

# =========================
# TOTAL CUSTOMERS
# =========================
st.markdown(f"### Total Customers: {len(filtered_df)}")

# =========================
# DISPLAY DATA
# =========================
st.dataframe(
    filtered_df,
    use_container_width=True,
    height=600
)
