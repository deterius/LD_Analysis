import streamlit as st
import pandas as pd
import numpy as np

# import database as db 
import helpers as hp
import plotly.express as px




st.title('Revenue Dashboard')

# date selectior
date_options = st.selectbox(
    'Select date view:',
    ['week_num','month','date'])
st.write(date_options)

dfx = pd.read_excel('data/xtd.xlsx',engine='openpyxl', header=12)
dfk = pd.read_excel('data/kc.xlsx',engine='openpyxl', header=12)
dfp = pd.read_excel('data/ptm.xlsx',engine='openpyxl', header=12)

dfx = hp.main_clean(dfx)
dfk = hp.main_clean(dfk)
dfp = hp.main_clean(dfp)

# Covert to Datetime Add Week, Month, Year, weekday
df = pd.concat([dfx,dfk, dfp]).groupby('date').sum()
df.index = pd.to_datetime(df.index)
df['month'] = df.index.month
df['week_num'] = df.index.isocalendar().week
df['week_day']= df.index.weekday
df['year'] =df.index.year
 # remove week 52 
df.loc[df['week_num'] == 52, 'week_num'] = 0

 # remove hours and others from the date column
df.index = df.index.strftime('%Y-%m-%d')

# clean up weekdays
df.loc[df['week_day'] == 0, 'week_day'] = '1-monday'
df.loc[df['week_day'] == 1, 'week_day'] = '2-tuesday'
df.loc[df['week_day'] == 2, 'week_day'] = '3-wednesday'
df.loc[df['week_day'] == 3, 'week_day'] = '4-thursday'
df.loc[df['week_day'] == 4, 'week_day'] = '5-friday'
df.loc[df['week_day'] == 5, 'week_day'] = '6-saturday'
df.loc[df['week_day'] == 6, 'week_day'] = '7-sunday'

# make 'date' a column
df = df.reset_index()

# drop unecessary columns
drop_cols = ['date','week_num','month','year','Checks', 'Discounts', 'Gross Sales', 'Per Check','Void','Avg Mins','Taxes', 'Avg Price','Avg Spend','Per Guest']
if date_options != 'date':
    drop_cols.append('week_day')


dftotal = hp.main_sum_org(df, date_options, drop_cols, None)

st.subheader('Total (SUM)')
st.write(dftotal)

