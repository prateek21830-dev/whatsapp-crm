import streamlit as st
import pandas as pd
import os
import requests
import uuid

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(page_title="Admin Dashboard", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_FOLDER = os.path.join(BASE_DIR, "product_images")
DB_FOLDER = os.path.join(BASE_DIR, "database")

PRODUCT_DB = os.path.join(DB_FOLDER, "products.csv")
ORDER_DB = os.path.join(DB_FOLDER, "orders.csv")

os.makedirs(PRODUCT_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

# =====================================================
# WHATSAPP CONFIG
# =====================================================

ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
PHONE_NUMBER_ID = "1057145457490182"

# =====================================================
# INIT FILES
# =====================================================

if not os.path.exists(PRODUCT_DB):
    pd.DataFrame(columns=["product_id", "product_name", "price", "image"]).to_csv(PRODUCT_DB, index=False)

if not os.path.exists(ORDER_DB):
    pd.DataFrame(columns=[
        "order_id",
        "customer_name",
        "customer_number",
        "product_id",
        "product_name",
        "qty",
        "price",
        "total"
    ]).to_csv(ORDER_DB, index=False)

# =====================================================
# LOAD DATA
# =====================================================

products_df = pd.read_csv(PRODUCT_DB, dtype=str)
orders_df = pd.read_csv(ORDER_DB, dtype=str)

# =====================================================
# CLEAN PHONE
# =====================================================

def clean_phone(phone):
    if pd.isna(phone):
        return ""
    phone = str(phone).split(".")[0]
    return phone.replace("+", "").replace(" ", "")

# =====================================================
# WHATSAPP SEND
# =====================================================

def send_whatsapp(phone, message):

    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "type": "text",
        "text": {"body": message}
    }

    return requests.post(url, headers=headers, json=payload).json()

# =====================================================
# TITLE
# =====================================================

st.title("📦 Admin CRM Dashboard (Full Control)")

tab1, tab2, tab3 = st.tabs(["📦 Products", "🛒 Orders", "📲 WhatsApp"])

# =====================================================
# TAB 1 - PRODUCTS (ADD + DELETE)
# =====================================================

with tab1:

    st.header("📦 Product Management")

    # ADD PRODUCT
    uploaded_image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    product_name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=1)

    if st.button("➕ Add Product"):

        if uploaded_image and product_name:

            product_id = f"P{str(len(products_df)+1).zfill(3)}"

            image_name = f"{product_id}_{uploaded_image.name}"
            image_path = os.path.join(PRODUCT_FOLDER, image_name)

            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())

            new_row = pd.DataFrame([{
                "product_id": product_id,
                "product_name": product_name,
                "price": price,
                "image": image_name
            }])

            products_df = pd.concat([products_df, new_row], ignore_index=True)
            products_df.to_csv(PRODUCT_DB, index=False)

            st.success("Product Added")
            st.rerun()

    st.markdown("---")
    st.subheader("📦 Current Products")

    for i, row in products_df.iterrows():

        col1, col2, col3 = st.columns([3,2,1])

        with col1:
            st.write(f"{row['product_id']} - {row['product_name']} - ₹{row['price']}")

        with col2:
            st.write(row["image"])

        with col3:
            if st.button("❌ Delete", key=f"delp_{i}"):

                products_df = products_df.drop(i).reset_index(drop=True)
                products_df.to_csv(PRODUCT_DB, index=False)

                st.warning("Product Deleted")
                st.rerun()

# =====================================================
# TAB 2 - ORDERS (DELETE SUPPORT)
# =====================================================

with tab2:

    st.header("🛒 Orders")

    if not orders_df.empty:

        orders_df["customer_number"] = orders_df["customer_number"].apply(clean_phone)

        st.dataframe(orders_df, use_container_width=True)

        st.markdown("---")

        st.subheader("❌ Remove Bogus Orders")

        for i, row in orders_df.iterrows():

            col1, col2 = st.columns([4,1])

            with col1:
                st.write(f"{row['order_id']} | {row['customer_name']} | ₹{row['total']}")

            with col2:
                if st.button("Delete", key=f"del_o_{i}"):

                    orders_df = orders_df.drop(i).reset_index(drop=True)
                    orders_df.to_csv(ORDER_DB, index=False)

                    st.warning("Order Deleted")
                    st.rerun()

        total_sales = pd.to_numeric(orders_df["total"], errors="coerce").sum()
        st.success(f"💰 Total Sales: ₹{total_sales}")

    else:
        st.warning("No orders found")

# =====================================================
# TAB 3 - WHATSAPP
# =====================================================

with tab3:

    st.header("📲 WhatsApp Sending Panel")

    if not orders_df.empty:

        orders_df["customer_number"] = orders_df["customer_number"].apply(clean_phone)

        for i, row in orders_df.iterrows():

            msg = f"""
Hi {row['customer_name']},

Order Confirmed
ID: {row['order_id']}
Product: {row['product_name']}
Qty: {row['qty']}
Total: ₹{row['total']}
"""

            col1, col2 = st.columns([4,1])

            with col1:
                st.write(f"{row['customer_name']} - {row['customer_number']}")

            with col2:
                if st.button("Send", key=f"send_{i}"):

                    phone = clean_phone(row["customer_number"])
                    res = send_whatsapp(phone, msg)
                    st.write(res)

        if st.button("🚀 Send All"):

            for _, row in orders_df.iterrows():

                msg = f"""
Hi {row['customer_name']},

Order Confirmed
ID: {row['order_id']}
Product: {row['product_name']}
Qty: {row['qty']}
Total: ₹{row['total']}
"""

                phone = clean_phone(row["customer_number"])
                send_whatsapp(phone, msg)

            st.success("All messages sent")

    else:
        st.warning("No orders found")