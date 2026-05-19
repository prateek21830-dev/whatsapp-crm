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
# SECRETS
# =====================================================

ACCESS_TOKEN = st.secrets.get("ACCESS_TOKEN", "")
PHONE_NUMBER_ID = st.secrets.get("PHONE_NUMBER_ID", "")

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

st.title("📦 Admin Dashboard")

# =====================================================
# WHATSAPP FUNCTION
# =====================================================

def send_whatsapp(phone, message):

    if ACCESS_TOKEN == "" or PHONE_NUMBER_ID == "":

        return {
            "error": "ACCESS_TOKEN or PHONE_NUMBER_ID missing in Streamlit secrets"
        }

    phone = str(phone)

    phone = phone.split(".")[0]

    phone = phone.replace("+", "")

    phone = phone.replace(" ", "")

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
# ADD PRODUCTS
# =====================================================

st.header("📤 Add Products")

uploaded_images = st.file_uploader(
    "Upload Product Images",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)

product_name = st.text_input("Product Name")

price = st.number_input(
    "Price",
    min_value=1,
    step=1
)

if st.button("➕ Add Products"):

    if not uploaded_images:

        st.warning("Upload images")

        st.stop()

    if not product_name:

        st.warning("Enter product name")

        st.stop()

    added_count = 0

    for uploaded_image in uploaded_images:

        # PRODUCT ID
        product_id = f"P{str(uuid.uuid4())[:5]}"

        # IMAGE NAME
        image_filename = uploaded_image.name.replace(
            " ",
            "_"
        )

        # SAVE IMAGE
        image_path = os.path.join(
            PRODUCT_FOLDER,
            image_filename
        )

        with open(image_path, "wb") as f:

            f.write(uploaded_image.getbuffer())

        # SAVE TO GOOGLE SHEETS
        add_product([
            product_id,
            product_name,
            price,
            image_filename
        ])

        added_count += 1

    st.success(
        f"✅ {added_count} products added successfully"
    )

    st.rerun()

# =====================================================
# PRODUCT CATALOG
# =====================================================

st.markdown("---")

st.header("📦 Product Catalog")

if not products_df.empty:

    for idx, row in products_df.iterrows():

        st.markdown("---")

        col1, col2, col3 = st.columns([1, 2, 1])

        # =================================================
        # IMAGE
        # =================================================

        with col1:

            image_name = row.get("image", "")

            image_path = os.path.join(
                PRODUCT_FOLDER,
                str(image_name)
            )

            if os.path.exists(image_path):

                st.image(
                    image_path,
                    width=180
                )

            else:

                st.warning("Image missing")

        # =================================================
        # DETAILS
        # =================================================

        with col2:

            product_name_value = row.get(
                "product_name",
                "No Name"
            )

            product_id_value = row.get(
                "product_id",
                "N/A"
            )

            product_price_value = row.get(
                "price",
                0
            )

            st.subheader(
                str(product_name_value)
            )

            st.write(
                f"Product ID: {product_id_value}"
            )

            st.write(
                f"Price: ₹{product_price_value}"
            )

        # =================================================
        # DELETE PRODUCT
        # =================================================

        with col3:

            st.write("")
            st.write("")

            if st.button(
                "❌ Delete Product",
                key=f"delete_product_{idx}"
            ):

                delete_product(idx + 2)

                st.success("Product deleted")

                st.rerun()

else:

    st.warning("No products available")

# =====================================================
# ORDERS
# =====================================================

st.markdown("---")

st.header("🛒 Orders")

if not orders_df.empty:

    grouped_orders = orders_df.groupby("order_id")

    for order_id, group in grouped_orders:

        st.markdown("---")

        first_row = group.iloc[0]

        customer_name = first_row.get(
            "customer_name",
            "Customer"
        )

        customer_number = str(
            first_row.get(
                "customer_number",
                ""
            )
        )

        customer_number = customer_number.split(".")[0]

        # =================================================
        # BUILD MESSAGE
        # =================================================

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

            qty = item.get("qty", 0)

            pname = item.get(
                "product_name",
                "Item"
            )

            total = item.get(
                "total",
                0
            )

            try:

                grand_total += float(total)

            except:

                pass

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

        # =================================================
        # DISPLAY
        # =================================================

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

        col1, col2 = st.columns(2)

        # =================================================
        # SEND WHATSAPP
        # =================================================

        with col1:

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

        # =================================================
        # DELETE ORDER
        # =================================================

        with col2:

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

                st.success(
                    "Order deleted"
                )

                st.rerun()

else:

    st.warning("No orders available")

# =====================================================
# SEND ALL WHATSAPP
# =====================================================

st.markdown("---")

if st.button("🚀 Send WhatsApp To All Customers"):

    grouped_orders = orders_df.groupby("order_id")

    sent_count = 0

    for order_id, group in grouped_orders:

        first_row = group.iloc[0]

        customer_name = first_row.get(
            "customer_name",
            "Customer"
        )

        customer_number = str(
            first_row.get(
                "customer_number",
                ""
            )
        )

        customer_number = customer_number.split(".")[0]

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

            qty = item.get("qty", 0)

            pname = item.get(
                "product_name",
                "Item"
            )

            total = item.get(
                "total",
                0
            )

            try:

                grand_total += float(total)

            except:

                pass

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
