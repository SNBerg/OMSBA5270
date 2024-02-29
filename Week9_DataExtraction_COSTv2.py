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
import plotly.express as px
import plotly.graph_objects as go # for combo chart

# if using Spyder
import plotly.io as pio
pio.renderers.default='browser'
#pio.renderers.default = "svg"

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
print(cik) # 0000789019
# print(companyCIK[companyCIK['cik_str']==cik])

""" 
Data retrieval and EDA 

Source: data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:
https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
"""

companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
# print(companyFacts.json().keys())
# print(companyFacts.json()['facts'])

""" Functions to get data in each key """
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
    print(df.count(), min(df['end']), max(df['end']))

    return(df, df_filtered)

# get revenues data
"""
RevenueFromContractWithCustomerExcludingAssessedTax
Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer.
Tax collected from customer is tax assessed by governmental authority that is both imposed on and concurrent with specific revenue-producing transaction, 
including, but not limited to, sales, use, value added and excise.
"""
revenue_df, revenue_df_filtered = getdata('Revenues', '10-K')
# observation: no null data, 288 rows start date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# has start and end date, has quarterly and annual data presented
# has NaN in frame column - need to clean up
# end date is object type

# quarterly data missing Q4 of FY21-22-23
# additional revenue data to get quarterly data for using in stock price analysis
revenue2k_df, revenue2k_df_filtered = getdata('RevenueFromContractWithCustomerExcludingAssessedTax', '10-K')
# additional data to get quarterly data from 8/31/2020
revenue2q_df, revenue2q_df_filtered = getdata('RevenueFromContractWithCustomerExcludingAssessedTax', '10-Q')
# print(revenue_df_filtered,revenue2_df_filtered)

# get Assets and convert the facts on assets to a dataframe
"""
Assets 
Sum of the carrying amounts as of the balance sheet date of all assets that are recognized. 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
assets_df, assets_df_filtered = getdata('Assets', '10-K')
# observation: no null data, 158 rows end date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end date - need to clean up
# end date is object type

# get current assets
"""
AssetsCurrent
Sum of the carrying amounts as of the balance sheet date of all assets that are expected to be realized in cash, sold, or consumed within one year (or the normal operating cycle, if longer). 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
cur_assets_df, cur_assets_df_filtered = getdata('AssetsCurrent', '10-K')
# observation: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
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
# observation: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# get current liabilities
"""
LiabilitiesCurrent
Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
"""
cur_liabilities_df, cur_libilities_df_filtered = getdata('LiabilitiesCurrent', '10-K') 
# observation: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
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
# observation: no null data, 114 rows end date between 2009-08-30 - 2023-11-26 - need to align period with other data points
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

# get net income
"""
NetIncomeLossLoss
The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
"""
netincome_df, netincome_df_filtered = getdata('NetIncomeLoss', '10-K') 
# observation: no null data, 272 rows end date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# has start and end date, has quarterly and annual data presented
# fp values are all FY, has NaN in frame column, has duplicated end dates - need to dedup and clean up
# end date is object type

"""
Data cleaning and wrangling - cleanup duplicated row and prepare data for the next step
"""
""" Function to filter for specific year data set """

def cleanup(df, year):
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

# get quarterly revenues report for using in Stock price analysis
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
print(rev)

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

# create a new column to 
revenue2k_df_annual['val_q'] = revenue2k_df_annual['val'] - revenue2k_df_annual['start'].map(rev) 

# add the missing quarterly start date to the dataframe
start_q = ['5/10/2021', '5/9/2022', '5/8/2023']
start_q_date = pd.to_datetime(start_q)
revenue2k_df_annual['start_q'] = start_q_date

revenue2k_df_missing = revenue2k_df_annual.copy()
revenue2k_df_missing = revenue2k_df_missing[['start_q', 'end', 'val_q', 'accn', 'fy', 'fp', 'form', 'filed', 'frame']]
revenue2k_df_missing = revenue2k_df_missing.rename(columns={'val_q': 'val', 'start_q': 'start'})
print(revenue2k_df_missing)

# add missing quarter
combined_revenues = pd.concat([combined_revenues, revenue2k_df_missing], ignore_index=True)
combined_revenues = combined_revenues.sort_values(by=['end'])
combined_revenues = combined_revenues.reset_index(drop=True)
print(combined_revenues)

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
print(merged_df.columns)

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

# 3. Net Profit Margin = Net Income/Total Revenue
# this ratio measure as a percentage, of how much netincome is generated from every dollar of revenue.
merged_df['netprofitmargin_ratio'] = (merged_df['netincome'] / merged_df['revenues']) * 100
# print(merged_df)

""" Data visualization """



# create a combo chart to show Assets, Liabilities, and Current Ratio

# Create a bar chart for assets and liabilities
# bar_chart = go.Figure()
# bar_chart.add_trace(go.Bar(x=merged_cur_asst_lib_df_filtered['end'], y=merged_cur_asst_lib_df_filtered['current_assets'], name='Current Assets'))
# bar_chart.add_trace(go.Bar(x=merged_cur_asst_lib_df_filtered['end'], y=merged_cur_asst_lib_df_filtered['current_liabilities'], name='Current Liabilities'))

# # Create a line chart for current ratio
# line_chart = go.Figure()
# line_chart.add_trace(go.Scatter(x=merged_cur_asst_lib_df_filtered['end'], y=merged_cur_asst_lib_df_filtered['current_ratio'], mode='lines', name='Current Ratio', yaxis='y2'))

# # Create a combo graph by combining bar and line charts
# combo_chart = go.Figure()

# # Add bar chart traces to combo chart
# for trace in bar_chart.data:
#     combo_chart.add_trace(trace)

# # Add line chart trace to combo chart
# for trace in line_chart.data:
#     combo_chart.add_trace(trace)

# # Update layout for better visualization
# combo_chart.update_layout(
#     barmode='group',
#     title='Combo Graph: Current Assets, Current Liabilities, and Current Ratio',
#     yaxis=dict(title='Current Assets and Current Liabilities'),
#     yaxis2=dict(title='Current Ratio', overlaying='y', side='right')
# )

# # Show the graph
# combo_chart.show()

