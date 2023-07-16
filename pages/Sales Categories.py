import streamlit as st
import pandas as pd
import numpy as np
import gspread



import helpers_full as hpf
import helpers as hp
import helpers2 as hp2

# authentication
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():

    # Set the display width to maximum
    pd.set_option('display.max_columns', None)
    pd.set_option('display.expand_frame_repr', True)
    # Configure the Streamlit page width
    st.set_page_config(layout="wide")

    st.title('Sales by Product Categories')
    st.write('Category sales per store per store. Select the store you want to view and then the categories if you want to look at by sales or by qty sold.')
    st.warning('JULY DATA INCOMPLETE! Will update at the end of the month')


    ### Get Online or Offline file:
    try:
        existing_file = 'data/consolidated_data.xlsx'
        df = pd.read_excel(existing_file,engine='openpyxl', header=0)

    except:
        # initialize the gspread client
        gc = gspread.service_account(filename='googlekeys/ld-revenue-analysis-50b1d5f2ed41.json')
        # open the Google Spreadsheet by its URL
        spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1_uOwLA3uPPgg-vG-b432I-pJJBmJNLx2-3kan10L4yA/edit#gid=0')
        # select the sheet from the spreadsheet
        worksheet = spreadsheet.worksheet("product_data")
        # get all values from the sheet and convert it to a pandas DataFrame
        df = pd.DataFrame(worksheet.get_all_records())







    # Clean DF
    df = hpf.clean(df)


    # Store selection
    all_stores = df['store'].unique().tolist()
    all_stores.append('ALL')
    store_filter = st.selectbox('Store Selection', all_stores)
    df = hpf.filter_store(df,store_filter)
    # st.dataframe(hpf.filter_store(df,store_filter)) 

    # Pivot table QTY
    st.header(f'Qty Sales by Category / Month for {store_filter}')
    # style
    df_qty = hpf.pivot(df,'Qty Sold')
    st.write(hpf.get_guests(store_filter).style.background_gradient(cmap='bwr', axis=1).format("{:,.0f}"))
    st.dataframe(hpf.style_pivot(df_qty))

    st.write('As % of Qty Sold')
    st.dataframe(hpf.pcnt_df(df_qty))


    # Pivot table NET SALES
    st.header(f' Net Sales by Category / Month for {store_filter}')
    # metrics = st.radio('Metrics', ['Qty Sold', 'Net Sales'])
    # style
    df_netsales = hpf.pivot(df,'Net Sales')
    st.write(hpf.get_guests(store_filter).style.background_gradient(cmap='bwr', axis=1).format("{:,.0f}"))
    st.dataframe(hpf.style_pivot(df_netsales))

    st.write('As % of Net Sales')
    st.dataframe(hpf.pcnt_df(df_netsales))



