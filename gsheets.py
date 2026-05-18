import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials

# =====================================================
# GOOGLE SHEETS AUTH
# =====================================================

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# =====================================================
# STREAMLIT SECRETS
# =====================================================

creds_dict = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(creds)

# =====================================================
# GOOGLE SHEET ID
# =====================================================

SHEET_ID = "1uyLY4L5ZMQtkhQSYgIIjmnrE8wctqO6vCzY_RdjFGmQ"

sheet = client.open_by_key(SHEET_ID)

# =====================================================
# PRODUCTS SHEET
# =====================================================

def get_products():

    ws = sheet.worksheet("PRODUCTS")

    data = ws.get_all_records()

    return pd.DataFrame(data)

# =====================================================
# ADD PRODUCT
# =====================================================

def add_product(product_row):

    ws = sheet.worksheet("PRODUCTS")

    ws.append_row(product_row)

# =====================================================
# DELETE PRODUCT
# =====================================================

def delete_product(row_number):

    ws = sheet.worksheet("PRODUCTS")

    ws.delete_rows(row_number)

# =====================================================
# ORDERS SHEET
# =====================================================

def get_orders():

    ws = sheet.worksheet("ORDERS")

    data = ws.get_all_records()

    return pd.DataFrame(data)

# =====================================================
# ADD ORDER
# =====================================================

def add_order(order_row):

    ws = sheet.worksheet("ORDERS")

    ws.append_row(order_row)

# =====================================================
# DELETE ORDER
# =====================================================

def delete_order(row_number):

    ws = sheet.worksheet("ORDERS")

    ws.delete_rows(row_number)
