import streamlit as st
import pandas as pd
import numpy as np
import gspread


# import database as db 
import helpers as hp
import helpers2 as hp2
import page_helpers as ph

import skhelper as skh


import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

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

    # date selectior
    date_options = ph.date_options
    group_by = ph.groupings(date_options)

    ### Get Online or Offline file:
    try:
        df = pd.read_excel('data/ptm.xlsx',engine='openpyxl')
        df = hp.main_clean(df)
    except:
        # initialize the gspread client
        gc = gspread.service_account(filename='googlekeys/ld-revenue-analysis-50b1d5f2ed41.json')
        # open the Google Spreadsheet by its URL
        spreadsheet = gc.open_by_url('https://docs.google.com/spreadsheets/d/1_uOwLA3uPPgg-vG-b432I-pJJBmJNLx2-3kan10L4yA/edit#gid=0')
        # select the sheet from the spreadsheet
        worksheet = spreadsheet.worksheet("ptm")
        # get all values from the sheet and convert it to a pandas DataFrame
        df = pd.DataFrame(worksheet.get_all_records())





    st.title('Revenue Dashboard')
    df = hp.main_clean(df)

    # df specify time window
    df = ph.date_window(df)

    # drop unecessary columns
    drop_cols = ph.drop_cols

    if date_options != 'date':
        drop_cols.append('week_day')
        
    # Metric results / group by date
    # transform DF
    df_metric = hp2.transform(df, 'sum', group_by, date_options)
    st.subheader("Averages 平均")
    dfmeans = hp2.transform(df, 'mean', group_by, date_options)
    st.write(hp2.main_mean(dfmeans))

    # write sums total numbers per time period
    dfsums = hp2.main_sum(df_metric, drop_cols, None)
    st.subheader("Totals 总")
    st.write(dfsums)

    # Line plot
    st.subheader(f'Average Net Revenue per {date_options[group_by]}')
    # Apply a 3-month moving average to the 'revenue' column
    if date_options[group_by] == None:
        window_size = 14
    elif date_options[group_by] == 'M':
        window_size = 1
    else:
        window_size = 4
        
    dfmeans['smoothed_revenue'] = dfmeans['Net Sales'].rolling(window_size, min_periods=1).mean()
    dfmeans['smoothed_Per_Guest'] = dfmeans['Per_Guest'].rolling(window_size, min_periods=1).mean()
    dfmeans['smoothed_Guests'] = dfmeans['Guests'].rolling(window_size, min_periods=1).mean()
    df['smoothed_revenue'] = df['Net Sales'].rolling(window_size, min_periods=1).mean()
    df['smoothed_Per_Guest'] = df['Per_Guest'].rolling(window_size, min_periods=1).mean()
    df['smoothed_Guests'] = df['Guests'].rolling(window_size, min_periods=1).mean()

    st.line_chart(dfmeans['smoothed_revenue'])    

    st.subheader(f'Average Revenue per Guests by: {date_options[group_by]}')
    st.line_chart(dfmeans[['smoothed_Per_Guest','smoothed_Guests']])

    # NORMALIZED NUMBERS
    st.subheader('Normalized Numbers')

    df_metric['smoothed_revenue'] = df_metric['Net Sales'].rolling(window_size, min_periods=1).mean()
    df_metric['smoothed_Per_Guest'] = df_metric['Per_Guest'].rolling(window_size, min_periods=1).mean()
    df_metric['smoothed_Guests'] = df_metric['Guests'].rolling(window_size, min_periods=1).mean()

    # Select the columns to normalize
    columns_to_normalize = ['smoothed_revenue', 'smoothed_Per_Guest', 'smoothed_Guests']
    # Perform min-max scaling
    scaler = MinMaxScaler()
    df_metric[columns_to_normalize] = scaler.fit_transform(df_metric[columns_to_normalize])
    st.line_chart(df_metric[['smoothed_revenue', 'smoothed_Per_Guest', 'smoothed_Guests']])

    # PLOT REGRESSION
    # Call the regression function
    plot = skh.regression(df)
    st.pyplot(plot)