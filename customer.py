import streamlit as st
import pandas as pd
import os
import uuid

from gsheets import (
    get_products,
    get_orders,
    add_order
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Product Catalog",
    layout="wide"
)

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
# LOAD PRODUCTS
# =====================================================

products_df = get_products()

# =====================================================
# TITLE
# =====================================================

st.title("🛍 Product Catalog")

st.markdown(
    "Select products and place your order."
)

# =====================================================
# NO PRODUCTS
# =====================================================

if products_df.empty:

    st.warning(
        "No products available."
    )

    st.stop()

# =====================================================
# CUSTOMER DETAILS
# =====================================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:

    customer_name = st.text_input(
        "Customer Name"
    )

with col2:

    customer_number = st.text_input(
        "WhatsApp Number",
        placeholder="919876543210"
    )

# =====================================================
# CLEAN PHONE
# =====================================================

def clean_phone(phone):

    phone = str(phone)

    phone = phone.replace(".0", "")

    phone = phone.replace("+", "")

    phone = phone.replace(" ", "")

    return phone.strip()

# =====================================================
# PRODUCT CATALOG
# =====================================================

st.markdown("---")

st.header("📦 Products")

cart = []

for idx, row in products_df.iterrows():

    st.markdown("---")

    col1, col2 = st.columns([1,2])

    # =================================================
    # IMAGE
    # =================================================

    with col1:

        image_path = os.path.join(
            PRODUCT_FOLDER,
            str(row["image"])
        )

        if os.path.exists(image_path):

            st.image(
                image_path,
                width=220
            )

    # =================================================
    # DETAILS
    # =================================================

    with col2:

        st.subheader(
            str(row["product_name"])
        )

        st.write(
            f"Code: {row['product_id']}"
        )

        st.markdown(
            f"## ₹{row['price']}"
        )

        qty = st.selectbox(
            f"Select Quantity - {row['product_id']}",
            [0,1,2,5,10,20],
            key=f"qty_{row['product_id']}"
        )

        if qty > 0:

            total = qty * float(row["price"])

            cart.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "qty": qty,
                "price": row["price"],
                "total": total
            })

# =====================================================
# ORDER SUMMARY
# =====================================================

st.markdown("---")

st.header("🛒 Order Summary")

if cart:

    cart_df = pd.DataFrame(cart)

    st.dataframe(
        cart_df,
        use_container_width=True
    )

    grand_total = cart_df["total"].sum()

    st.success(
        f"Grand Total: ₹{grand_total}"
    )

    # =================================================
    # PLACE ORDER
    # =================================================

    if st.button("🚀 Place Order"):

        if not customer_name:

            st.warning(
                "Please enter customer name."
            )

            st.stop()

        if not customer_number:

            st.warning(
                "Please enter WhatsApp number."
            )

            st.stop()

        customer_number = clean_phone(
            customer_number
        )

        order_id = str(uuid.uuid4())[:8]

        # =============================================
        # SAVE EACH ITEM
        # =============================================

        for item in cart:

            add_order([
                order_id,
                customer_name,
                customer_number,
                item["product_id"],
                item["product_name"],
                item["qty"],
                item["price"],
                item["total"]
            ])

        st.balloons()

        st.success(
            "✅ Order Placed Successfully"
        )

        st.markdown(
            f"""
### Order ID: `{order_id}`

Our team will contact you shortly on WhatsApp.
"""
        )

else:

    st.info(
        "Select products to create order."
    )
