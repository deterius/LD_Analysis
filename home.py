import streamlit as st
import datetime

# import database as db 
import helpers as hp
import helpers2 as hp2
import skhelper as skh

import pandas as pd
import numpy as np

# import database as db 
import helpers as hp
import helpers2 as hp2
import plotly.express as px

from sklearn.preprocessing import MinMaxScaler

st.set_page_config (
    page_title = 'Revenue Dashboard Example',
    page_icon="🖖",
    layout='wide',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)


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
    st.title('Revenue Dashboard')
    st.subheader('Revenue Results per store')

    # date selectior
    date_options = {
        'No Grouping': None,
        'Group by Month': 'M',
        'Group by Week Number': 'W'
    }
    group_by = st.selectbox('Select Grouping Option', list(date_options.keys()))


    dfx = pd.read_excel('data/xtd.xlsx',engine='openpyxl', )
    dfk = pd.read_excel('data/kc.xlsx',engine='openpyxl', header=0)
    dfp = pd.read_excel('data/ptm.xlsx',engine='openpyxl', header=0)

    dfx = hp.main_clean(dfx)
    dfk = hp.main_clean(dfk)
    dfp = hp.main_clean(dfp)


    # Covert to Datetime Add Week, Month, Year, weekday
    df = pd.concat([dfx,dfk, dfp]).groupby('date').sum()
    df = df.reset_index()
    # df specify time window:
    # Add input widgets for minimum and maximum dates
    # Convert the 'date' column to datetime.date objects
    df['date'] = pd.to_datetime(df['date']).dt.date
    # Add input widgets for minimum and maximum dates
    min_date = st.date_input('Minimum Date', value=min(df['date']))
    max_date = st.date_input('Maximum Date', value=max(df['date']))
    # Filter the DataFrame based on the specified time period
    mask = (df['date'] >= min_date) & (df['date'] <= max_date)
    df = df[mask]

    df = df.set_index('date')




    df.index = pd.to_datetime(df.index)
    df['month'] = df.index.month
    df['week_num'] = df.index.isocalendar().week
    df['week_day']= df.index.weekday
    df['year'] = df.index.year
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
    drop_cols = ['week_num','month','year','Checks', 'Discounts', 'Gross Sales', 'Per Check','Void','Avg Mins','Taxes', 'Avg Price','Avg Spend','Per Guest']
    if date_options != 'date':
        drop_cols.append('week_day')

    # Metric results / group by date
    df['date'] = pd.to_datetime(df['date'])

    exclude_columns = ['Year','date','week_num']
    group_column = date_options[group_by]
    agg_functions = {column: 'sum' if column not in exclude_columns else 'first' for column in df.columns}
    df_metric = df.groupby(pd.Grouper(key='date', freq=group_column)).agg(agg_functions)

    # df_metric = df.groupby(date_options).sum()
    # Format the date column based on grouping option
    if group_by == 'Group by Month':
        df_metric['date'] = df_metric['date'].dt.to_period('M').dt.strftime('%Y-%m')
    elif group_by == 'Group by Week Number':
        df_metric['date'] = df_metric['date'].dt.to_period('W').dt.strftime('%Y-%W')


    rev_current = df_metric['Net Sales'].iloc[-1]
    rev_prev = df_metric['Net Sales'].iloc[-2]
    rev_delta = rev_current - rev_prev

    guest_current = df_metric['Guests'].iloc[-1]
    guest_prev = df_metric['Guests'].iloc[-2]
    guest_delta = float(guest_current - guest_prev)

    col1, col2, = st.columns(2)
    with col1:
        st.metric("Net Revenue", rev_current, delta=rev_delta, delta_color='normal', help='Change in revenue from previous time period')
    with col2:
        st.metric("Guest Count", guest_current, delta=guest_delta, delta_color='normal', help='Change in guests from previous time period')

    # dftotal = hp.main_sum_org(df, date_options, drop_cols, None)
    dftotal = hp2.main_sum(df_metric,drop_cols,None)


    # -----------------------
    # Metric results / group by date
    # transform DF
    df_metric = hp2.transform(df, 'sum', group_by, date_options)
    st.subheader("Averages 平均")
    dfmeans = hp2.transform(df, 'mean', group_by, date_options)
    st.write(hp2.main_mean(dfmeans))



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



    # main df
    with col1: 
        st.markdown(' *** ')
        st.subheader('Total (SUM)')
        st.dataframe(dftotal)
    with col2:
        # revenue chart
        st.markdown(' **** ')
        st.line_chart(df_metric['Net Sales'])    
        # guest count chart
        st.bar_chart(df_metric['Guests'])



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







