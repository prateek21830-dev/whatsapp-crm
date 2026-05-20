import streamlit as st
import pandas as pd
import uuid

from gsheets import (
    get_products,
    add_order
)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Customer Dashboard",
    layout="wide"
)

# =====================================================
# LOAD PRODUCTS
# =====================================================

products_df = get_products()

# =====================================================
# TITLE
# =====================================================

st.title("🛍️ Customer Dashboard")

# =====================================================
# CUSTOMER DETAILS
# =====================================================

st.header("👤 Customer Details")

customer_name = st.text_input(
    "Customer Name"
)

customer_number = st.text_input(
    "WhatsApp Number"
)

# =====================================================
# PRODUCT SEARCH + FILTER
# =====================================================

st.markdown("---")

st.header("🔍 Search Products")

col1, col2 = st.columns(2)

with col1:

    search_product = st.text_input(
        "Search Product Name"
    )

with col2:

    max_price = st.number_input(
        "Maximum Price",
        min_value=0,
        value=100000
    )

# =====================================================
# APPLY FILTER
# =====================================================

filtered_df = products_df.copy()

# Product Name Filter

if search_product:

    filtered_df = filtered_df[
        filtered_df["product_name"]
        .astype(str)
        .str.contains(
            search_product,
            case=False,
            na=False
        )
    ]

# Price Filter

filtered_df = filtered_df[
    pd.to_numeric(
        filtered_df["price"],
        errors="coerce"
    ).fillna(0) <= max_price
]

# =====================================================
# PRODUCT CATALOG
# =====================================================

st.markdown("---")

st.header("📦 Products")

cart = []

if not filtered_df.empty:

    for idx, row in filtered_df.iterrows():

        st.markdown("---")

        col1, col2 = st.columns([1, 2])

        # =================================================
        # IMAGE
        # =================================================

        with col1:

            image_url = row.get("image", "")

            if image_url:

                st.image(
                    image_url,
                    width=220
                )

            else:

                st.warning("No image available")

        # =================================================
        # DETAILS
        # =================================================

        with col2:

            st.subheader(
                str(
                    row.get(
                        "product_name",
                        "No Name"
                    )
                )
            )

            st.write(
                f"Product ID: {row.get('product_id', 'N/A')}"
            )

            st.write(
                f"Price: ₹{row.get('price', 0)}"
            )

            qty = st.number_input(
                f"Quantity - {row.get('product_id', idx)}",
                min_value=0,
                step=1,
                key=f"qty_{idx}"
            )

            if qty > 0:

                total = qty * float(
                    row.get("price", 0)
                )

                cart.append({

                    "product_id": row.get(
                        "product_id",
                        ""
                    ),

                    "product_name": row.get(
                        "product_name",
                        ""
                    ),

                    "price": row.get(
                        "price",
                        0
                    ),

                    "qty": qty,

                    "total": total
                })

else:

    st.warning("No matching products found")

# =====================================================
# CART SUMMARY
# =====================================================

st.markdown("---")

st.header("🛒 Cart Summary")

if len(cart) > 0:

    cart_df = pd.DataFrame(cart)

    st.dataframe(
        cart_df,
        use_container_width=True
    )

    grand_total = cart_df["total"].sum()

    st.subheader(
        f"Grand Total: ₹{grand_total}"
    )

else:

    st.info("Cart is empty")

# =====================================================
# PLACE ORDER
# =====================================================

st.markdown("---")

if st.button("✅ Place Order"):

    if customer_name == "":

        st.warning(
            "Enter customer name"
        )

        st.stop()

    if customer_number == "":

        st.warning(
            "Enter WhatsApp number"
        )

        st.stop()

    if len(cart) == 0:

        st.warning(
            "Select at least one product"
        )

        st.stop()

    # =================================================
    # CREATE ORDER ID
    # =================================================

    order_id = f"O{str(uuid.uuid4())[:6]}"

    # =================================================
    # SAVE ORDER
    # =================================================

    for item in cart:

        add_order([

            order_id,

            customer_name,

            customer_number,

            item["product_id"],

            item["product_name"],

            item["price"],

            item["qty"],

            item["total"]
        ])

    st.success(
        f"✅ Order placed successfully. Order ID: {order_id}"
    )

    st.balloons()
