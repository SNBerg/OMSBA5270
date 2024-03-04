# -*- coding: utf-8 -*-
"""
Class: OMSBA 5270 01 24 WQ
Author: Sirina Berg
Source : https://www.sec.gov/edgar/sec-api-documentation

Objectives:
1. Data Extraction and Processing: Utilize the EDGAR API to extract financial statements of a single company. Focus on key financial ratios that are indicative of a company's health, such as P/E ratio, debt-to-equity ratio, return on equity, etc.
- Focus on 5 data points with 3 of them being financial ratios - if you reported on revenue, that is a standard data point and not a financial ratio.
2. Stock Price Data Integration: Incorporate historical stock price data for the same set of companies. This data can be sourced from APIs like Yahoo Finance or Alpha Vantage.
3. Correlation Analysis: Conduct statistical analysis to examine the correlation between changes in financial ratios and subsequent stock price movements. Explore both short-term and long-term effects.
4. Event Study: Perform an event study around the dates of significant financial disclosures (e.g., annual reports, quarterly earnings) to observe stock price reactions before and after these events.
"""

# import libraries
import requests
import pandas as pd
from datetime import datetime, timedelta
from tabulate import tabulate # to create ratio tables
import numpy as np 
from numpy import median
from scipy.stats import linregress

import plotly
import plotly.express as px
import plotly.graph_objects as go # for combo chart

import seaborn as sns # for plot correlation heatmap
import matplotlib.pyplot as plt

# if using Spyder
# import plotly.io as pio
# pio.renderers.default='browser'
# pio.renderers.default = "svg"

import warnings
warnings.filterwarnings('ignore')

# setup display so it shows all columns
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

pd.options.plotting.backend = 'plotly'

# set number float format
pd.options.display.float_format = '{:.2f}'.format

""" Data pre-processing """
# create a request header
# using seattlu account to identify me as a user who makes a request
headers = {'User-Agent' : "sberg@seattleu.edu"}

# get all companies data from the company_tickers.json
# this will return a set of dictionary with cik_str (cik number), ticker (company symbol), title (company name)
companyTickers = requests.get(f"https://www.sec.gov/files/company_tickers.json", headers=headers)
# print(companyTickers.json())

companyCIK = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
# print(companyCIK)

# adding leading 0s
companyCIK['cik_str'] = companyCIK['cik_str'].astype(str).str.zfill(10)
# print(companyCIK)

"""
COSTCO WHOLESALE CORP (COST) 0000909832
Costco Wholesale Corporation is an American multinational corporation that operates a chain of membership-only big-box warehouse club retail stores. 
Founded in the 1980s by Jim Sinegal and Jeffrey H. Brotman, the first store opened in Seattle, Washington. 
The current CEO and director is Craig Jelinek. Costco Wholesales has 875 warehouses (as of 2/22/2024). 
In 2023, it is the third-largest retailer in the world with annual net sales of $237.7B.
  
"""
# get company cik_str
ticker_symbol = 'COST'
cik = companyCIK.loc[companyCIK['ticker'] == ticker_symbol, 'cik_str'].iloc[0]
# print(cik) # 0000909832
print(companyCIK[companyCIK['cik_str']==cik])

""" 
Data retrieval and EDA 

Source: data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:
https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
"""

companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
# print(companyFacts.json().keys())
# print(companyFacts.json()['facts'])

""" Functions to get data from each key """
def getdata(key, form):
    df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap'][key]['units']['USD'])
    df = df.sort_values(by=['end', 'filed'])
    # print(df)
    
    # filter to use form 10-K
    df_filtered = df[df['form'] == form]
    df_filtered = df_filtered.reset_index(drop=True)
    # print(dffiltered)

    # exploring data
    print(df.info())
    print(median(df['val']), min(df['end']), max(df['end']))
    print(df.describe())
    return(df, df_filtered)

# get revenues data
"""
RevenueFromContractWithCustomerExcludingAssessedTax
Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer.
Tax collected from customer is tax assessed by governmental authority that is both imposed on and concurrent with specific revenue-producing transaction, 
including, but not limited to, sales, use, value added and excise.
"""
revenue_df, revenue_df_filtered = getdata('Revenues', '10-K')
# observations: no null data, 288 rows start date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# has start and end date, has quarterly and annual data presented
# Note on data anormally: 10-K contains all annual data but not all quarterly data were reported. Quarterly filing missing after FY17.
# has NaN in frame column - need to clean up
# end date is object type

# additional revenue data to get quarterly data for using in stock price analysis from FY2017 and onward
revenue2k_df, revenue2k_df_filtered = getdata('RevenueFromContractWithCustomerExcludingAssessedTax', '10-K')
# print(revenue2k_df_filtered) # 2016-08-28 2023-11-26

# additional data to get quarterly data from 8/31/2020
revenue2q_df, revenue2q_df_filtered = getdata('RevenueFromContractWithCustomerExcludingAssessedTax', '10-Q')
# print(revenue2q_df_filtered) # 2016-08-28 2023-11-26

# get Assets and convert the facts on assets to a dataframe
"""
Assets 
Sum of the carrying amounts as of the balance sheet date of all assets that are recognized. 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
assets_df, assets_df_filtered = getdata('Assets', '10-K')
# print(assets_df)

# check 10-Q
# assetsq_df, assetsq_df_filtered = getdata('Assets', '10-Q')
# assetsq_df = assetsq_df.drop_duplicates('end')
# assetsq_df = assetsq_df.reset_index(drop=True)
# print(assetsq_df['filed'].unique())
# print(assetsq_df_filtered)

# observations: no null data, 158 rows end date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end date - need to clean up
# end date is object type

# get current assets
"""
AssetsCurrent
Sum of the carrying amounts as of the balance sheet date of all assets that are expected to be realized in cash, sold, or consumed within one year (or the normal operating cycle, if longer). 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
cur_assets_df, cur_assets_df_filtered = getdata('AssetsCurrent', '10-K')
# observations: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# get liabilities data and convert the facts on assets to a dataframe
"""
Liabilities
Sum of the carrying amounts as of the balance sheet date of all liabilities that are recognized. 
Liabilities are probable future sacrifices of economic benefits arising from present obligations of an entity to transfer assets 
or provide services to other entities in the future.
"""
liabilities_df, liabilities_df_filtered = getdata('Liabilities', '10-K')
# observations: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# get current liabilities
"""
LiabilitiesCurrent
Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
"""
cur_liabilities_df, cur_libilities_df_filtered = getdata('LiabilitiesCurrent', '10-K') 
# observations: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# get stockholders' equity
"""
StockholdersEquity
Total of all stockholders' equity (deficit) items, net of receivables from officers, directors, owners, and affiliates of the entity which are attributable to the parent.
The amount of the economic entity's stockholders' equity attributable to the parent excludes the amount of stockholders' equity 
which is allocable to that ownership interest in subsidiary equity which is not attributable to the parent (noncontrolling interest, minority interest). 
This excludes temporary equity and is sometimes called permanent equity.
"""
equity_df, equity_df_filtered = getdata('StockholdersEquity', '10-K') 
# observations: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# get net income
"""
NetIncomeLossLoss
The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
"""
netincome_df, netincome_df_filtered = getdata('NetIncomeLoss', '10-K') 
# observations: no null data, 272 rows end date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# has start and end date, has quarterly and annual data presented
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# print(companyFacts.json()['facts']['us-gaap']['CommonStockDividendsPerShareDeclared']['units'].keys())#dict_keys(['pure', 'USD/shares']
# print(companyFacts.json()['facts']['us-gaap']['CommonStockDividendsPerShareDeclared']['units']['USD/shares'])

dividend_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['CommonStockDividendsPerShareDeclared']['units']['USD/shares'])
dividend_df_filtered = dividend_df[dividend_df['form']=='10-K']
print(dividend_df_filtered)
# observations: dividend reports up to 2020-11-22 both form 10-Q and 10-K. There is a mentioned in the 10-K report for 2023 but no filed data

"""
Data cleaning and wrangling - cleanup duplicated row and prepare data for the next step
"""

def cleanup(df, year):
    """ Function to filter for specific year data set """
    # make a copy of the data frame
    df = df.copy()

    # remove duplicated rows of the same 'end' date and keep the row with the last filed
    df = df.drop_duplicates(subset=['end'], keep='last')

    # create a temp date column since our data has the object type
    df['end_date'] = pd.to_datetime(df['end'])

    # filter to a specific year
    df = df[df['end_date'].dt.year >= year]
    df = df.drop(columns=['end_date'])
    df = df.reset_index(drop=True)
 
    return df

# getting annual revenue data
# make a copy of the filter dataframe to create a clean dataframe
revenue_df_clean = revenue_df_filtered.copy()

# remove quarterly data by calculate the duration between start and end. Quarterly durations
# convert to start and end date to datetime
revenue_df_clean['start'] = pd.to_datetime(revenue_df_clean['start'])
revenue_df_clean['end'] = pd.to_datetime(revenue_df_clean['end'])
revenue_df_clean['months_diff'] = ((revenue_df_clean['end'] - revenue_df_clean['start']) / pd.Timedelta(days=30)).astype(int)
revenue_df_clean = revenue_df_clean[revenue_df_clean['months_diff'] >= 12] # there are the same record that filed multiple times, need to drop duplicated
revenue_df_clean = revenue_df_clean.drop(columns=['months_diff']) 

# remove duplicated rows of the same 'end' date and keep the row with the last filed and filter the end year
revenue_df_clean = cleanup(revenue_df_clean, 2013) 
# print(revenue_df_filtered, revenue_df_clean) # 2008-08-31 to 2023-09-03 # new 2013-09-01 to 2023-09-03

# getting quarterly revenue data from two revenue keys plus form 10-Q and 10-K to fill out the filiing gap in the dataset
# get the first portion of quarterly data from Revenues file up to FY2016
revenuek_df_clean = revenue_df_filtered.copy()

# calculate the duration between start and end. Quarterly durations = 2 or 3 months.
# convert to start and end date to datetime
revenuek_df_clean['start'] = pd.to_datetime(revenuek_df_clean['start'])
revenuek_df_clean['end'] = pd.to_datetime(revenuek_df_clean['end'])

# filter for FY2013-2016 
revenuek_df_clean = revenuek_df_clean[(revenuek_df_clean['start'] >= '9/3/2012') & (revenuek_df_clean['start'] <= '5/8/2017')]

revenuek_df_clean['months_diff'] = ((revenuek_df_clean['end'] - revenuek_df_clean['start']) / pd.Timedelta(days=30)).astype(int)
revenuek_df_clean = revenuek_df_clean[revenuek_df_clean['months_diff'] < 12] # there are the same record that filed multiple times, need to drop duplicated
revenuek_df_clean = revenuek_df_clean.drop(columns=['months_diff']) 
revenuek_df_clean = revenuek_df_clean.drop_duplicates(subset=['end'], keep='last')
print(revenuek_df_clean)

# get the second portion of the revenues from other revenue file up to FY2023
revenue2k_df_clean = revenue2k_df_filtered.copy()

# calculate the duration between start and end. Quarterly durations = 2 or 3 months.
# convert to start and end date to datetime
revenue2k_df_clean['start'] = pd.to_datetime(revenue2k_df_clean['start'])
revenue2k_df_clean['end'] = pd.to_datetime(revenue2k_df_clean['end'])

# filter for FY2016-2020 
revenue2k_df_clean = revenue2k_df_clean[(revenue2k_df_clean['start'] >= '9/4/2017')]

revenue2k_df_clean['months_diff'] = ((revenue2k_df_clean['end'] - revenue2k_df_clean['start']) / pd.Timedelta(days=30)).astype(int)
revenue2k_df_clean = revenue2k_df_clean[revenue2k_df_clean['months_diff'] < 12] # there are the same record that filed multiple times, need to drop duplicated
revenue2k_df_clean = revenue2k_df_clean.drop(columns=['months_diff']) 
revenue2k_df_clean = revenue2k_df_clean.drop_duplicates(subset=['end'], keep='last')
print(revenue2k_df_clean)

# combine data
combined_revenues = pd.concat([revenuek_df_clean, revenue2k_df_clean], ignore_index=True)
print(combined_revenues)

# get data quarterly data from 2020 - 2023
revenue2q_df_clean = revenue2q_df_filtered.copy()

# calculate the duration between start and end. Quarterly durations = 2 or 3 months.
# convert to start and end date to datetime
revenue2q_df_clean['start'] = pd.to_datetime(revenue2q_df_clean['start'])
revenue2q_df_clean['end'] = pd.to_datetime(revenue2q_df_clean['end'])

# filter for FY2016-2020 
revenue2q_df_clean = revenue2q_df_clean[(revenue2q_df_clean['start'] >= '8/31/2020')]

revenue2q_df_clean['months_diff'] = ((revenue2q_df_clean['end'] - revenue2q_df_clean['start']) / pd.Timedelta(days=30)).astype(int)
revenue2q_df_clean = revenue2q_df_clean[revenue2q_df_clean['months_diff'] < 5] # there are the same record that filed multiple times, need to drop duplicated
revenue2q_df_clean = revenue2q_df_clean.drop(columns=['months_diff']) 
revenue2q_df_clean = revenue2q_df_clean.drop_duplicates(subset=['end'], keep='last')
print(revenue2q_df_clean)

combined_revenues = pd.concat([combined_revenues, revenue2q_df_clean], ignore_index=True)
print(combined_revenues)

# sum revenues from the first 3 quarter to get the 4th quarter from annual revenues
revenue2q_df_sum = revenue2q_df_clean.copy()
revenue2q_df_sum = revenue2q_df_clean.reset_index(drop=True) # reset index to start from 0
print(revenue2q_df_sum)

start_index = 0
rev= {} # dictionary to collect sum of Q1+Q2+Q3

# iterate over the df in chunk of 3 rows
for i in range(start_index, len(revenue2q_df_sum), 3):
    rows_to_sum = revenue2q_df_sum.iloc[i:i+3]
    rev_sum = rows_to_sum['val'].sum()
    end_date = rows_to_sum.iloc[0]['start']
    rev[end_date] = rev_sum 
# print(rev)

# convert to Dataframe
rev_df = pd.DataFrame.from_dict(rev, orient='index', columns=['val'])
print(rev_df)

# get the Q4 data by derived from annual revenue - Q1-Q3
revenue2k_df_annual = revenue2k_df_filtered.copy()

# convert start/end date to datetime
revenue2k_df_annual['start'] = pd.to_datetime(revenue2k_df_annual['start'])
revenue2k_df_annual['end'] = pd.to_datetime(revenue2k_df_annual['end'])

 # filter for the annual revenue for FY2021-2023
revenue2k_df_annual = revenue2k_df_annual[revenue2k_df_annual['start'] >= '8/31/2020']
revenue2k_df_annual = revenue2k_df_annual.dropna()
print(revenue2k_df_annual)

# create a new column to capture calculated quarterly revenue
revenue2k_df_annual['val_q'] = revenue2k_df_annual['val'] - revenue2k_df_annual['start'].map(rev) 

# add the missing quarterly start date to the dataframe
start_q = ['5/10/2021', '5/9/2022', '5/8/2023']
start_q_date = pd.to_datetime(start_q)
revenue2k_df_annual['start_q'] = start_q_date

revenue2k_df_missing = revenue2k_df_annual.copy()
revenue2k_df_missing = revenue2k_df_missing[['start_q', 'end', 'val_q', 'accn', 'fy', 'fp', 'form', 'filed', 'frame']]
revenue2k_df_missing = revenue2k_df_missing.rename(columns={'val_q': 'val', 'start_q': 'start'})
print(revenue2k_df_missing)

# add missing quarters to the dataframe
combined_revenues = pd.concat([combined_revenues, revenue2k_df_missing], ignore_index=True)
combined_revenues = combined_revenues.sort_values(by=['end'])
combined_revenues = combined_revenues.reset_index(drop=True)
print(combined_revenues) # 45 rows # end date from 2012-11-25 to 2023-11-26

# print(assets_df_filtered) # 2009-08-31 to 2023-09-03
assets_df_clean = cleanup(assets_df_filtered, 2013)
# print(assets_df_clean) # 2013-09-01 to 2023-09-03

# print(cur_assets_df_filtered) # 2009-08-30 to 2023-09-03
cur_assets_df_clean = cleanup(cur_assets_df_filtered, 2013)
# print(cur_assets_df_clean) # 2013-09-01 to 2023-09-03

# print(liabilities_df_filtered) #2009-08-30 to 2023-09-03
liabilities_df_clean = cleanup(liabilities_df_filtered, 2013)
# print(liabilities_df_clean) # 2013-09-01 to 2023-09-03

# print(cur_libilities_df_filtered) #2009-08-30 to 2023-09-03
cur_libilities_df_clean = cleanup(cur_libilities_df_filtered, 2013)
# print(cur_libilities_df_clean) # 2013-09-01 to 2023-09-03

# print(equity_df_filtered) #2009-08-30 to 2023-09-03
equity_df_clean = cleanup(equity_df_filtered, 2013)
# print(equity_df_clean) # 2013-09-01 to 2023-09-03

# remove quarterly data by calculate the duration between start and end. Quarterly durations
# make a copy of netincome_df_filtered to netincome_df_clean
netincome_df_clean = netincome_df_filtered.copy()

# convert to start and end date to datetime
netincome_df_clean['start'] = pd.to_datetime(netincome_df_clean['start'])
netincome_df_clean['end'] = pd.to_datetime(netincome_df_clean['end'])
netincome_df_clean['months_diff'] = ((netincome_df_clean['end'] - netincome_df_clean['start']) / pd.Timedelta(days=30)).astype(int)
netincome_df_clean = netincome_df_clean[netincome_df_clean['months_diff'] >= 12] # there are the same record that filed multiple times, need to drop duplicated
netincome_df_clean = netincome_df_clean.drop(columns=['months_diff']) 
# print(netincome_df_filtered, netincome_df_clean) # 2008-08-31 to 2023-09-03

# remove duplicated of the same 'end' date, keep the last filed record and filter for end year period.
netincome_df_clean = cleanup(netincome_df_clean, 2013) 
# print(netincome_df_clean) # 2013-09-01 to 2023-09-03

""" Merge data"""
# merge data together to prepare for calculating ratio, analysis, and visualization

# assets and liabilities
merged_asst_li_df = pd.merge(assets_df_clean, liabilities_df_clean, on=['end'], how='inner')
# print(merged_asst_li_df.columns)

# drop un-used columns
merged_asst_li_df = merged_asst_li_df[['end', 'val_x', 'val_y', 'form_x', 'filed_x', 'frame_x']]
merged_asst_li_df = merged_asst_li_df.rename(columns={'val_x': 'assets', 'val_y': 'liabilities', 'form_x': 'form', 'filed_x': 'filed', 'frame_x': 'frame'})
# print(merged_asst_li_df)

# current assets and current liabilities
merged_cur_asst_li_df = pd.merge(cur_assets_df_clean, cur_libilities_df_clean, on=['end'], how='inner')
# print(merged_cur_asst_li_df.columns)

# drop un-used columns and rename columns
merged_cur_asst_li_df = merged_cur_asst_li_df[['end', 'val_x', 'val_y', 'form_x', 'filed_x', 'frame_x']]
merged_cur_asst_li_df = merged_cur_asst_li_df.rename(columns={'val_x': 'cur_assets', 'val_y': 'cur_liabilities', 'form_x': 'form', 'filed_x': 'filed', 'frame_x': 'frame'})
# print(merged_cur_asst_li_df)

# revenues and net income
merged_rev_inc_df = pd.merge(revenue_df_clean, netincome_df_clean, on=['end'], how='inner')
# print(merged_rev_inc_df.columns)

# drop un-used columns and rename columns
merged_rev_inc_df = merged_rev_inc_df[['end', 'val_x', 'val_y', 'form_x', 'filed_x', 'frame_x']]
merged_rev_inc_df = merged_rev_inc_df.rename(columns={'val_x': 'revenues', 'val_y': 'netincome', 'form_x': 'form', 'filed_x': 'filed', 'frame_x': 'frame'})
# print(merged_rev_inc_df)

# assets/liabilities and current assets/current liabilities
merged_all_asst_li_df = pd.merge(merged_asst_li_df, merged_cur_asst_li_df, on=['end'], how='inner')
# print(merged_all_asst_li_df.columns)

# drop un-used columns
merged_all_asst_li_df = merged_all_asst_li_df[['end', 'assets', 'liabilities', 'cur_assets', 'cur_liabilities', 'form_x', 'filed_x', 'frame_x']]
merged_all_asst_li_df = merged_all_asst_li_df.rename(columns={'form_x': 'form', 'filed_x': 'filed', 'frame_x': 'frame'})
# print(merged_all_asst_li_df)

# merge revenues/net income to the df
# convert end date from datetime type to string to merge with the rest of the data
merged_rev_inc_df['end'] = merged_rev_inc_df['end'].dt.strftime('%Y-%m-%d')
# print(merged_rev_inc_df.info())

merged_df = pd.merge(merged_all_asst_li_df, merged_rev_inc_df, on=['end'], how='inner')

# drop un-used columns
merged_df = merged_df[['end', 'assets', 'liabilities', 'cur_assets', 'cur_liabilities', 'revenues', 'netincome', 'form_x', 'filed_x', 'frame_x']]
merged_df = merged_df.rename(columns={'form_x': 'form', 'filed_x': 'filed', 'frame_x': 'frame'})
# print(merged_df)

# merge equity to the df
merged_df = pd.merge(merged_df, equity_df_clean, on=['end'], how='inner')
# print(merged_df.columns)

# drop un-used columns
merged_df = merged_df[['end', 'assets', 'liabilities', 'cur_assets', 'cur_liabilities', 'revenues', 'netincome', 'val', 'form_x', 'filed_x', 'frame_x']]
merged_df = merged_df.rename(columns={'val': 'equity', 'form_x': 'form', 'filed_x': 'filed', 'frame_x': 'frame'})
# print(merged_df)

""" Ratios """
# 1. Current ratio = Current Assets / Current Liabilities
# this ratio help us understand the company's finanical strength, how likely the company can meet its' obligations.
merged_df['current_ratio'] = merged_df['cur_assets']/ merged_df['cur_liabilities']

# 2. Debt-to-Equity Ratio (D/E) = Total liabilities / Total shareholders' Equity
# this ratio help us understand the net worth of the company by comparing the total shareholders' equity to its total liabilities
merged_df['debt_to_equity_ratio'] = merged_df['liabilities']/merged_df['equity']

# 3. Return on Equity = Net Income / Shareholder Equity (ref, https://www.investopedia.com/ask/answers/070914/how-do-you-calculate-return-equity-roe.asp)
# this ratio provides insight into the efficiently of company on managing shareholders' equity. it indicates how much money shareholders make on their investment.
merged_df['roe_ratio'] = merged_df['netincome'] / merged_df['equity']
# print(merged_asst_lib_eq_net_df)

# 4. Net Profit Margin = Net Income/Total Revenue
# this ratio measure as a percentage, of how much netincome is generated from every dollar of revenue.
merged_df['netprofitmargin_ratio'] = (merged_df['netincome'] / merged_df['revenues']) * 100

print(merged_df)

""" growth rate """
def growth_rate(col_name, df, val):
    """ Function to calculate and return growth rate"""
    df[col_name] = ((df[val].shift(-1) - df[val]) / df[val]) * 100
    return df

# Revenue (quarterly)
combined_revenues = growth_rate('rev_quarterly_growthrate', combined_revenues, 'val') 
# print(combined_revenues)    

# annual growth rate for each data point and financial ratio
merged_df = growth_rate('revenue_growthrate', merged_df, 'revenues')
merged_df = growth_rate('netincome_growthrate', merged_df, 'netincome')
merged_df = growth_rate('current_ratio_growthrate', merged_df, 'current_ratio')
merged_df = growth_rate('de_growthrate', merged_df, 'debt_to_equity_ratio')
merged_df = growth_rate('netprofitmargin_growthrate', merged_df, 'netprofitmargin_ratio')
merged_df = growth_rate('roe_growthrate', merged_df, 'roe_ratio')
print(merged_df)

""" Get filing date """
# 1. examine the relationship between stock prices and the filing dates
# get unique filing date from 10-Q
allfilings = revenue_df[['accn', 'fp','form','filed']]
allfilings = allfilings[allfilings['form'] == '10-Q']
allfilings = allfilings.drop_duplicates()

# convert to datetime
allfilings['filed'] = pd.to_datetime(allfilings['filed'])
print(allfilings)

# find the last date
last_filing_date = allfilings.iloc[-1]['filed']
print(last_filing_date)

# find the last 2 years date
three_year_filing_date = last_filing_date - pd.DateOffset(years = 5)
print(three_year_filing_date)

# filter for the last 3 years of filing date
allfilings_filtered = allfilings[(allfilings['filed'] >= three_year_filing_date) & (allfilings['filed'] <= last_filing_date)]
print(allfilings_filtered)

# convert filing dates back to str
allfilings_filtered['filed'] = allfilings_filtered['filed'].dt.strftime('%Y-%m-%d')

# print(allfilings_filtered.info())

######################################
# pull the stock market price based upon the filing date

import yfinance as yf
from datetime import datetime, timedelta

# create empty column to add stock price to the quarterly filing 
# print(allfilings_filtered)
allfilings_filtered['stock_price'] = 0
allfilings_filtered['stock_price_before'] = 0
allfilings_filtered['stock_price_after'] = 0

for index, row in allfilings_filtered.iterrows():
    value = row['filed']
    # print(value)
          
    # start date for the api call
    # get the price around the filing date
    start_date_str = value # iterate the filed date
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1) # get end date 1 day after the filed date
    end_date_str = end_date.strftime('%Y-%m-%d')

    start_date_before = datetime.strptime(value, '%Y-%m-%d') # convert filing date str to datetime
    start_date_before = start_date_before - timedelta(weeks=1) # get stock prices 1 week date before the filing date
    start_date_str_before = start_date_before.strftime('%Y-%m-%d') # convert datetime back to str
 
    # calculate the delta
    end_date_str_before = value # end date for one week before is the date of filing
    # print(start_date_before, end_date_str_after)

    # get start and end date after the filing date
    start_date_str_after = value # start date is from the date of filing
    start_date_after = datetime.strptime(start_date_str_after, '%Y-%m-%d') # convert to datetime
    
    end_date_after = start_date_after + timedelta(weeks=1) # get end date 1 day after the filed date
    end_date_str_after = end_date_after.strftime('%Y-%m-%d') # convert end date back to str to feed to yfinance
    # print(start_date_after, end_date_after)

    # create a y finance ticker object
    ticker = yf.Ticker(ticker_symbol)

    # pull yfinance historical data
    historical_data = ticker.history(period='1d', start=start_date_str, end=end_date_str)       
    historical_data_before = ticker.history(period='1d', start=start_date_str_before, end=end_date_str_before)
    historical_data_after = ticker.history(period='1d', start=start_date_str_after, end=end_date_str_after)

    # create historical dataframe
    historical_df = pd.DataFrame(historical_data)          
    historical_df_before = pd.DataFrame(historical_data_before)   
    historical_df_after = pd.DataFrame(historical_data_after)
    # print(historical_df_before, historical_df_after)
    
    # need the first row of the closing date
    specific_data = historical_data.iloc[0]['Close'] 
    specific_data_before = historical_data_before.iloc[0]['Close'] 
    specific_data_after = historical_data_after.iloc[0]['Close'] 
    # print(specific_data_before, specific_data_after)
    
    # store the specific date data in the dataframe
    allfilings_filtered.at[index,'stock_price'] = specific_data
    allfilings_filtered.at[index,'stock_price_before'] = specific_data_before
    allfilings_filtered.at[index,'stock_price_after'] = specific_data_after   

print(allfilings_filtered)

# add stock prices to the annual filing

# create empty column to add stock price to the quarterly filing 
# print(merged_df)
merged_df['stock_price'] = 0
merged_df['stock_price_before'] = 0
merged_df['stock_price_after'] = 0

for index, row in merged_df.iterrows():
    value = row['filed']
    # print(value)
          
    # start date for the api call
    # get the price around the filing date
    start_date_str = value # iterate the filed date
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = start_date + timedelta(days=1) # get end date 1 day after the filed date
    end_date_str = end_date.strftime('%Y-%m-%d')
 
    # for before and after
    start_date_before = datetime.strptime(value, '%Y-%m-%d') # convert filing date str to datetime
    start_date_before = start_date_before - timedelta(weeks=1) # get stock prices 1 week date before the filing date
    start_date_str_before = start_date_before.strftime('%Y-%m-%d') # convert datetime back to str
 
    # calculate the delta
    end_date_str_before = value # end date for one week before is the date of filing
    # print(start_date_before, end_date_str_after)

    # get start and end date after the filing date
    start_date_str_after = value # start date is from the date of filing
    start_date_after = datetime.strptime(start_date_str_after, '%Y-%m-%d') # convert to datetime
    
    end_date_after = start_date_after + timedelta(weeks=1) # get end date 1 day after the filed date
    end_date_str_after = end_date_after.strftime('%Y-%m-%d') # convert end date back to str to feed to yfinance
    # print(start_date_after, end_date_after)

    # create a y finance ticker object
    ticker = yf.Ticker(ticker_symbol)

    # pull yfinance historical data
    historical_data = ticker.history(period='1d', start=start_date_str, end=end_date_str)    
    historical_data_before = ticker.history(period='1d', start=start_date_str_before, end=end_date_str_before)
    historical_data_after = ticker.history(period='1d', start=start_date_str_after, end=end_date_str_after)

    # create historical dataframe
    historical_df = pd.DataFrame(historical_data)     
    historical_df_before = pd.DataFrame(historical_data_before)   
    historical_df_after = pd.DataFrame(historical_data_after)
    # print(historical_df_before, historical_df_after)
    
    # need the first row of the closing date   
    specific_data = historical_data.iloc[0]['Close']     
    specific_data_before = historical_data_before.iloc[0]['Close'] 
    specific_data_after = historical_data_after.iloc[0]['Close'] 
    print(specific_data, specific_data_before, specific_data_after)
    
    # store the specific date data in the dataframe
    merged_df.at[index,'stock_price'] = specific_data   
    merged_df.at[index,'stock_price_before'] = specific_data_before
    merged_df.at[index,'stock_price_after'] = specific_data_after   

print(merged_df)

# 2. examine relationship between stock price and report date

# pull all the sec recent filing data the chosen company
#SEC filling API call
companyFilling = requests.get(f'https://data.sec.gov/submissions/CIK{cik}.json', headers=headers)

print(companyFilling.json()['filings'].keys())

allFilings_recent = pd.DataFrame.from_dict(companyFilling.json()['filings']['recent'])

print(allFilings_recent[['accessionNumber', 'reportDate', 'form']])

#print all columns for allFilings dataframe
print(allFilings_recent.columns)

filtered_df = allFilings_recent[allFilings_recent['form'] == '10-K']

print(filtered_df)

filtered_df = filtered_df[['accessionNumber', 'reportDate', 'form']]

print(filtered_df)

# reset index so start with 0
filtered_df = filtered_df.reset_index()

# define the timeframe for data that we want to look at
# start_date = filtered_df['reportDate'].iloc[-1] # 2014-08-31
# end_date = filtered_df['reportDate'].iloc[0] # 2023-09-03

start_date = '2023-01-01'
end_date = '2023-12-31'
print(start_date, end_date)

filtered_df = filtered_df[(filtered_df['reportDate'] >= start_date) & (filtered_df['reportDate'] <= end_date)]
print(filtered_df)

# start the stock integration with yfinance
stock_prices_df = pd.DataFrame()

# step 1: convert reportDate to datetime
filtered_df['reportDate'] = pd.to_datetime(filtered_df['reportDate'])

# ticker_symbol is the stock symbol from the API call at the beginning of the code
# write function for getting stock price
def get_stock_price(ticker_symbol, filing_dates):

    prices = {'reportDate': [], '0_days_after': [], '30_days_after': [], '60_days_after': [], '90_days_after': [], '120_days_after': []}

    for filing_date in filing_dates:
        for days_after in [0, 30, 60, 90, 120]: 
            target_date = filing_date + timedelta(days=days_after)
            # print('for loop ', target_date, target_date.weekday() )
            # adjust for weekends
            
            if target_date.weekday() == 5:
                target_date += timedelta(days=2)
                # print('Sat ', target_date, target_date.weekday() )
            
            elif target_date.weekday() == 6:
                target_date += timedelta(days=1)
                # print('Sun ', target_date, target_date.weekday() )

            try:
                historical_data = yf.download(ticker_symbol, start=target_date.strftime('%Y-%m-%d'), end=(target_date + timedelta(days=1)).strftime('%Y-%m-%d'))
                if not historical_data.empty:
                    # print('found price')
                    price = historical_data['Close'].values[0]

                else:
                    # print('not found price', historical_data)
                    # it could be holiday so keep moving the day out 1 day until find the price
                    while historical_data.empty:
                        target_date += timedelta(days=1)
                        # print('add one more day', target_date)
                        historical_data = yf.download(ticker_symbol, start=target_date.strftime('%Y-%m-%d'), end=(target_date + timedelta(days=1)).strftime('%Y-%m-%d'))
                    price = historical_data['Close'].values[0]           
            except Exception as e:
                print(f'Error fetching data for {ticker_symbol} on {target_date}: {e}')
                price = None
                
            prices[f'{days_after}_days_after'].append(price)
        prices['reportDate'].append(filing_date)
    return pd.DataFrame(prices)
                    
stock_prices_df = get_stock_price(ticker_symbol, filtered_df['reportDate'])
print(stock_prices_df)

# melt the dataframe to turn on axis for easier graphing
melted_df = pd.melt(stock_prices_df, id_vars=['reportDate'], var_name='Days After', value_name='Stock Price' )
print(melted_df)

# convert days after to strftime in stead of date time
melted_df['Days After'] = melted_df['Days After'].astype(str) + ' days after'
print(melted_df)

""" Data visualization """
pd.options.plotting.backend = 'plotly'

def line_graph(df, title, x, y, x_label, y_label, showlabel=0):
    """ This function creates a line graph. """
    # print('create line graph') 
    # print(df)
    # print(title, x, y, x_label, y_label, callout)
    
    # check if need to add data label on the graph
    if showlabel == 1:
        plot = px.line(df,
                x=x, y=y, text=y,
                title=title,
                labels={x: x_label,
                        y: y_label})
        plot.update_traces(texttemplate='%{y}')
        plot.update_layout(yaxis_tickformat='.2f')
        
        # shift data labels to above the line
        plot.update_traces(textposition='top center')
    else:
        plot = px.line(df,
                    x=x, y=y,
                    title=title,
                    labels={x: x_label,
                            y: y_label})

    # check if need to add callouts to line graph.
    # if callout == 1:
    #     for i in range(len(df)):
    #         idx = df[y].sub(i).abs().idxmin()  # Find index of nearest value in the DataFrame
    #         plot.add_annotation(x=df[x][i], y=df[y][i],
    #                             text=f"{df[y][idx]:,.2f}",
    #                             # text=f"{df[y][i]:,.2f}",
    #                             showarrow=True,
    #                             arrowhead=1,
    #                             ax=0,
    #                             ay=-30)
    return plot

# Revenues
rev_plot = line_graph(combined_revenues,'COST Revenues Between FY2013-2023','end', 'val', 'Date', 'Value in $', 0) # too crowded, need to adjust data label format if want to show data label.
plotly.offline.plot(rev_plot)

# create bar chart with trend line
# Calculate trend line
x = np.arange(len(combined_revenues['end']))
slope, intercept, _, _, _ = linregress(x, combined_revenues['val'])
trend_line = slope * x + intercept

# Create bar plot
rev_bar_trend_plot = px.bar(combined_revenues, 
                      x='end', y='val',
                      title='COST Revenues Between FY2013-2023',
                      labels={'end': 'Date',
                              'val': 'Value in $'})

# add trend line
rev_bar_trend_plot.add_scatter(x=combined_revenues['end'], 
                         y=trend_line, 
                         mode='lines',
                         name='trend Line')

plotly.offline.plot(rev_bar_trend_plot)

# Assets and liabilities line chart
asst_li_plot = px.line(merged_df,
                           x='end', y=['assets', 'liabilities'],
                           title='COST Total Assets & Total Liabilities')

# Update layout to set x-axis and y-axis title
asst_li_plot.update_layout(yaxis_title="Value in $")
asst_li_plot.update_layout(xaxis_title="Date")
plotly.offline.plot(asst_li_plot)

# Current assets and current liabilities line chart
cur_asst_li_plot = px.line(merged_df,
                           x='end', y=['cur_assets', 'cur_liabilities'],
                           title='COST Current Assets & Current Liabilities')

# Update layout to set x-axis and y-axis title
cur_asst_li_plot.update_layout(yaxis_title="Value in $")
cur_asst_li_plot.update_layout(xaxis_title="Date")
plotly.offline.plot(cur_asst_li_plot)

# Net Income
netincome_plot = line_graph(merged_df, 'COST Net Income Between FY2013-2023', 'end', 'netincome', 'Date', 'Value in $')
plotly.offline.plot(netincome_plot)

# create equity chart
equity_plot = line_graph(merged_df, 'COST Stockholder Equity Between FY2013-2023', 'end', 'equity', 'Date', 'Value in $')
plotly.offline.plot(equity_plot)

# function to create combo chart displaying data points and ratio
def create_combo_chart(df, ybar1, name1, ybar2, name2, y2line, y2name, title):

    # Create a bar chart for Current assets and Current liabilities
    bar_chart = go.Figure()
    bar_chart.add_trace(go.Bar(x=df['end'], y=df[ybar1], name=name1))
    bar_chart.add_trace(go.Bar(x=df['end'], y=df[ybar2], name=name2))

    # # Create a line chart for current ratio
    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(x=df['end'], y=df[y2line], mode='lines', name=y2name, yaxis='y2'))

    # # Create a combo graph by combining bar and line charts
    combo_chart = go.Figure()

    # # Add bar chart traces to combo chart
    for trace in bar_chart.data:
        combo_chart.add_trace(trace)

    # # Add line chart trace to combo chart
    for trace in line_chart.data:
        combo_chart.add_trace(trace)

    # # Update layout for better visualization
    combo_chart.update_layout(
        barmode='group',
        title=title,
        yaxis=dict(title='Value in $'),
        yaxis2=dict(title='Ratio', overlaying='y', side='right')
    )
    # # Show the graph
    return plotly.offline.plot(combo_chart)

# create a combo chart to show Current Assets, Current Liabilities, and Current Ratio
current_ratio_plot = create_combo_chart(merged_df, 
                                        'cur_assets', 'Current Assets', 
                                        'cur_liabilities', 'Current Liabilities', 
                                        'current_ratio', 'Current Ratio', 
                                        'Combo Graph: Current Assets, Current Liabilities, and Current Ratio')

# Create a combo chart for D/E ratio
de_ratio_plot = create_combo_chart(merged_df,
                                   'liabilities', 'Total Liabilities', 
                                   'equity', 'Stockholder Equity', 
                                   'debt_to_equity_ratio', 'D/E Ratio', 
                                   'Combo Graph: Total Liabilities, Stockholder Equity, and Debt to Equity (D/E) Ratio')

# Profit margin ratio chart
netprofitmargin_plot = line_graph(merged_df, 'COST Net Profit Margin Ratio between FY2013-2023', 'end', 'netprofitmargin_ratio', 'Date', 'Value (%)')
plotly.offline.plot(netprofitmargin_plot)

# Return on Equity
roe_plot = line_graph(merged_df, 'Costco (COST) Return on Equity Between FY2013-2023', 'end', 'roe_ratio', 'Date', 'Value in $')
plotly.offline.plot(roe_plot)

# create combo chart for ROE ratio
roe_combo_plot = create_combo_chart(merged_df, 
                                    'netincome', 'Net Income',
                                    'equity', 'Stockholder Equity',
                                    'roe_ratio', 'ROE Ratio',
                                    'Combo Graph: Net Income, Shareholder Equity, and Return on Equity')

# Filings date vs stock price
# print(allfilings_filtered)
stock_plot = line_graph(allfilings_filtered,'Stock Price vs Filing Date for Costco (COST)', 'filed', 'stock_price', 'Filing Date', 'Stock Price ($)',1)
plotly.offline.plot(stock_plot)

# stock price vs filing date
# assign report_date to show on the graph title 
report_date = filtered_df['reportDate'].dt.strftime('%Y-%m-%d').values
print(report_date)

fig = px.line(melted_df, x='Days After', y= 'Stock Price',
              text='Stock Price',
              title = f'Stock Price Evolution After Filing Dates {report_date} {ticker_symbol} : {start_date} <-> {end_date}',
              labels={'Days After': 'Period After Filing', 'reportDate': 'Report Date', 'Stock Price': 'Stock Price ($)'})

fig.update_traces(texttemplate='$ %{y}', 
                  textposition='top left')

fig.update_layout(
        xaxis_title='Report Date',
        yaxis_title='Stock Price ($)',
        legend_title='Time After Filing')

plotly.offline.plot(fig)

# correlation
heatmap_df = merged_df[['revenues', 'netincome', 'equity','current_ratio', 'debt_to_equity_ratio', 'roe_ratio', 'netprofitmargin_ratio','stock_price_after']]
corr = heatmap_df.corr()

plt.figure(figsize=(8,6))
sns.heatmap(corr, annot=True, cmap='inferno')
plt.title('Correlation Heatmap')
plt.show()

print('End of Code. Thank you!')

