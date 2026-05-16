import streamlit as st
import pandas as pd
import os
import uuid

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(page_title="Product Catalog", layout="wide")

# =====================================================
# PATHS
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRODUCT_FOLDER = os.path.join(BASE_DIR, "product_images")
DB_FOLDER = os.path.join(BASE_DIR, "database")

PRODUCT_DB = os.path.join(DB_FOLDER, "products.csv")
ORDER_DB = os.path.join(DB_FOLDER, "orders.csv")

os.makedirs(DB_FOLDER, exist_ok=True)
os.makedirs(PRODUCT_FOLDER, exist_ok=True)

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
# LOAD PRODUCTS
# =====================================================

products_df = pd.read_csv(PRODUCT_DB, dtype=str)

# =====================================================
# SAFE PHONE CLEAN FUNCTION (NO CRASH EVER)
# =====================================================

def clean_phone(phone):
    if pd.isna(phone):
        return ""

    phone = str(phone)
    phone = phone.strip()
    phone = phone.replace(".0", "")
    phone = phone.replace("+", "")
    phone = phone.replace(" ", "")

    # keep only digits
    phone = "".join([c for c in phone if c.isdigit()])

    if not phone.startswith("91"):
        phone = "91" + phone

    return phone

# =====================================================
# TITLE
# =====================================================

st.title("🛍 Product Catalog")
st.markdown("Select products and place your order")

# =====================================================
# CUSTOMER INPUT
# =====================================================

col1, col2 = st.columns(2)

with col1:
    customer_name = st.text_input("Customer Name")

with col2:
    customer_number = st.text_input("WhatsApp Number")

# =====================================================
# PRODUCT LIST
# =====================================================

cart = []

st.markdown("---")
st.header("📦 Products")

for _, row in products_df.iterrows():

    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        img_path = os.path.join(PRODUCT_FOLDER, str(row["image"]))
        if os.path.exists(img_path):
            st.image(img_path, width=250)

    with col2:
        st.subheader(row["product_name"])
        st.write("Code:", row["product_id"])
        st.markdown(f"₹ {row['price']}")

        qty = st.selectbox(
            f"Qty - {row['product_id']}",
            [0, 1, 5, 10, 20, 50],
            key=row["product_id"]
        )

        if qty > 0:
            cart.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "qty": qty,
                "price": float(row["price"]),
                "total": qty * float(row["price"])
            })

# =====================================================
# ORDER SUMMARY
# =====================================================

st.markdown("---")
st.header("🛒 Order Summary")

if cart:

    cart_df = pd.DataFrame(cart)
    st.dataframe(cart_df, use_container_width=True)

    total = cart_df["total"].sum()
    st.success(f"Total: ₹{total}")

    # =================================================
    # PLACE ORDER
    # =================================================

    if st.button("🚀 Place Order"):

        if not customer_name:
            st.error("Enter customer name")
            st.stop()

        if not customer_number:
            st.error("Enter WhatsApp number")
            st.stop()

        # FINAL SAFE CLEAN (FIX ALL ERRORS HERE)
        customer_number = clean_phone(customer_number)

        order_id = str(uuid.uuid4())[:8]

        # SAFE LOAD ORDERS
        try:
            orders_df = pd.read_csv(ORDER_DB, dtype=str)
        except:
            orders_df = pd.DataFrame(columns=[
                "order_id",
                "customer_name",
                "customer_number",
                "product_id",
                "product_name",
                "qty",
                "price",
                "total"
            ])

        # SAFE CLEAN OLD DATA (NO SPLIT CRASH)
        orders_df["customer_number"] = orders_df["customer_number"].apply(
            lambda x: clean_phone(x)
        )

        # ADD NEW ITEMS
        for item in cart:

            new_row = {
                "order_id": order_id,
                "customer_name": customer_name,
                "customer_number": customer_number,
                "product_id": item["product_id"],
                "product_name": item["product_name"],
                "qty": item["qty"],
                "price": item["price"],
                "total": item["total"]
            }

            orders_df = pd.concat([orders_df, pd.DataFrame([new_row])], ignore_index=True)

        # FINAL SAVE
        orders_df.to_csv(ORDER_DB, index=False)

        st.success("✅ Order placed successfully!")
        st.balloons()

else:
    st.info("Select products to continue")