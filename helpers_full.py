import warnings
import pandas as pd
from openpyxl import styles
import re
import helpers as hp
import helpers2 as hp2




def clean(df):
    # Suppress the warning
    warnings.filterwarnings("ignore", category=UserWarning, module=styles.stylesheet.__name__)
    
    df['Item Code'] = df['Item Code'].astype(str)
    df['date'] = pd.to_datetime(df['date'])

    # Dictionary for item code prefixes and categories
    item_code_categories = {
        'BA':'Sets',
        'BB': 'Savory',
        'BC': 'Pastries',
        'BCK':'Pastries',
        'BKS':'Viennoiseries',
        'BE':'Beverage',
        'BK':'Viennoiseries',
        'CA': 'Secrets',
        'CF':'Beverage',
        'CH':'Beverage',
        'CHG':'Grocery',
        'CI':'Beverage',
        'CK':'Pastries',
        'CP':'Beverage',
        'CT':'Beverage',
        'DS':'Savory',
        'DJ':'Savory',
        'DP':'Sets',
        'DY':'Douyin',
        'DSS':'Savory',
        'FS':'Sets',
        'FT':'French Toast',
        'GB':'Macarons',
        'HS':'Sets',
        'IC':'Ice Cream',
        'JU':'Beverage',
        'LY':'Event Boxes',
        'KC':'Secrets',
        'MA':'Macarons',
        'MC':'Savory',
        'MCS':'Savory',
        'OT':'Pastries',
        'RS':'Secrets',
        'RW':'Beverage',
        'SA':'Savory',
        'SD':'Savory',
        'SDS':'Savory',
        'SF':'Beverage',
        'SM':'Beverage',
        'SW':'Savory',
        'TB':'Grocery',
        'TE':'Beverage',
        'TP':'Savory',
        'TPS':'Savory',
        'WW':'Beverage',
        'WM':'Sets',
        

    }

    # Function to categorize item codes
    def categorize_item_code(item_code):
        
        prefix = re.sub('\d', '', item_code)  # Extract all the letters
        
        if prefix not in item_code_categories:
            print(f"Missing prefix: {prefix}")
        return item_code_categories.get(prefix, prefix)



    # Create a new column with the product categories
    df['Category'] = df['Item Code'].apply(categorize_item_code)

    # add months & years
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year


    # Special Categories
    df.loc[df['Item Code'] == 'FS005', 'Category'] = 'Afternoon Set'
    df.loc[df['Item Code'] == 'DY003', 'Category'] = 'Afternoon Set'
    df.loc[df['Item Code'] == 'FS031', 'Category'] = 'Macarons'
    df.loc[df['Item Code'] == 'FS034', 'Category'] = 'Macarons'
    df.loc[df['Item Code'] == 'DY004', 'Category'] = 'Macarons'
    
    
    # Strip leading and trailing white spaces from column headers
    df.columns = df.columns.str.strip()

    # Keep only releveant columns
    df = df[['store','Category', 'month','year', 'Item Code' ,'Item Name','Gross Sales', 'Net Sales', 'Qty Sold']]
    
    # Delete blanks
    df = df.drop(df[df['Category'] == ''].index)
    df = df.drop(df[df['Category'] == 'MSG'].index)

    
    return df


def filter_store(df,store):
    if store == 'ALL':
        return df
    else: 
        return df[df['store']== store]
    
    
def pivot(df, metrics):
    # Create a pivot table to calculate the sum of quantity sold month by month

    pivot_table = df.pivot_table(values=metrics, index='Category', columns='month', aggfunc='sum')

    # Sort the columns in chronological order
    pivot_table = pivot_table.reindex(sorted(pivot_table.columns), axis=1)
    
    # Calculate the totals and append them as a new row
    # totals = pivot_table.sum(axis=0)
    # pivot_table.loc['<<Total>>'] = totals
    
    

    return pivot_table

def style_pivot(pivot_table):
    # Apply conditional formatting to each row
    pivot_table_styled = pivot_table.style.background_gradient(cmap='YlGnBu', axis=1)

    # Format all numbers as whole numbers
    pivot_table_styled = pivot_table_styled.format("{:,.0f}")
    return pivot_table_styled

def get_guests(store):
    def clean_guests(df_guests):
        df_guests = hp.main_clean(df_guests)
        # Exclude rows with year 2022 and month 7
        df_guests = df_guests.loc[df_guests['year'] != 2022]
        df_guests = df_guests.loc[df_guests['month'] != 7]
        # Group by 'Month' and apply sum() while excluding 'Year'
        df_guests = df_guests.groupby('month').agg({ 'Guests': 'sum'}).reset_index()
        df_guests = df_guests.transpose()
        df_guests.columns = df_guests.iloc[0]
        df = df_guests.drop(labels=['month'],axis=0)
        return df
    
    if store == 'KC':
        df_guests = pd.read_excel('data/kc.xlsx',engine='openpyxl', header=0)
        df = clean_guests(df_guests)
    elif store == 'XTD':
        df_guests = pd.read_excel('data/xtd.xlsx',engine='openpyxl', header=0)
        df = clean_guests(df_guests)

    elif store == 'PTM':
        df_guests = pd.read_excel('data/ptm.xlsx',engine='openpyxl', header=0)
        df = clean_guests(df_guests)

    else:
        dfk = pd.read_excel('data/kc.xlsx',engine='openpyxl', header=0)
        dfx = pd.read_excel('data/xtd.xlsx',engine='openpyxl', header=0)
        dfp = pd.read_excel('data/ptm.xlsx',engine='openpyxl', header=0)
        
        dfk = hp.main_clean(dfk)
        dfx = hp.main_clean(dfx)
        dfp = hp.main_clean(dfp)
    
        
        dfm = pd.concat([dfk, dfx, dfp]).groupby(['date']).sum().reset_index()
        
        dfm = clean_guests(dfm)
        
        # dfm = clean_guests(dfm)
        
        return dfm

    return df


def pcnt_df(df):
    df_pcnt_qty = df.apply(lambda x: x / x.sum() * 100).round(2)
    df_pcnt_qty = df_pcnt_qty.style.background_gradient(cmap='YlGnBu', axis=1).format("{:,.1f}%")
    return df_pcnt_qty
