import streamlit as st
import pandas as pd
import os
import uuid
from PIL import Image

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Mini Commerce Website",
    layout="wide"
)

PRODUCT_FOLDER = "product_images"
DB_FOLDER = "database"

PRODUCT_DB = os.path.join(DB_FOLDER, "products.csv")
ORDER_DB = os.path.join(DB_FOLDER, "orders.csv")

os.makedirs(PRODUCT_FOLDER, exist_ok=True)
os.makedirs(DB_FOLDER, exist_ok=True)

# =====================================================
# INIT DATABASES
# =====================================================

if not os.path.exists(PRODUCT_DB):

    pd.DataFrame(columns=[
        "product_id",
        "product_name",
        "price",
        "image"
    ]).to_csv(PRODUCT_DB, index=False)

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
# LOAD DATABASES
# =====================================================

products_df = pd.read_csv(PRODUCT_DB)
orders_df = pd.read_csv(ORDER_DB)

# =====================================================
# SIDEBAR ADMIN PANEL
# =====================================================

st.sidebar.title("📤 Admin Product Upload")

uploaded_image = st.sidebar.file_uploader(
    "Upload Product Image",
    type=["jpg", "jpeg", "png"]
)

product_name = st.sidebar.text_input(
    "Product Name"
)

price = st.sidebar.number_input(
    "Product Price",
    min_value=1,
    step=1
)

if st.sidebar.button("Save Product"):

    if uploaded_image and product_name:

        product_id = f"P{str(len(products_df)+1).zfill(3)}"

        image_filename = (
            f"{product_id}_{uploaded_image.name}"
        )

        image_path = os.path.join(
            PRODUCT_FOLDER,
            image_filename
        )

        with open(image_path, "wb") as f:
            f.write(uploaded_image.getbuffer())

        new_product = pd.DataFrame([{
            "product_id": product_id,
            "product_name": product_name,
            "price": price,
            "image": image_filename
        }])

        updated_df = pd.concat(
            [products_df, new_product],
            ignore_index=True
        )

        updated_df.to_csv(PRODUCT_DB, index=False)

        st.sidebar.success(
            f"✅ Product Saved: {product_id}"
        )

        st.rerun()

# =====================================================
# CUSTOMER WEBSITE
# =====================================================

st.title("🛍 Mini Commerce Website")

st.markdown(
    "Browse products and place your order instantly."
)

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
# PRODUCT CATALOG
# =====================================================

st.markdown("---")

st.header("📦 Product Catalog")

cart = []

# =====================================================
# DISPLAY PRODUCTS
# =====================================================

for idx, row in products_df.iterrows():

    st.markdown("---")

    col1, col2 = st.columns([1, 2])

    # =============================================
    # IMAGE
    # =============================================

    with col1:

        image_path = os.path.join(
            PRODUCT_FOLDER,
            row["image"]
        )

        if os.path.exists(image_path):

            st.image(
                image_path,
                width=250
            )

    # =============================================
    # PRODUCT DETAILS
    # =============================================

    with col2:

        st.subheader(
            row["product_name"]
        )

        st.write(
            f"Product Code: {row['product_id']}"
        )

        st.markdown(
            f"## ₹{row['price']}"
        )

        qty = st.selectbox(
            f"Select Quantity - {row['product_id']}",
            [0, 1, 5, 10, 20, 50],
            key=row["product_id"]
        )

        if qty > 0:

            cart.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "qty": qty,
                "price": row["price"],
                "total": qty * row["price"]
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

        order_id = str(uuid.uuid4())[:8]

        for item in cart:

            new_order = pd.DataFrame([{
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_number": customer_number,
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "qty": item["qty"],
                "price": item["price"],
                "total": item["total"]
            }])

            orders_df = pd.read_csv(ORDER_DB)

            updated_orders = pd.concat(
                [orders_df, new_order],
                ignore_index=True
            )

            updated_orders.to_csv(
                ORDER_DB,
                index=False
            )

        # =============================================
        # THANK YOU SCREEN
        # =============================================

        st.balloons()

        st.success(
            "✅ Order Placed Successfully"
        )

        st.markdown(
            f"""
### Thank You For Your Order

Order ID: `{order_id}`

Our team will contact you shortly on WhatsApp.
"""
        )

        # =============================================
        # OPTIONAL WHATSAPP CONFIRMATION LINK
        # =============================================

        whatsapp_message = (
            f"Thank you {customer_name}! "
            f"Your order {order_id} "
            f"has been received successfully."
        )

        whatsapp_url = (
            f"https://wa.me/{customer_number}"
            f"?text={whatsapp_message}"
        )

        st.markdown(
            f"""
<a href="{whatsapp_url}" target="_blank">
<button style="
background-color:#25D366;
color:white;
padding:12px;
border:none;
border-radius:8px;
font-size:16px;
cursor:pointer;
">
Open WhatsApp Confirmation
</button>
</a>
""",
            unsafe_allow_html=True
        )

else:

    st.info(
        "Select products to create order."
    )

# =====================================================
# ADMIN REPORTS
# =====================================================

st.markdown("---")

with st.expander("📊 Admin Reports"):

    orders_df = pd.read_csv(ORDER_DB)

    if not orders_df.empty:

        st.dataframe(
            orders_df,
            use_container_width=True
        )

        total_sales = orders_df["total"].sum()

        st.success(
            f"Total Sales: ₹{total_sales}"
        )

        csv = orders_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="⬇ Download Orders CSV",
            data=csv,
            file_name="orders_report.csv",
            mime="text/csv"
        )

    else:

        st.warning(
            "No orders available yet."
        )