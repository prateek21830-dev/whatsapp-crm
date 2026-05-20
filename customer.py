import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Customer CRM",
    layout="wide"
)

st.title("📋 Customer Management")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    return pd.read_csv("customers.csv")

customer_df = load_data()

# =========================
# SAFETY CHECKS
# =========================

required_columns = [
    "Customer Name",
    "Contact Number",
    "Rating",
    "Total Purchase",
    "Last Purchase Days"
]

for col in required_columns:
    if col not in customer_df.columns:
        customer_df[col] = ""

# =========================
# SEARCH + FILTER SECTION
# =========================

st.subheader("🔍 Search & Filter Customers")

col1, col2, col3, col4 = st.columns(4)

with col1:
    search_name = st.text_input(
        "Search Customer Name"
    )

with col2:
    search_phone = st.text_input(
        "Search Phone Number"
    )

with col3:
    rating_filter = st.selectbox(
        "Filter By Rating",
        [
            "All",
            "⭐",
            "⭐⭐",
            "⭐⭐⭐",
            "⭐⭐⭐⭐",
            "⭐⭐⭐⭐⭐"
        ]
    )

with col4:
    inactive_filter = st.selectbox(
        "Inactive Customers",
        [
            "All",
            "30+ Days",
            "60+ Days",
            "90+ Days",
            "180+ Days"
        ]
    )

# =========================
# APPLY FILTERS
# =========================

filtered_df = customer_df.copy()

# Name Search
if search_name:
    filtered_df = filtered_df[
        filtered_df["Customer Name"]
        .astype(str)
        .str.lower()
        .str.contains(search_name.lower())
    ]

# Phone Search
if search_phone:
    filtered_df = filtered_df[
        filtered_df["Contact Number"]
        .astype(str)
        .str.contains(search_phone)
    ]

# Rating Filter
if rating_filter != "All":
    filtered_df = filtered_df[
        filtered_df["Rating"] == rating_filter
    ]

# Inactive Filter
if inactive_filter != "All":

    days = int(inactive_filter.replace("+ Days", ""))

    filtered_df["Last Purchase Days"] = pd.to_numeric(
        filtered_df["Last Purchase Days"],
        errors="coerce"
    )

    filtered_df = filtered_df[
        filtered_df["Last Purchase Days"] >= days
    ]

# =========================
# SORT SECTION
# =========================

st.subheader("📊 Sorting")

sort_option = st.selectbox(
    "Sort Customers By",
    [
        "Highest Purchase",
        "Lowest Purchase",
        "Most Active",
        "Most Inactive",
        "A-Z",
        "Z-A"
    ]
)

# Numeric Conversion
filtered_df["Total Purchase"] = pd.to_numeric(
    filtered_df["Total Purchase"],
    errors="coerce"
)

# Apply Sorting
if sort_option == "Highest Purchase":

    filtered_df = filtered_df.sort_values(
        by="Total Purchase",
        ascending=False
    )

elif sort_option == "Lowest Purchase":

    filtered_df = filtered_df.sort_values(
        by="Total Purchase",
        ascending=True
    )

elif sort_option == "Most Active":

    filtered_df = filtered_df.sort_values(
        by="Last Purchase Days",
        ascending=True
    )

elif sort_option == "Most Inactive":

    filtered_df = filtered_df.sort_values(
        by="Last Purchase Days",
        ascending=False
    )

elif sort_option == "A-Z":

    filtered_df = filtered_df.sort_values(
        by="Customer Name",
        ascending=True
    )

elif sort_option == "Z-A":

    filtered_df = filtered_df.sort_values(
        by="Customer Name",
        ascending=False
    )

# =========================
# SUMMARY CARDS
# =========================

st.subheader("📈 CRM Summary")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Total Customers",
        len(filtered_df)
    )

with c2:
    st.metric(
        "Total Sales",
        f"₹ {filtered_df['Total Purchase'].sum():,.0f}"
    )

with c3:
    inactive_90 = len(
        filtered_df[
            filtered_df["Last Purchase Days"] >= 90
        ]
    )

    st.metric(
        "90+ Days Inactive",
        inactive_90
    )

with c4:
    vip = len(
        filtered_df[
            filtered_df["Rating"] == "⭐⭐⭐⭐⭐"
        ]
    )

    st.metric(
        "VIP Customers",
        vip
    )

# =========================
# DOWNLOAD OPTION
# =========================

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Customers",
    data=csv,
    file_name="filtered_customers.csv",
    mime="text/csv"
)

# =========================
# CUSTOMER TABLE
# =========================

st.subheader("📋 Customer List")

st.dataframe(
    filtered_df,
    use_container_width=True,
    height=650
)

# =========================
# FOOTER
# =========================

st.success(
    f"Showing {len(filtered_df)} customers"
)
