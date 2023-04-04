import pandas as pd
import numpy as np
import streamlit as st

def main_clean(df):
    df = df.drop(df.index[[0,1]])
    df = df.rename(columns={'Unnamed: 0':'date'})
    df = df.drop(columns=['Code','Cost','Cost %','Profit','Profit %','Service Charges','Table Turns','Rev. /m²','Seat Occ. %','Tips','Table Use'])

    # Covert to Datetime Add Week, Month, Year, weekday
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['week_num'] = df['date'].dt.isocalendar().week
    df['week_day']= df['date'].dt.weekday
    df['year'] =df['date'].dt.year
    
    # remove hours and others from the date column
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    
    # guest conversion
    try:
        df['guest_conversion'] =  df['Guests'] / df['Traffic']
    except:
        pass
    
    # remove week 52 
    df.loc[df['week_num'] == 52, 'week_num'] = 0
    
    # clean up weekdays
    df.loc[df['week_day'] == 0, 'week_day'] = '1-monday'
    df.loc[df['week_day'] == 1, 'week_day'] = '2-tuesday'
    df.loc[df['week_day'] == 2, 'week_day'] = '3-wednesday'
    df.loc[df['week_day'] == 3, 'week_day'] = '4-thursday'
    df.loc[df['week_day'] == 4, 'week_day'] = '5-friday'
    df.loc[df['week_day'] == 5, 'week_day'] = '6-saturday'
    df.loc[df['week_day'] == 6, 'week_day'] = '7-sunday'
    
    # round the numbers
    
    
    
    return df

def main_org(df, date_options, drop_cols, traffic):
    
    common_cols = ['date','Gross Sales', 'Net Sales', 'Avg Price', 'Discounts', 'Taxes',
        'Guests', 'Per Guest', 'Checks', 'Per Check', 'Void', 'Avg Spend',
        'Avg Mins', 'month', 'week_num', 'week_day', 'year']     

    if traffic is not None:
        common_cols.append('Traffic')
        common_cols.append('guest_conversion')
    agg_cols = {}
    # ------- select categories
    def categories_select():
        for col in common_cols:
            if col == 'year' or col == 'month' or col == 'week_num' or col == 'week_day' or col == 'date':
                agg_cols[col] = 'first'
            else:
                agg_cols[col] = 'mean'
        return True


    categories_select()
    
    
    # organizes by date selected and aggs all the other columns
    df = df.groupby(['year', date_options]).agg(agg_cols).sort_index(ascending=True)

    df['Per_Guest'] = df['Net Sales'] / df['Guests']
    
    # style!
    df = (df
                .drop(columns=drop_cols)
                .style
                .format(
                        {
                        'Net Sales':"¥{:,.0f}",
                        'Per_Guest':"¥{:,.0f}",
                        'guest_conversion':"% {:,.3f}",
                        'Traffic':"{:,.0f}",
                        'Guests':"{:,.0f}",
                        }
                    )
                # .format("{:,.0f}") ALL COLUMNS
                .background_gradient( subset=['Per_Guest'],cmap='Blues')
                .background_gradient( subset=['Net Sales'], cmap='viridis')
                .background_gradient( subset=['Guests'], cmap='OrRd')
                )

    return df

def main_sum_org(df, date_options, drop_cols, traffic):
    
    common_cols = ['date','Gross Sales', 'Net Sales', 'Avg Price', 'Discounts', 'Taxes',
        'Guests', 'Per Guest', 'Checks', 'Per Check', 'Void', 'Avg Spend',
        'Avg Mins', 'month', 'week_num', 'week_day', 'year']     

    if traffic is not None:
        common_cols.append('Traffic')
        common_cols.append('guest_conversion')
    agg_cols = {}
    # ------- select categories
    def categories_select():
        for col in common_cols:
            if col == 'year' or col == 'month' or col == 'week_num' or col == 'week_day' or col == 'date':
                agg_cols[col] = 'first'
            else:
                agg_cols[col] = 'sum'
        return True


    categories_select()
    
    
    # organizes by date selected and aggs all the other columns
    df = df.groupby(['year', date_options]).agg(agg_cols).sort_index(ascending=True)

    df['Per_Guest'] = df['Net Sales'] / df['Guests']
    
    # style!
    df = (df
                .drop(columns=drop_cols)
                .style
                .format(
                        {
                        'Net Sales':"¥{:,.0f}",
                        'Per_Guest':"¥{:,.0f}",
                        'guest_conversion':"% {:,.3f}",
                        'Traffic':"{:,.0f}",
                        'Guests':"{:,.0f}",
                        }
                    )
                # .format("{:,.0f}") ALL COLUMNS
                .background_gradient( subset=['Per_Guest'],cmap='Blues')
                .background_gradient( subset=['Net Sales'], cmap='viridis')
                .background_gradient( subset=['Guests'], cmap='OrRd')
                )

    return df

def weekday_df(df, traffic):
    cols = ['Net Sales','Guests','avg guest spend']
    
    if traffic is not None:
        cols.append('Traffic')
        cols.append('guest_conversion')
    
    
    dfweek = df.groupby(['month','week_day']).mean()
    dfweek['avg guest spend']= dfweek['Net Sales']/ dfweek['Guests']
    dfweek[cols].style.format("{:,.0f}")
    
    drop_cols = ['week_num','year','Checks', 'Discounts', 'Gross Sales', 'Per Check','Void','Avg Mins','Taxes', 'Avg Price','Avg Spend','Per Guest']

    # style!
    dfweek = (dfweek
                .drop(columns=drop_cols)
                .style
                .format(
                        {
                        'Net Sales':"¥{:,.0f}",
                        'avg guest spend':"¥{:,.0f}",
                        'Traffic':"{:,.0f}",
                        'Guests':"{:,.0f}",
                        }
                    )
                # .format("{:,.0f}") ALL COLUMNS
                .background_gradient( subset=['avg guest spend'],cmap='Blues')
                .background_gradient( subset=['Net Sales'], cmap='viridis')
                .background_gradient( subset=['Guests'], cmap='OrRd')
                )

    
    
    return dfweek


# Plot Line Chart of averages
def plot_avg(df,date_options):
    dfchart = df.groupby(['year',date_options]).mean().reset_index()
    return dfchart['Net Sales']

# Plot Line Chart of average customer spend
def customer_avg(df,date_options):
    dfavg = df.groupby(['year',date_options]).mean().reset_index()
    dfavg['Avg Guest Spend'] = dfavg['Net Sales'] / dfavg['Guests']
    return dfavg[['Avg Guest Spend','Guests']]