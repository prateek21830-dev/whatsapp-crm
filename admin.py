import streamlit as st
import pandas as pd
import requests
import uuid
import os

from gsheets import (
    get_products,
    add_product,
    delete_product,
    get_orders,
    add_order,
    delete_order
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Admin CRM Dashboard",
    layout="wide"
)

# =====================================================
# WHATSAPP CONFIG
# =====================================================

ACCESS_TOKEN = st.secrets["ACCESS_TOKEN"]
PHONE_NUMBER_ID = st.secrets["PHONE_NUMBER_ID"]

# =====================================================
# IMAGE FOLDER
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_FOLDER = os.path.join(
    BASE_DIR,
    "product_images"
)

os.makedirs(PRODUCT_FOLDER, exist_ok=True)

# =====================================================
# LOAD DATA
# =====================================================

products_df = get_products()
orders_df = get_orders()

# =====================================================
# CLEAN PHONE
# =====================================================

def clean_phone(phone):

    if pd.isna(phone):
        return ""

    phone = str(phone)

    phone = phone.replace(".0", "")

    phone = phone.replace("+", "")

    phone = phone.replace(" ", "")

    return phone.strip()

# =====================================================
# SEND WHATSAPP
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
        "text": {
            "body": message
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    return response.json()

# =====================================================
# TITLE
# =====================================================

st.title("📦 Admin CRM Dashboard")

tab1, tab2, tab3 = st.tabs([
    "📦 Products",
    "🛒 Orders",
    "📲 WhatsApp"
])

# =====================================================
# TAB 1 - PRODUCTS
# =====================================================

with tab1:

    st.header("📦 Product Management")

    uploaded_image = st.file_uploader(
        "Upload Product Image",
        type=["jpg", "jpeg", "png"]
    )

    product_name = st.text_input(
        "Product Name"
    )

    product_price = st.number_input(
        "Price",
        min_value=1
    )

    # =================================================
    # ADD PRODUCT
    # =================================================

    if st.button("➕ Add Product"):

        if uploaded_image and product_name:

            product_id = f"P{str(uuid.uuid4())[:6]}"

            image_filename = (
                f"{product_id}_{uploaded_image.name}"
            )

            image_path = os.path.join(
                PRODUCT_FOLDER,
                image_filename
            )

            with open(image_path, "wb") as f:

                f.write(uploaded_image.getbuffer())

            add_product([
                product_id,
                product_name,
                product_price,
                image_filename
            ])

            st.success("✅ Product Added")

            st.rerun()

        else:

            st.warning(
                "Please upload image and enter product name."
            )

    st.markdown("---")

    st.subheader("📦 Current Products")

    if not products_df.empty:

        for i, row in products_df.iterrows():

            col1, col2, col3 = st.columns([3,2,1])

            with col1:

                st.write(
                    f"{row['product_id']} | {row['product_name']} | ₹{row['price']}"
                )

            with col2:

                st.write(row["image"])

            with col3:

                if st.button(
                    "❌ Delete",
                    key=f"del_product_{i}"
                ):

                    delete_product(i + 2)

                    st.warning("Product Deleted")

                    st.rerun()

    else:

        st.info("No products available.")

# =====================================================
# TAB 2 - ORDERS
# =====================================================

with tab2:

    st.header("🛒 Orders")

    if not orders_df.empty:

        orders_df["customer_number"] = (
            orders_df["customer_number"]
            .astype(str)
            .apply(clean_phone)
        )

        st.dataframe(
            orders_df,
            use_container_width=True
        )

        st.markdown("---")

        st.subheader("❌ Remove Bogus Orders")

        for i, row in orders_df.iterrows():

            col1, col2 = st.columns([4,1])

            with col1:

                st.write(
                    f"{row['order_id']} | {row['customer_name']} | ₹{row['total']}"
                )

            with col2:

                if st.button(
                    "Delete",
                    key=f"delete_order_{i}"
                ):

                    delete_order(i + 2)

                    st.warning("Order Deleted")

                    st.rerun()

        total_sales = pd.to_numeric(
            orders_df["total"],
            errors="coerce"
        ).sum()

        st.success(
            f"💰 Total Sales: ₹{total_sales}"
        )

    else:

        st.warning("No orders found.")

# =====================================================
# TAB 3 - WHATSAPP
# =====================================================

with tab3:

    st.header("📲 WhatsApp Message Sending")

    if not orders_df.empty:

        orders_df["customer_number"] = (
            orders_df["customer_number"]
            .astype(str)
            .apply(clean_phone)
        )

        for i, row in orders_df.iterrows():

            message = f"""
Hi {row['customer_name']},

✅ Your order is confirmed.

🆔 Order ID: {row['order_id']}
📦 Product: {row['product_name']}
🔢 Qty: {row['qty']}
💰 Total: ₹{row['total']}

Thank you for shopping with us.
"""

            col1, col2 = st.columns([4,1])

            with col1:

                st.write(
                    f"{row['customer_name']} | {row['customer_number']}"
                )

            with col2:

                if st.button(
                    "Send",
                    key=f"send_msg_{i}"
                ):

                    phone = clean_phone(
                        row["customer_number"]
                    )

                    result = send_whatsapp(
                        phone,
                        message
                    )

                    st.write(result)

        # =============================================
        # SEND ALL
        # =============================================

        if st.button("🚀 Send All Messages"):

            for _, row in orders_df.iterrows():

                phone = clean_phone(
                    row["customer_number"]
                )

                message = f"""
Hi {row['customer_name']},

✅ Your order is confirmed.

🆔 Order ID: {row['order_id']}
📦 Product: {row['product_name']}
🔢 Qty: {row['qty']}
💰 Total: ₹{row['total']}

Thank you for shopping with us.
"""

                send_whatsapp(
                    phone,
                    message
                )

            st.success("✅ All Messages Sent")

    else:

        st.warning("No orders available.")
