import streamlit as st
import gspread
import pandas as pd

from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]

creds = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

client = gspread.authorize(creds)

SHEET_ID = st.secrets["SHEET_ID"]

sheet = client.open_by_key(SHEET_ID)

# =====================================================
# PRODUCTS
# =====================================================

def get_products():

    try:

        ws = sheet.worksheet("PRODUCTS")

        data = ws.get_all_records()

        return pd.DataFrame(data)

    except Exception as e:

        st.error(f"PRODUCTS sheet error: {e}")

        return pd.DataFrame()

def add_product(row):

    ws = sheet.worksheet("PRODUCTS")

    ws.append_row(row)

def delete_product(row_number):

    ws = sheet.worksheet("PRODUCTS")

    ws.delete_rows(row_number)

# =====================================================
# ORDERS
# =====================================================

def get_orders():

    try:

        ws = sheet.worksheet("ORDERS")

        data = ws.get_all_records()

        return pd.DataFrame(data)

    except Exception as e:

        st.error(f"ORDERS sheet error: {e}")

        return pd.DataFrame()

def add_order(row):

    ws = sheet.worksheet("ORDERS")

    ws.append_row(row)

def delete_order(row_number):

    ws = sheet.worksheet("ORDERS")

    ws.delete_rows(row_number)
