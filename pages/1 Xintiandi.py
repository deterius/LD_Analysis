import streamlit as st
import pandas as pd
import numpy as np

# import database as db 
import helpers as hp
import helpers2 as hp2
import page_helpers as ph
import skhelper as skh


import plotly.express as px
from sklearn.preprocessing import MinMaxScaler


# date selectior
date_options = ph.date_options
group_by = ph.groupings(date_options)

st.title('Revenue Dashboard')
df = pd.read_excel('data/xtd.xlsx',engine='openpyxl', header=12)
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
# XTD Traffic & Revenue
# Apply a 3-month moving average to the 'revenue' column
if date_options[group_by] == None:
    window_size = 14
elif date_options[group_by] == 'M':
    window_size = 1
else:
    window_size = 4



dfmeans['smoothed_Traffic'] = dfmeans['Traffic'].rolling(window_size, min_periods=1).mean()
dfmeans['smoothed_revenue'] = dfmeans['Net Sales'].rolling(window_size, min_periods=1).mean()
dfmeans['smoothed_Per_Guest'] = dfmeans['Per_Guest'].rolling(window_size, min_periods=1).mean()
dfmeans['smoothed_Guests'] = dfmeans['Guests'].rolling(window_size, min_periods=1).mean()
df['smoothed_revenue'] = df['Net Sales'].rolling(window_size, min_periods=1).mean()
df['smoothed_Per_Guest'] = df['Per_Guest'].rolling(window_size, min_periods=1).mean()
df['smoothed_Guests'] = df['Guests'].rolling(window_size, min_periods=1).mean()


st.subheader(f'Average Net Revenue per {date_options[group_by]}')
st.line_chart(dfmeans['smoothed_revenue'])    

st.subheader(f'Average Revenue per Guests by: {date_options[group_by]}')
st.line_chart(dfmeans[['smoothed_Per_Guest','smoothed_Guests']])

# NORMALIZED NUMBERS


df_metric['smoothed_revenue'] = df_metric['Net Sales'].rolling(window_size, min_periods=1).mean()
df_metric['smoothed_Per_Guest'] = df_metric['Per_Guest'].rolling(window_size, min_periods=1).mean()
df_metric['smoothed_Guests'] = df_metric['Guests'].rolling(window_size, min_periods=1).mean()
df_metric['smoothed_Traffic'] = df_metric['Traffic'].rolling(window_size, min_periods=1).mean()
df_metric['smoothed_guest_conversion'] = df_metric['guest_conversion'].rolling(window_size, min_periods=1).mean()


# Select the columns to normalize
columns_to_normalize = ['smoothed_revenue', 'smoothed_Per_Guest', 'smoothed_Guests', 'smoothed_Traffic','smoothed_guest_conversion']
# Perform min-max scaling
scaler = MinMaxScaler()
df_metric[columns_to_normalize] = scaler.fit_transform(df_metric[columns_to_normalize])

st.subheader('NORAMLIZED: Revenue, Per-Guest, Guest Count')
st.line_chart(df_metric[['smoothed_revenue', 'smoothed_Per_Guest', 'smoothed_Guests']])

st.subheader('NORMALIZED: XTD Traffic, Guests, Revenue')
st.line_chart(df_metric[[ 'smoothed_Guests', 'smoothed_Traffic','smoothed_revenue',]])

st.subheader('ACTUAL: XTD Traffic & Revenue')
st.line_chart(dfmeans[['smoothed_revenue','smoothed_Traffic']])

st.subheader('NORMALIZED: XTD Traffic & Guest Conversion')
st.line_chart(df_metric[['smoothed_guest_conversion','smoothed_Traffic']])

# PLOT REGRESSION
# Call the regression function
plot = skh.regression(df)
st.pyplot(plot)