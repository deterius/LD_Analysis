import pandas as pd
import numpy as np
import streamlit as st

date_options = {
        'Per Day': None,
        'Group by Month': 'M',
        'Group by Week Number': 'W'
    }
# columns to drop from df
drop_cols = ['week_num','month','year','Checks', 'Gross Sales', 'Per Check','Void','Avg Mins','Taxes', 'Avg Price','Avg Spend','Per Guest']


def groupings(date_options):
    return st.selectbox('Select Date Group Option', list(date_options.keys()))


def date_window(df):
    # df specify time window:
    # Add input widgets for minimum and maximum dates
    # Convert the 'date' column to datetime.date objects
    df['date'] = pd.to_datetime(df['date']).dt.date
    # Add input widgets for minimum and maximum dates
    min_date = st.date_input('Minimum Date', value=min(df['date']))
    max_date = st.date_input('Maximum Date', value=max(df['date']))
    # Filter the DataFrame based on the specified time period
    mask = (df['date'] >= min_date) & (df['date'] <= max_date)
    return df[mask]