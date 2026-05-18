import streamlit as st
import pandas as pd
import os
import uuid
import requests

from gsheets import (
    get_products,
    add_product,
    delete_product,
    get_orders,
    delete_order
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Admin Dashboard",
    layout="wide"
)

# =====================================================
# STREAMLIT SECRETS
# =====================================================

ACCESS_TOKEN = st.secrets.get("ACCESS_TOKEN", "")
PHONE_NUMBER_ID = st.secrets.get("PHONE_NUMBER_ID", "")
SHEET_ID = st.secrets.get("SHEET_ID", "")

# =====================================================
# PATHS
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
# TITLE
# =====================================================

st.title("📦 Admin CRM Dashboard")

# =====================================================
# PHONE CLEANER
# =====================================================

def clean_phone(phone):

    phone = str(phone)

    phone = phone.split(".")[0]

    phone = phone.replace("+", "")

    phone = phone.replace(" ", "")

    return phone

# =====================================================
# WHATSAPP FUNCTION
# =====================================================

def send_whatsapp(phone, message):

    phone = clean_phone(phone)

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
# TABS
# =====================================================

tab1, tab2, tab3 = st.tabs([
    "📦 Products",
    "🛒 Orders",
    "📲 WhatsApp"
])

# =====================================================
# TAB 1 — PRODUCTS
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

    price = st.number_input(
        "Price",
        min_value=1,
        step=1
    )

    if st.button("➕ Add Product"):

        if not uploaded_image:

            st.warning("Please upload image")

            st.stop()

        if not product_name:

            st.warning("Please enter product name")

            st.stop()

        product_id = f"P{str(uuid.uuid4())[:5]}"

        image_filename = f"{product_id}_{uploaded_image.name}"

        image_path = os.path.join(
            PRODUCT_FOLDER,
            image_filename
        )

        with open(image_path, "wb") as f:

            f.write(uploaded_image.getbuffer())

        add_product([
            product_id,
            product_name,
            price,
            image_filename
        ])

        st.success("✅ Product Added")

        st.rerun()

    st.markdown("---")

    st.subheader("📦 Current Products")

    if not products_df.empty:

        for idx, row in products_df.iterrows():

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 2, 1])

            # IMAGE
            with col1:

                image_path = os.path.join(
                    PRODUCT_FOLDER,
                    str(row["image"])
                )

                if os.path.exists(image_path):

                    st.image(
                        image_path,
                        width=180
                    )

            # DETAILS
            with col2:

                st.subheader(
                    str(row["product_name"])
                )

                st.write(
                    f"Product ID: {row['product_id']}"
                )

                st.write(
                    f"Price: ₹{row['price']}"
                )

            # DELETE
            with col3:

                st.write("")

                st.write("")

                if st.button(
                    "❌ Delete Product",
                    key=f"delete_product_{idx}"
                ):

                    delete_product(idx + 2)

                    st.success("Product Deleted")

                    st.rerun()

    else:

        st.warning("No products found")

# =====================================================
# TAB 2 — ORDERS
# =====================================================

with tab2:

    st.header("🛒 Orders")

    if not orders_df.empty:

        grouped_orders = orders_df.groupby("order_id")

        total_sales = 0

        for order_id, group in grouped_orders:

            st.markdown("---")

            first_row = group.iloc[0]

            customer_name = first_row["customer_name"]

            customer_number = clean_phone(
                first_row["customer_number"]
            )

            st.subheader(
                f"Order ID: {order_id}"
            )

            st.write(
                f"Customer: {customer_name}"
            )

            st.write(
                f"WhatsApp: {customer_number}"
            )

            st.dataframe(
                group,
                use_container_width=True
            )

            grand_total = pd.to_numeric(
                group["total"],
                errors="coerce"
            ).sum()

            total_sales += grand_total

            st.success(
                f"Order Total: ₹{grand_total}"
            )

            if st.button(
                "❌ Delete Order",
                key=f"delete_order_{order_id}"
            ):

                rows_to_delete = []

                for idx2, row2 in orders_df.iterrows():

                    if row2["order_id"] == order_id:

                        rows_to_delete.append(idx2 + 2)

                rows_to_delete.reverse()

                for r in rows_to_delete:

                    delete_order(r)

                st.success("Order Deleted")

                st.rerun()

        st.markdown("---")

        st.success(
            f"💰 Total Sales: ₹{total_sales}"
        )

    else:

        st.warning("No orders found")

# =====================================================
# TAB 3 — WHATSAPP
# =====================================================

with tab3:

    st.header("📲 WhatsApp Sending Panel")

    if not orders_df.empty:

        grouped_orders = orders_df.groupby("order_id")

        for order_id, group in grouped_orders:

            first_row = group.iloc[0]

            customer_name = first_row["customer_name"]

            customer_number = clean_phone(
                first_row["customer_number"]
            )

            lines = []

            lines.append(
                f"Hello {customer_name},"
            )

            lines.append("")

            lines.append(
                "Your order details:"
            )

            grand_total = 0

            for _, item in group.iterrows():

                qty = item["qty"]

                pname = item["product_name"]

                total = float(item["total"])

                grand_total += total

                lines.append(
                    f"• {pname} x {qty} = ₹{total}"
                )

            lines.append("")

            lines.append(
                f"Total Amount: ₹{grand_total}"
            )

            lines.append("")

            lines.append(
                "Thank you for your order 🙏"
            )

            message = "\n".join(lines)

            st.markdown("---")

            st.subheader(
                f"{customer_name} ({customer_number})"
            )

            st.code(message)

            if st.button(
                "📲 Send WhatsApp",
                key=f"send_{order_id}"
            ):

                result = send_whatsapp(
                    customer_number,
                    message
                )

                if "messages" in result:

                    st.success(
                        "WhatsApp Sent Successfully"
                    )

                else:

                    st.error(result)

        st.markdown("---")

        if st.button(
            "🚀 Send WhatsApp To All Customers"
        ):

            sent_count = 0

            for order_id, group in grouped_orders:

                first_row = group.iloc[0]

                customer_name = first_row["customer_name"]

                customer_number = clean_phone(
                    first_row["customer_number"]
                )

                lines = []

                lines.append(
                    f"Hello {customer_name},"
                )

                lines.append("")

                lines.append(
                    "Your order details:"
                )

                grand_total = 0

                for _, item in group.iterrows():

                    qty = item["qty"]

                    pname = item["product_name"]

                    total = float(item["total"])

                    grand_total += total

                    lines.append(
                        f"• {pname} x {qty} = ₹{total}"
                    )

                lines.append("")

                lines.append(
                    f"Total Amount: ₹{grand_total}"
                )

                lines.append("")

                lines.append(
                    "Thank you for your order 🙏"
                )

                message = "\n".join(lines)

                result = send_whatsapp(
                    customer_number,
                    message
                )

                if "messages" in result:

                    sent_count += 1

            st.success(
                f"✅ WhatsApp sent to {sent_count} customers"
            )

    else:

        st.warning("No orders found")
