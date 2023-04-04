import streamlit as st
import pandas as pd
import numpy as np

# import database as db 
import helpers as hp
import plotly.express as px

# date selectior
date_options = st.selectbox(
    'Select date view:',
    ['week_num','month','date'])


st.title('Revenue Dashboard')
df = pd.read_excel('data/ptm.xlsx',engine='openpyxl', header=12)
df = hp.main_clean(df)


# drop unecessary columns
drop_cols = ['date','week_num','month','year','Checks', 'Discounts', 'Gross Sales', 'Per Check','Void','Avg Mins','Taxes', 'Avg Price','Avg Spend','Per Guest']

if date_options != 'date':
    drop_cols.append('week_day')


dftotal = hp.main_org(df, date_options, drop_cols, None)

st.write(dftotal)

# Line plot
st.subheader(f'Average Net Revenue per {date_options}')
st.line_chart(hp.plot_avg(df, date_options))

st.subheader(f'Average Revenue per Guests by: {date_options}')
st.line_chart(hp.customer_avg(df, date_options))

# Week day sales
dfweek = hp.weekday_df(df, None)
st.write(dfweek)