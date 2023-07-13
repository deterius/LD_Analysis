import pandas as pd
import numpy as np
import streamlit as st

def transform(df, aggType, group_by, date_options):
    # transform DF
    df['Per_Guest'] = df['Net Sales'] / df['Guests']
    try:
        df['guest_conversion'] = df['Guests'] / df['Traffc']
    except:
        pass
        

   # Drop the 'week_day' column
    if aggType == 'mean':
        df = df.drop('week_day', axis=1)
    
    df['date'] = pd.to_datetime(df['date'])
    exclude_columns = ['Year','date','week_num']
    group_column = date_options[group_by]
    agg_functions = {column: aggType if column not in exclude_columns else 'first' for column in df.columns}
    df_metric = df.groupby(pd.Grouper(key='date', freq=group_column)).agg(agg_functions)

    # Format the date column based on grouping option
    if group_by == 'Group by Month':
        df_metric['date'] = df_metric['date'].dt.to_period('M').dt.strftime('%Y-%m')
    elif group_by == 'Group by Week Number':
        df_metric['date'] = df_metric['date'].dt.to_period('W').dt.strftime('%Y-%W')

    return df_metric

def main_sum(df, drop_cols, traffic):
    
    common_cols = ['date','Gross Sales', 'Net Sales', 'Avg Price', 'Discounts', 'Taxes',
        'Guests', 'Per Guest', 'Checks', 'Per Check', 'Void', 'Avg Spend',
        'Avg Mins', 'month', 'week_num', 'week_day', 'year'] 
        
   
    df['Per_Guest'] = df['Net Sales'] / df['Guests']
    df = df.set_index('date')
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


def main_org(df, drop_cols, traffic):
    
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
                        'Discounts':"{:,.0f}",
                        }
                    )
                # .format("{:,.0f}") ALL COLUMNS
                .background_gradient( subset=['Per_Guest'],cmap='Blues')
                .background_gradient( subset=['Net Sales'], cmap='viridis')
                .background_gradient( subset=['Guests'], cmap='OrRd')
                .background_gradient( subset=['Discounts'], cmap='viridis')
                )

    return df


def main_mean(df):
    df = df[['date','Net Sales', 'Discounts', 'Guests']]
    df = df.set_index('date')
    df['Per_Guest'] = df['Net Sales'] / df['Guests']
    
    # style!
    df = (df
                .style
                .format(
                        {
                        'Net Sales':"¥{:,.0f}",
                        'Per_Guest':"¥{:,.0f}",
                        'guest_conversion':"% {:,.3f}",
                        'Traffic':"{:,.0f}",
                        'Guests':"{:,.0f}",
                        'Discounts':"{:,.0f}",
                        }
                    )
                # .format("{:,.0f}") ALL COLUMNS
                .background_gradient( subset=['Per_Guest'],cmap='Blues')
                .background_gradient( subset=['Net Sales'], cmap='viridis')
                .background_gradient( subset=['Guests'], cmap='OrRd')
                .background_gradient( subset=['Discounts'], cmap='viridis')
                )
    return df