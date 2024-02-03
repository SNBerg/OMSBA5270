"""
Class: OMSBA 5270 01 24 WQ
Author: Sirina Berg
Source : https://www.sec.gov/edgar/sec-api-documentation
Midterm DTC - comprehensive analysis using the EDGAR database to provide insights into which companies to allocate $1 million for further analysis.

Project Objectives
- Utilize the EDGAR API to retrieve financial data of publicly traded companies.
- Calculate and analyze key financial ratios for the selected companies.
- Interpret the results to gain insights into the financial health and performance of these companies.
- Present your findings through code and a comprehensive report with visuals.
"""

# import libraries
import requests
import pandas as pd
import plotly.express as px
from tabulate import tabulate # to create ratio tables
import plotly.graph_objects as go # for combo chart

# setup display so it shows all columns
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

pd.options.plotting.backend = 'plotly'

# set number float format
pd.options.display.float_format = '{:.2f}'.format

# function to get cik_str for the selected company
def search_comp(ticker):
    return(companyCIK.loc[companyCIK['ticker'] == ticker, 'cik_str'].iloc[0])

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
First company = Apple Inc. (AAPL)
Apple Inc. (formerly Apple Computer, Inc.) is an American multinational technology company headquartered in Cupertino, California, in Silicon Valley. 
It designs, develops, and sells consumer electronics, computer software, and online services. Devices include the iPhone, iPad, Mac, Apple Watch, and 
Apple TV; operating systems include iOS and macOS; and software applications and services include iTunes, iCloud, and Apple Music.

As of March 2023, Apple is the world's largest company by market capitalization.[6] In 2022, it was the largest technology company by revenue, 
with US$394.3 billion.[7] As of June 2022, Apple was the fourth-largest personal computer vendor by unit sales, the largest manufacturing company 
by revenue, and the second-largest manufacturer of mobile phones in the world. It is one of the Big Five American information technology companies, 
alongside Alphabet (the parent company of Google), Amazon, Meta (the parent company of Facebook), and Microsoft.
"""
cik = search_comp('AAPL')  # call function search_comp to get cik_str
# print(companyCIK[companyCIK['cik_str'] == cik])

""" Data retrieval and EDA """
"""
Source: data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:

https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
"""

companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
# print(companyFacts.json()['facts']['us-gaap']['SalesRevenueNet']['units'])

# get revenues data
"""
RevenueFromContractWithCustomerExcludingAssessedTax
Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer.
Tax collected from customer is tax assessed by governmental authority that is both imposed on and concurrent with specific revenue-producing transaction, 
including, but not limited to, sales, use, value added and excise.
"""

revenue_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD'])
revenue_df = revenue_df.sort_values(by=['start'])
# check data structure
print(revenue_df.info())
# no null data
# print(revenue_df) # 81 rows start date between 2017-09-30 - 2023-07-01
# observation: has data both in annual and quarterly, has multiple forms, NaN in frame column

# get Assets and convert the facts on assets to a dataframe
"""
Assets 
Sum of the carrying amounts as of the balance sheet date of all assets that are recognized. 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
assets_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Assets']['units']['USD'])
print(assets_df) # 124 rows end 2008-09-27-2023-09-30
print(assets_df.info())
# observed multiple filing for the same perious of data, for example 2011-09-24 10-K has 2 filing on 2011-10-26 and 2012-10-31
# print(assets_df.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(assets_df['form'].unique()) # has multiple form ['10-K' '10-Q' '8-K']

# observation: there are NaN in the dataset.
# There could be more than one data filed at the same time. For example 2009-10-27 has two end years – 2008-09-27 and 2009-09-26.
# there could be data that filed multiple times and the val could be the same or different.

# get current assets
"""
AssetsCurrent
Sum of the carrying amounts as of the balance sheet date of all assets that are expected to be realized in cash, sold, or consumed within one year (or the normal operating cycle, if longer). 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
cur_assets_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['AssetsCurrent']['units']['USD'])
print(cur_assets_df) # 122 rows end 2008-09-27-2023-09-30
print(cur_assets_df.info()) # non-null
# print(cur_assets_df['form'].unique()) #['10-Q' '10-K' '10-K/A' '8-K']
# print(cur_assets_df.columns) #Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')

# observation: frame column contains NaN

# get liabilities data and convert the facts on assets to a dataframe
"""
Liabilities
Sum of the carrying amounts as of the balance sheet date of all liabilities that are recognized. 
Liabilities are probable future sacrifices of economic benefits arising from present obligations of an entity to transfer assets 
or provide services to other entities in the future.
"""
liabilities_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Liabilities']['units']['USD'])
# liabilities_df = liabilities_df.sort_values(by='filed')
print(liabilities_df) # 122 rows end 2008-09-27-2023-09-30
print(liabilities_df.info())
# print(liabilities_df.columns) #Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(liabilities_df['form'].unique()) # ['10-Q' '10-K/A' '10-K' '8-K']

# get current liabilities
"""
LiabilitiesCurrent
Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
"""
cur_liabilities_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['LiabilitiesCurrent']['units']['USD'])
# cur_liabilities_df = cur_liabilities_df.sort_values(by='filed')
print(cur_liabilities_df) # 122 rows end 2008-09-27-2023-09-30
print(cur_liabilities_df.info())
# print(cur_liabilities_df.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(cur_liabilities_df['form'].unique()) # has multiple form ['10-K/A' '10-Q' '10-K' '8-K']

# observation, same as AssetsCurrent, there are multiple period, calendar year and quarterly. Different period of data can be filed at the same time.

# get stockholders' equity
"""
StockholdersEquity
Total of all stockholders' equity (deficit) items, net of receivables from officers, directors, owners, and affiliates of the entity which are attributable to the parent.
The amount of the economic entity's stockholders' equity attributable to the parent excludes the amount of stockholders' equity 
which is allocable to that ownership interest in subsidiary equity which is not attributable to the parent (noncontrolling interest, minority interest). 
This excludes temporary equity and is sometimes called permanent equity.
"""
equity_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['StockholdersEquity']['units']['USD'])
print(equity_df) # 208 rows end 2006-09-30-2023-09-30
print(equity_df.info())
# print(equity_df.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(equity_df['form'].unique()) # has multiple form ['10-K/A' '10-Q' '10-K' '8-K']

# observation, same as AssetsCurrent, there are multiple period, calendar year and quarterly. Different period of data can be filed at the same time.

print(companyFacts.json()['facts']['us-gaap'].keys())
# get net income
"""
NetIncomeLossLoss
The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
"""
netincome_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['NetIncomeLoss']['units']['USD'])
print(netincome_df) # 302 rows end 2007-09-29-2023-09-30
print(netincome_df.info())
# print(netincome_df.columns) # Index(['start', 'end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(netincome_df['form'].unique()) # has multiple form ['10-K' '10-K/A' '10-Q' '8-K']

"""
Data cleaning and wrangling - cleanup duplicated row and prepare data for the next step
"""
# filter for 10-K
revenue_df_filtered = revenue_df[revenue_df['form'] == '10-K']
# print(revenue_df_filtered)
# print(revenue_df_filtered.count()) # 91 rows 2007-09-29 - 2017-09-30

# sort data by end and filed dates
revenue_df_filtered = revenue_df_filtered.sort_values(by=['end', 'filed'])

# remove quarterly data # 45 rows
# revenue_df_filtered = revenue_df_filtered[~revenue_df_filtered['frame'].str.contains('Q', na=False)]
revenue_df_filtered['start'] = pd.to_datetime(revenue_df_filtered['start'])
revenue_df_filtered['end'] = pd.to_datetime(revenue_df_filtered['end'])
revenue_df_filtered['months_diff'] = ((revenue_df_filtered['end'] - revenue_df_filtered['start']) / pd.Timedelta(days=30)).astype(int)
revenue_df_filtered = revenue_df_filtered[revenue_df_filtered['months_diff'] >= 12] # there are the same record that filed multiple times, need to drop duplicated
revenue_df_filtered = revenue_df_filtered.drop(columns=['months_diff'])

# remove duplicated rows of the same period and keep the row with the last filed.
revenue_df_filtered = revenue_df_filtered.drop_duplicates(subset=['end'], keep='last')
# print(revenue_df_filtered) # 11 rows, 2017-09-30 - 2023-09-30

# drop start as we no longer need this
revenue_df_filtered = revenue_df_filtered.drop(columns='start')
# print(revenue_df_filtered)

# filter for 10-K form only
assets_df_filtered = assets_df[assets_df['form'] == '10-K']
# print(assets_df_filtered)
# print(assets_df_filtered.count()) # 14 rows
# print(assets_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
assets_df_filtered = assets_df_filtered.sort_values(by=['end', 'filed'])
# assets_df_filtered['filed'] = pd.to_datetime(assets_df_filtered['filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
assets_df_filtered = assets_df_filtered.drop_duplicates(subset=['end'], keep='last')
# print(assets_df_filtered) # 16 rows end 2008-09-27-2023-09-30

cur_assets_df_filtered = cur_assets_df[cur_assets_df['form'] == '10-K']
# print(assets_df_filtered)
# print(assets_df_filtered.count()) # 14 rows
# print(assets_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
cur_assets_df_filtered = cur_assets_df_filtered.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
cur_assets_df_filtered = cur_assets_df_filtered.drop_duplicates(subset=['end'], keep='last')
# print(cur_assets_df_filtered) # 16 rows end 2008-09-27-2023-09-30

liabilities_df_filtered = liabilities_df[liabilities_df['form'] == '10-K']
# print(liabilities_df_filtered)
# print(liabilities_df_filtered.count()) # 13 rows
# print(liabilities_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
liabilities_df_filtered = liabilities_df_filtered.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
liabilities_df_filtered = liabilities_df_filtered.drop_duplicates(subset=['end'], keep='last')
# print(liabilities_df_filtered) # 16 rows end 2008-09-27-2023-09-30

cur_liabilities_df_filtered = cur_liabilities_df[cur_liabilities_df['form'] == '10-K']
# print(cur_liabilities_df_filtered)
# print(cur_liabilities_df_filtered.count()) # 13 rows
# print(cur_liabilities_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
cur_liabilities_df_filtered = cur_liabilities_df_filtered.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
cur_liabilities_df_filtered = cur_liabilities_df_filtered.drop_duplicates(subset=['end'], keep='last')
# print(cur_liabilities_df_filtered) # 16 rows end 2008-09-27-2023-09-30

equity_df_filtered = equity_df[equity_df['form'] == '10-K']
# print(equity_df_filtered)
# print(equity_df_filtered.count()) # 15 rows
# print(equity_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
equity_df_filtered = equity_df_filtered.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
equity_df_filtered = equity_df_filtered.drop_duplicates(subset=['end'], keep='last')
# print(equity_df_filtered) # 18 rows end 2006-09-30-2023-09-30

# filter for 10-K
netincome_df_filtered = netincome_df[netincome_df['form'] == '10-K']
# print(netincome_df_filtered)
# print(netincome_df_filtered.count()) # 133 rows 2007-09-29 - 2023-09-30
# print(netincome_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
netincome_df_filtered = netincome_df_filtered.sort_values(by=['end', 'filed'])

# remove quarterly data # 45 rows
netincome_df_filtered = netincome_df_filtered[~netincome_df_filtered['frame'].str.contains('Q', na=False)]
netincome_df_filtered['start'] = pd.to_datetime(netincome_df_filtered['start'])
netincome_df_filtered['end'] = pd.to_datetime(netincome_df_filtered['end'])
netincome_df_filtered['months_diff'] = ((netincome_df_filtered['end'] - netincome_df_filtered['start']) / pd.Timedelta(days=30)).astype(int)
netincome_df_filtered = netincome_df_filtered[netincome_df_filtered['months_diff'] >= 12] # 17 rows end date 2007-09-29-2023-09-30
netincome_df_filtered = netincome_df_filtered.drop(columns=['months_diff'])

# remove duplicated rows of the same period and keep the row with the last filed.
netincome_df_filtered = netincome_df_filtered.drop_duplicates(subset=['end'], keep='last')

# drop start date, we only need end date
netincome_df_filtered = netincome_df_filtered.drop(columns='start')
# print(netincome_df_filtered) # 17 rows end 2007-09-29-2023-09-30
# there are quarterly data in this dataset, For example CY2008Q4.
# frame column has NaN

""" Summary and graph"""
desc_rev = revenue_df_filtered.describe()
print(desc_rev['val'])
# mean 92,615,221,311.475
# min  30,006,000,000.000
# max  163,231,000,000.000

# create visual
rev_plot = px.line(revenue_df_filtered,
                  title='AAPL Revenues',
                  x='end',
                  y='val')
rev_plot.show()

desc_assets = assets_df_filtered.describe()
print(desc_assets['val'])
# mean 247,621,750,000.00
# min  36,171,000,000.00
# max  375,319,000,000.00

# what is the assets trend?
assets_plot = px.line(assets_df_filtered,
                      title=f"AAPL Assets",
                      x="end",
                      y="val")
assets_plot.show()

desc_cur_assets = cur_assets_df.describe()
print(desc_cur_assets)
# mean 92,615,221,311.00
# min  30,006,000,000.00
# max  163,231,000,000.00

cur_assets_plot = px.line(cur_assets_df_filtered,
                      title=f"AAPL Current Assets",
                      x="end",
                      y="val")
cur_assets_plot.show()

desc_liabilities = liabilities_df_filtered.describe()
print(desc_liabilities['val'])
# mean 163,402,125,000.00
# min  15,861,000,000.00
# max  302,083,000,000.00

# what is the liabilities trend look like?
liabilities_plot = px.line(liabilities_df_filtered,
                      title=f"AAPL Liabilities",
                      x="end",
                      y="val")
liabilities_plot.show()

desc_cur_liabilities = cur_liabilities_df.describe()
print(desc_cur_liabilities)
# mean 72,966,442,623.00
# min  11,361,000,000.00
# max  153,982,000,000.00

cur_liabilities_plot = px.line(cur_liabilities_df_filtered,
                      title=f"AAPL Current Liabilities",
                      x="end",
                      y="val")
cur_liabilities_plot.show()

desc_equity = equity_df.describe()
print(desc_equity)
# mean 87,437,461,538.00
# min  9,984,000,000.00
# max  140,199,000,000.00

equity_plot = px.line(equity_df_filtered,
                      title=f"AAPL Stockholder Equity",
                      x="end",
                      y="val")
equity_plot.show()

desc_netincome = netincome_df_filtered.describe()
print(desc_netincome['val'])
# mean 46304294117.647
# min  3496000000.000
# max  99,803,000,000.000

# what is the netincome trend?
netincome_plot = px.line(netincome_df_filtered,
                      title=f"APPL Net Income & Loss",
                      x="end",
                      y="val")
netincome_plot.show()

# merge total assets and total liabilities using end column for calculate current ratio
merged_asst_lib_df = pd.merge(assets_df_filtered, liabilities_df_filtered, on=['end'], how='inner')
merged_asst_lib_df = merged_asst_lib_df.drop(merged_asst_lib_df.columns[9:], axis=1)
# print(merged_asst_lib_df) # 16 rows
# print(merged_asst_lib_df.columns)
# return Index(['end_x', 'val_x', 'accn', 'fy_x', 'fp_x', 'form_x', 'filed_x',
#        'frame_x', 'end_y', 'val_y'], dtype='object')

merged_asst_lib_df = merged_asst_lib_df.rename(columns={'val_x': 'assets', 'val_y': 'liabilities'})
print(merged_asst_lib_df)

# get summaries of merged dataframe
desc_merged_asst_lib_df = merged_asst_lib_df.describe()
print(desc_merged_asst_lib_df[['assets', 'liabilities']])

# what is the liabilities trend?
merged_plot1 = px.line(merged_asst_lib_df,
                      x='end', y=['assets', 'liabilities'],
                      title="AAPL Assets & Liabilities")
merged_plot1.update_layout(yaxis_title="Value in $")
merged_plot1.update_layout(xaxis_title="Date")

merged_plot1.show()

# merge total assets and total liability with shareholders' equity to calculate D/E ratio
# filed date for the same period appears to be different from each other so using end date to join the two data
merged_asst_lib_eq_df = pd.merge(merged_asst_lib_df, equity_df_filtered, on='end')
merged_asst_lib_eq_df = merged_asst_lib_eq_df.drop(merged_asst_lib_eq_df.columns[10:], axis=1)
merged_asst_lib_eq_df = merged_asst_lib_eq_df.rename(columns={'val': 'equity'})
print(merged_asst_lib_eq_df) # 16 rows
# print(merged_asst_lib_eq_df.columns)

desc_merged_asst_lib_eq_df = merged_asst_lib_eq_df.describe()
print(desc_merged_asst_lib_eq_df[['liabilities', 'equity']])

# what is the liabilities trend?
merged_plot2 = px.line(merged_asst_lib_eq_df,
                      x='end', y=['liabilities', 'equity'],
                      title="AAPL Total Liabilities & Shareholders' Equity")
merged_plot2.update_layout(yaxis_title="Value in $")
merged_plot2.update_layout(xaxis_title="Date")
merged_plot2.show()

# merge net income for calculate ROE
# filed date can be different for the same period so join using end date instead of accn
# update the end date type to datetime to join the data
merged_asst_lib_eq_df['end'] = pd.to_datetime(merged_asst_lib_eq_df['end'])

# merge data
merged_asst_lib_eq_net_df = pd.merge(merged_asst_lib_eq_df, netincome_df_filtered, on='end')
merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.drop(merged_asst_lib_eq_net_df.columns[11:], axis=1)
merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.rename(columns={'val': 'netincome'})
print(merged_asst_lib_eq_net_df) # 16 rows
# print(merged_asst_lib_eq_net_df.columns)

desc_merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.describe()
print(desc_merged_asst_lib_eq_net_df[['netincome', 'equity']])

# what is the liabilities trend?
merged_plot3 = px.line(merged_asst_lib_eq_net_df,
                      x='end', y=['netincome', 'equity'],
                      title="APPL Net Income & Shareholders' Equity")

# Update layout to set x-axis and y-axis title
merged_plot3.update_layout(yaxis_title="Value in $")
merged_plot3.update_layout(xaxis_title="Date")

# Show the plot
merged_plot3.show()

# merge sales revenue data
# print(merged_asst_lib_eq_net_df['end'], revenue_df_filtered['end'])
# end date aligned between files so join with end date
merged_asst_lib_eq_net_rev_df = pd.merge(merged_asst_lib_eq_net_df, revenue_df_filtered, on='end')
merged_asst_lib_eq_net_rev_df = merged_asst_lib_eq_net_rev_df.drop(merged_asst_lib_eq_net_rev_df.columns[12:], axis=1)
merged_asst_lib_eq_net_rev_df = merged_asst_lib_eq_net_rev_df.rename(columns={'val': 'revenue'})
print(merged_asst_lib_eq_net_rev_df) # 7 rows
# print(merged_asst_lib_eq_net_rev_df.columns)

desc_merged_asst_lib_eq_net_rev_df = merged_asst_lib_eq_net_rev_df.describe()
print(desc_merged_asst_lib_eq_net_rev_df[['netincome', 'revenue']])

# what is the liabilities trend?
merged_plot4 = px.line(merged_asst_lib_eq_net_rev_df,
                      x='end', y=['netincome', 'revenue'],
                      title="APPL Net Income & Total Revenue")

# Update layout to set x-axis and y-axis title
merged_plot4.update_layout(yaxis_title="Value in $")
merged_plot4.update_layout(xaxis_title="Date")

# Show the plot
merged_plot4.show()

# merge current assets and current liabilities
merged_cur_asst_lib_df = pd.merge(cur_assets_df_filtered, cur_liabilities_df_filtered, on=['accn', 'end'], how='inner')
merged_cur_asst_lib_df = merged_cur_asst_lib_df.drop(merged_cur_asst_lib_df.columns[9:], axis=1)
merged_cur_asst_lib_df = merged_cur_asst_lib_df.rename(columns={'val_x': 'current_assets', 'val_y': 'current_liabilities'})
print(merged_cur_asst_lib_df) # 16 rows end 2008-09-27 to 2023-09-30
# print(merged_cur_asst_lib_df.columns)

# get summaries of merged dataframe
desc_merged_cur_asst_lib_df = merged_cur_asst_lib_df.describe()
print(desc_merged_cur_asst_lib_df[['current_assets', 'current_liabilities']])

# what is the liabilities trend?
merged_plot5 = px.line(merged_cur_asst_lib_df,
                      x='end', y=['current_assets', 'current_liabilities'],
                      title="AAPL Current Assets & Current Liabilities")

# Update layout to set x-axis and y-axis title
merged_plot5.update_layout(yaxis_title="Value in $")
merged_plot5.update_layout(xaxis_title="Date")

# Show the plot
merged_plot5.show()

""" Ratios """
# 1. Current ratio = Current Assets / Current Liabilities
# this ratio help us understand the company's finanical strength, how likely the company can meet its' obligations.

merged_cur_asst_lib_df['current_ratio'] = merged_cur_asst_lib_df['current_assets']/ merged_cur_asst_lib_df['current_liabilities']
# print(merged_cur_asst_lib_df)

# normalized to based year
merged_cur_asst_lib_df['end'] = pd.to_datetime(merged_cur_asst_lib_df['end'])
merged_cur_asst_lib_df_filtered = merged_cur_asst_lib_df.loc[merged_cur_asst_lib_df['end'] > '2016-01-01']
# print(merged_cur_asst_lib_df_filtered)

current_ratio_plot = px.line(merged_cur_asst_lib_df_filtered,
                      x='end', y='current_ratio',
                      title="AAPL Current Ratio")
current_ratio_plot.update_yaxes(range=[0, max(merged_cur_asst_lib_df_filtered['current_ratio']+1)])

# Update layout to set x-axis and y-axis title
current_ratio_plot.update_layout(yaxis_title="Ratio")
current_ratio_plot.update_layout(xaxis_title="Date")

current_ratio_plot.show()

# check growth rate
merged_cur_asst_lib_df_filtered['currentratio_growthrate'] = ((merged_cur_asst_lib_df_filtered['current_ratio'].shift(-1) - merged_cur_asst_lib_df_filtered['current_ratio']) / merged_cur_asst_lib_df_filtered['current_ratio']) * 100
print(merged_cur_asst_lib_df_filtered[['end', 'current_ratio', 'currentratio_growthrate']])

# 2. Debt-to-Equity Ratio (D/E) = Total liabilities / Total shareholders' Equity
# this ratio help us understand the net worth of the company by comparing the total shareholders' equity to its total liabilities

merged_asst_lib_eq_df['debt_to_equity_ratio'] = merged_asst_lib_eq_df['liabilities']/merged_asst_lib_eq_df['equity']
print(merged_asst_lib_eq_df)

# normalized to based year
merged_asst_lib_eq_df['end'] = pd.to_datetime(merged_asst_lib_eq_df['end'])
merged_asst_lib_eq_df_filtered = merged_asst_lib_eq_df.loc[merged_asst_lib_eq_df['end'] > '2016-01-01']
# print(merged_asst_lib_eq_df_filtered)

debt_to_equity_ratio_plot = px.line(merged_asst_lib_eq_df_filtered,
                      x='end', y='debt_to_equity_ratio',
                      title="AAPL Debt-to-Equity Ratio",
                                    labels={
                                        "debt_to_equity_ratio": "Debt-to-Equity Ratio",
                                        "end": "Date"
                                    })
debt_to_equity_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_df_filtered['debt_to_equity_ratio'])])

debt_to_equity_ratio_plot.show()

# check growth rate
merged_asst_lib_eq_df_filtered['DE_growthrate'] = ((merged_asst_lib_eq_df_filtered['debt_to_equity_ratio'].shift(-1) - merged_asst_lib_eq_df_filtered['debt_to_equity_ratio']) / merged_asst_lib_eq_df_filtered['debt_to_equity_ratio']) * 100
print(merged_asst_lib_eq_df_filtered[['end', 'debt_to_equity_ratio','DE_growthrate']])

# 3. Return on Equity = Net Income / Shareholder Equity (ref, https://www.investopedia.com/ask/answers/070914/how-do-you-calculate-return-equity-roe.asp)
# this ratio provides insight into the efficiently of company on managing shareholders' equity. it indicates how much money shareholders make on their investment.

merged_asst_lib_eq_net_df['roe_ratio'] = merged_asst_lib_eq_net_df['netincome'] / merged_asst_lib_eq_net_df['equity']
# print(merged_asst_lib_eq_net_df)

# normalized to based year
merged_asst_lib_eq_net_df['end'] = pd.to_datetime(merged_asst_lib_eq_net_df['end'])
merged_asst_lib_eq_net_df_filtered = merged_asst_lib_eq_net_df.loc[merged_asst_lib_eq_net_df['end'] > '2016-01-01']
# print(merged_asst_lib_eq_net_df_filtered)

roe_ratio_plot = px.line(merged_asst_lib_eq_net_df_filtered,
                      x='end', y='roe_ratio',
                      title="AAPL Return on Equity Ratio",
                                    labels={
                                        'roe_ratio': "Return on Equity Ratio",
                                        "end": "Date"
                                    })
roe_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_net_df_filtered['roe_ratio'])])

# Update y-axis interval to align with the first company
roe_ratio_plot.update_layout(yaxis=dict(dtick=0.05, range=[0, 2]))

roe_ratio_plot.show()

# check growth rate
merged_asst_lib_eq_net_df_filtered['roe_growthrate'] = ((merged_asst_lib_eq_net_df_filtered['roe_ratio'].shift(-1) - merged_asst_lib_eq_net_df_filtered['roe_ratio']) / merged_asst_lib_eq_net_df_filtered['roe_ratio']) * 100
print(merged_asst_lib_eq_net_df_filtered[['end', 'roe_ratio','roe_growthrate']])

# 4. Net Profit Margin = Net Income/Total Revenue
merged_asst_lib_eq_net_rev_df['netprofitmargin_ratio'] = merged_asst_lib_eq_net_rev_df['netincome'] / merged_asst_lib_eq_net_rev_df['revenue']
# print(merged_asst_lib_eq_net_rev_df)

netprofmargin_ratio_plot = px.line(merged_asst_lib_eq_net_rev_df,
                      x='end', y='netprofitmargin_ratio',
                      title="AAPL Net Profit Margin Ratio",
                                    labels={
                                        'netprofitmargin_ratio': "Net Profit Margin Ratio",
                                        "end": "Date"
                                    })
netprofmargin_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_net_rev_df['netprofitmargin_ratio'])])

# Update y-axis interval to align with the first company
netprofmargin_ratio_plot.update_layout(yaxis=dict(dtick=0.004, range=[0, 0.26]))

netprofmargin_ratio_plot.show()

# check growth rate
merged_asst_lib_eq_net_rev_df['netprofitmargin_growthrate'] = ((merged_asst_lib_eq_net_rev_df['netprofitmargin_ratio'].shift(-1) - merged_asst_lib_eq_net_rev_df['netprofitmargin_ratio']) / merged_asst_lib_eq_net_rev_df['netprofitmargin_ratio']) * 100
print(merged_asst_lib_eq_net_rev_df[['end', 'netprofitmargin_ratio','netprofitmargin_growthrate']])

# print(merged_asst_lib_eq_net_rev_df[['end','revenue', 'assets']])

# 5. Asset Turnover Ratio = Total Revenue / (Beginning Assets + Ending Assets)/2)
# merged_asst_lib_eq_net_rev_df.loc['assetturnover_ratio'] = merged_asst_lib_eq_net_rev_df.loc['revenue'] / merged_asst_lib_eq_net_rev_df.loc['assets'].rolling(2).mean()
# Calculate average total assets
# merged_asst_lib_eq_net_rev_df['avg_assets'] = (merged_asst_lib_eq_net_rev_df['assets'].shift(1) + merged_asst_lib_eq_net_rev_df['assets']) / 2
# merged_asst_lib_eq_net_rev_df['asset_turnover_ratio'] = merged_asst_lib_eq_net_rev_df['revenue'] / merged_asst_lib_eq_net_rev_df['avg_assets']

# Calculate rolling average of total assets
window_size = 2
merged_asst_lib_eq_net_rev_df['rolling_avg_assets'] = merged_asst_lib_eq_net_rev_df['assets'].rolling(window=window_size).mean()

# Calculate asset turnover
merged_asst_lib_eq_net_rev_df['asset_turnover_ratio'] = merged_asst_lib_eq_net_rev_df['revenue'] / merged_asst_lib_eq_net_rev_df['rolling_avg_assets']
print(merged_asst_lib_eq_net_rev_df)

asset_turnover_ratio_plot = px.line(merged_asst_lib_eq_net_rev_df,
                      x='end', y='asset_turnover_ratio',
                      title="AAPL asset_turnover Ratio",
                                    labels={
                                        'asset_turnover_ratio': "Asset Turnover Ratio",
                                        "end": "Date"
                                    })
# update y-axis to start with 0
asset_turnover_ratio_plot.update_layout(yaxis=dict(dtick=0.5, range=[0, 8.5]))
asset_turnover_ratio_plot.show()

# growth rate
merged_asst_lib_eq_net_rev_df['assetsturnover_growthrate'] = ((merged_asst_lib_eq_net_rev_df['asset_turnover_ratio'].shift(-1) - merged_asst_lib_eq_net_rev_df['asset_turnover_ratio']) / merged_asst_lib_eq_net_rev_df['asset_turnover_ratio']) * 100
print(merged_asst_lib_eq_net_rev_df[['end', 'asset_turnover_ratio','assetsturnover_growthrate']])

# 6.Equity Ratio = Shareholder's Equity / Total Assets
# a leverage ratio that measures the portion of company resources that are funded by contributions of its equity participants and its earnings.
# Companies with a high equity ratio are known as “conservative” companies.
merged_asst_lib_eq_net_rev_df['equity_ratio'] = merged_asst_lib_eq_net_rev_df['equity'] / merged_asst_lib_eq_net_rev_df['assets']
print(merged_asst_lib_eq_net_rev_df)

# normalized to based year
merged_asst_lib_eq_net_rev_df['end'] = pd.to_datetime(merged_asst_lib_eq_net_rev_df['end'])
merged_asst_lib_eq_net_rev_df_filtered = merged_asst_lib_eq_net_rev_df.loc[merged_asst_lib_eq_net_rev_df['end'] > '2016-01-01']
# print(merged_asst_lib_eq_net_df_filtered)

equity_ratio_plot = px.line(merged_asst_lib_eq_net_rev_df_filtered,
                      x='end', y='equity_ratio',
                      title="AAPL Equity Ratio",
                                    labels={
                                        'equity_ratio': "Equity Ratio",
                                        "end": "Date"
                                    })
equity_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_net_rev_df_filtered['equity_ratio'])])

equity_ratio_plot.show()

# Growth Rate
merged_asst_lib_eq_net_rev_df_filtered['equity_growthrate'] = ((merged_asst_lib_eq_net_rev_df_filtered['equity_ratio'].shift(-1) - merged_asst_lib_eq_net_rev_df_filtered['equity_ratio']) / merged_asst_lib_eq_net_rev_df_filtered['equity_ratio']) * 100
print(merged_asst_lib_eq_net_rev_df_filtered[['end', 'equity_ratio','equity_growthrate']])

# print ratios and growth rate
# Current Ratio
merged_cur_asst_lib_df_filtered['year'] = merged_cur_asst_lib_df_filtered['end'].dt.year.astype(str)
current_ratio_table = tabulate(merged_cur_asst_lib_df_filtered[['year', 'current_ratio', 'currentratio_growthrate']], headers='keys', tablefmt='pretty')
print(current_ratio_table)

# D/E
merged_asst_lib_eq_df_filtered.loc[merged_asst_lib_eq_df_filtered['end'] > '2017-01-01', 'year'] = merged_asst_lib_eq_df_filtered['end'].dt.year.astype(str)
DE_ratio_table = tabulate(merged_asst_lib_eq_df_filtered[['year', 'debt_to_equity_ratio', 'DE_growthrate']], headers='keys', tablefmt='pretty')
print(DE_ratio_table)

# Return on Equity
# using loc to avoid warning
merged_asst_lib_eq_net_df_filtered.loc[merged_asst_lib_eq_net_df_filtered['end'] > '2017-01-01', 'year'] = merged_asst_lib_eq_net_df_filtered['end'].dt.year.astype(str)
roe_ratio_table = tabulate(merged_asst_lib_eq_net_df_filtered[['year', 'roe_ratio', 'roe_growthrate']], headers='keys', tablefmt='pretty')
print(roe_ratio_table)

# Net profit margin
merged_asst_lib_eq_net_rev_df['year'] = merged_asst_lib_eq_net_rev_df['end'].dt.year.astype(str)
netprofitmargin_ratio_table = tabulate(merged_asst_lib_eq_net_rev_df[['year', 'netprofitmargin_ratio', 'netprofitmargin_growthrate']], headers='keys', tablefmt='pretty')
print(netprofitmargin_ratio_table)


# Asset turnover ratio
merged_asst_lib_eq_net_rev_df['year'] = merged_asst_lib_eq_net_rev_df['end'].dt.year.astype(str)
assetsturnover_ratio_table = tabulate(merged_asst_lib_eq_net_rev_df[['year', 'asset_turnover_ratio', 'assetsturnover_growthrate']], headers='keys', tablefmt='pretty')
print(assetsturnover_ratio_table)

# Equity ratio
merged_asst_lib_eq_net_rev_df_filtered['year'] = merged_asst_lib_eq_net_rev_df_filtered['end'].dt.year.astype(str)
equity_ratio_table = tabulate(merged_asst_lib_eq_net_rev_df_filtered[['year', 'equity_ratio', 'equity_growthrate']], headers='keys', tablefmt='pretty')
print(equity_ratio_table)

# combine ratio results
merged_df = pd.merge(merged_cur_asst_lib_df_filtered[['year', 'current_ratio', 'currentratio_growthrate']], merged_asst_lib_eq_df_filtered[['year', 'debt_to_equity_ratio', 'DE_growthrate']], on='year', how='outer')
merged_df = pd.merge(merged_df, merged_asst_lib_eq_net_df_filtered[['year', 'roe_ratio', 'roe_growthrate']], on='year', how='outer')
merged_df = pd.merge(merged_df, merged_asst_lib_eq_net_rev_df[['year', 'netprofitmargin_ratio', 'netprofitmargin_growthrate']], on='year', how='outer')
merged_df = pd.merge(merged_df, merged_asst_lib_eq_net_rev_df[['year', 'asset_turnover_ratio', 'assetsturnover_growthrate']], on='year', how='outer')
merged_df = pd.merge(merged_df, merged_asst_lib_eq_net_rev_df_filtered[['year', 'equity_ratio', 'equity_growthrate']], on='year', how='outer')
merged_df_table = tabulate(merged_df, headers='keys', tablefmt='pretty')
print(merged_df_table)

"""
Second company = Kroger Co. (KR)
The Kroger Company, or simply Kroger, is an American retail company that operates (either directly or through its subsidiaries[5]) supermarkets and 
multi-department stores throughout the United States
"""

cik = search_comp('KR')  # call function search_comp to get cik_str
# print(companyCIK[companyCIK['cik_str'] == cik])

""" Data retrieval and EDA """
"""
Source: data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:

https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
"""

companyFacts2 = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
# print(companyFacts.json()['facts']['us-gaap']['SalesRevenueNet']['units'])

# get revenues data
"""
RevenueFromContractWithCustomerExcludingAssessedTax
Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer.
Tax collected from customer is tax assessed by governmental authority that is both imposed on and concurrent with specific revenue-producing transaction, 
including, but not limited to, sales, use, value added and excise.
"""

revenue_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['RevenueFromContractWithCustomerExcludingAssessedTax']['units']['USD'])
revenue_df2 = revenue_df.sort_values(by=['start'])
# check data structure
print(revenue_df2.info())
# no null data
# print(revenue_df2) # 81 rows start date between 2017-09-30 - 2023-07-01
# observation: has data both in annual and quarterly, has multiple forms, NaN in frame column

# get Assets and convert the facts on assets to a dataframe
"""
Assets 
Sum of the carrying amounts as of the balance sheet date of all assets that are recognized. 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
assets_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['Assets']['units']['USD'])
print(assets_df2) # 120 rows end 2009-01-31-2023-11-04
print(assets_df2.info())
# observed multiple filing for the same perious of data, for example 2011-09-24 10-K has 2 filing on 2011-10-26 and 2012-10-31
# print(assets_df.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(assets_df2['form'].unique()) # has multiple form ['10-Q' '10-K' '10-K/A']

# observation: there are NaN in the dataset.
# Data can be filed multiple times with the same or different frame. Frame shows either NaN or quartrely period.

# get current assets
"""
AssetsCurrent
Sum of the carrying amounts as of the balance sheet date of all assets that are expected to be realized in cash, sold, or consumed within one year (or the normal operating cycle, if longer). 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
cur_assets_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['AssetsCurrent']['units']['USD'])
print(cur_assets_df2) # 120 rows end 2009-01-31-2023-11-04
print(cur_assets_df2.info()) # non-null
# print(cur_assets_df2['form'].unique()) #['10-Q' '10-K' '10-K/A' '8-K']
# print(cur_assets_df2.columns) #Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')

# observation: frame column contains NaN

# get liabilities data and convert the facts on assets to a dataframe
"""
Liabilities
Sum of the carrying amounts as of the balance sheet date of all liabilities that are recognized. 
Liabilities are probable future sacrifices of economic benefits arising from present obligations of an entity to transfer assets 
or provide services to other entities in the future.
"""
liabilities_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['Liabilities']['units']['USD'])
print(liabilities_df2) # 120 rows end 2009-01-31-2023-11-04
print(liabilities_df2.info())
# print(liabilities_df2.columns) #Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(liabilities_df2['form'].unique()) # ['10-Q' '10-K' '10-K/A']

# get current liabilities
"""
LiabilitiesCurrent
Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
"""
cur_liabilities_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['LiabilitiesCurrent']['units']['USD'])
print(cur_liabilities_df2) # 120 rows end 2009-01-31-2023-11-04
print(cur_liabilities_df2.info())
# print(cur_liabilities_df2.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(cur_liabilities_df2['form'].unique()) # has multiple form ['10-Q' '10-K' '10-K/A']

# observation, there are NaN or quarterly period in frame. Different period of data can be filed at the same time for different forms.

# get stockholders' equity
"""
StockholdersEquity
Total of all stockholders' equity (deficit) items, net of receivables from officers, directors, owners, and affiliates of the entity which are attributable to the parent.
The amount of the economic entity's stockholders' equity attributable to the parent excludes the amount of stockholders' equity 
which is allocable to that ownership interest in subsidiary equity which is not attributable to the parent (noncontrolling interest, minority interest). 
This excludes temporary equity and is sometimes called permanent equity.
"""
equity_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['StockholdersEquity']['units']['USD'])
print(equity_df2) # 120 rows end 2009-01-31-2023-11-04
print(equity_df2.info())
# print(equity_df2.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(equity_df2['form'].unique()) # has multiple form ['10-Q' '10-K' '10-K/A']

# observation, frame can be NaN or shows quarterly. Different period of data can be filed at the same time.

# get net income
"""
NetIncomeLossLoss
The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
"""
netincome_df2 = pd.DataFrame.from_dict(companyFacts2.json()['facts']['us-gaap']['NetIncomeLoss']['units']['USD'])
print(netincome_df2) # 283 rows end 2009-01-31-2023-11-04
print(netincome_df2.info())
# print(netincome_df2.columns) # Index(['start', 'end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(netincome_df2['form'].unique()) # has multiple form ['10-K' '10-Q' '10-K/A']

# observation: val could be a negative value

"""
Data cleaning and wrangling - cleanup duplicated row and prepare data for the next step
"""
# filter for 10-K
revenue_df_filtered2 = revenue_df2[revenue_df2['form'] == '10-K']
# print(revenue_df_filtered2)
# print(revenue_df_filtered2.count()) # 31 rows 2017-09-30 - 2023-09-30

# sort data by end and filed dates
revenue_df_filtered2 = revenue_df_filtered2.sort_values(by=['end', 'filed'])

# remove quarterly data # 45 rows
# revenue_df_filtered2 = revenue_df_filtered2[~revenue_df_filtered2['frame'].str.contains('Q', na=False)]
revenue_df_filtered2['start'] = pd.to_datetime(revenue_df_filtered2['start'])
revenue_df_filtered2['end'] = pd.to_datetime(revenue_df_filtered2['end'])
revenue_df_filtered2['months_diff'] = ((revenue_df_filtered2['end'] - revenue_df_filtered2['start']) / pd.Timedelta(days=30)).astype(int)
revenue_df_filtered2 = revenue_df_filtered2[revenue_df_filtered2['months_diff'] >= 12] # there are the same record that filed multiple times, need to drop duplicated
revenue_df_filtered2 = revenue_df_filtered2.drop(columns=['months_diff'])

# remove duplicated rows of the same period and keep the row with the last filed.
revenue_df_filtered2 = revenue_df_filtered2.drop_duplicates(subset=['end'], keep='last')
# print(revenue_df_filtered2) # 7 rows, 2017-09-30 - 2023-09-30

# drop start as we no longer need this
revenue_df_filtered2 = revenue_df_filtered2.drop(columns='start')
# print(revenue_df_filtered2)

# filter for 10-K form only
assets_df_filtered2 = assets_df2[assets_df2['form'] == '10-K']
# print(assets_df_filtered2)
# print(assets_df_filtered2.count()) # 28 rows
# has duplicated row need to be dedup

# sort data by end and filed dates
assets_df_filtered2 = assets_df_filtered2.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
assets_df_filtered2 = assets_df_filtered2.drop_duplicates(subset=['end'], keep='last')
# print(assets_df_filtered2) # 15 rows end 2009-01-31-2023-01-28

# filter for 10-K form
cur_assets_df_filtered2 = cur_assets_df2[cur_assets_df2['form'] == '10-K']
# print(assets_df_filtered2) # end date 2009-01-31 - 2023-01-28
# print(assets_df_filtered2.count()) # 15 rows
# print(assets_df_filtered2['form'].unique()) # return ['10-K']

# sort data by end and filed dates
cur_assets_df_filtered2 = cur_assets_df_filtered2.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
cur_assets_df_filtered2 = cur_assets_df_filtered2.drop_duplicates(subset=['end'], keep='last')
# print(cur_assets_df_filtered2) # 15 rows end 2009-01-31 - 2023-01-28

liabilities_df_filtered2 = liabilities_df2[liabilities_df2['form'] == '10-K']
# print(liabilities_df_filtered2) # end 2009-01-31 - 2023-01-28
# print(liabilities_df_filtered2.count()) # 28 rows

# sort data by end and filed dates
liabilities_df_filtered2 = liabilities_df_filtered2.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
liabilities_df_filtered2 = liabilities_df_filtered2.drop_duplicates(subset=['end'], keep='last')
# print(liabilities_df_filtered2) # 28 rows , end 2009-01-31 - 2023-01-28

# filter for the 10-K form
cur_liabilities_df_filtered2 = cur_liabilities_df2[cur_liabilities_df2['form'] == '10-K']
# print(cur_liabilities_df_filtered2) #end 2009-01-31 - 2023-01-28
# print(cur_liabilities_df_filtered2.count()) # 28 rows

# sort data by end and filed dates
cur_liabilities_df_filtered2 = cur_liabilities_df_filtered2.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
cur_liabilities_df_filtered2 = cur_liabilities_df_filtered2.drop_duplicates(subset=['end'], keep='last')
# print(cur_liabilities_df_filtered2) # 15 rows  #end 2009-01-31 - 2023-01-28

equity_df_filtered2 = equity_df2[equity_df2['form'] == '10-K']
# print(equity_df_filtered2) #end 2009-01-31 - 2023-01-28
# print(equity_df_filtered2.count()) # 28 rows
# contains duplicated end date

# sort data by end and filed dates
equity_df_filtered2 = equity_df_filtered2.sort_values(by=['end', 'filed'])

# remove duplicated rows of the same period and keep the row with the last filed.
equity_df_filtered2 = equity_df_filtered2.drop_duplicates(subset=['end'], keep='last')
# print(equity_df_filtered2) # 15 rows end 2009-01-31 - 2023-01-28

# filter for 10-K
netincome_df_filtered2 = netincome_df2[netincome_df2['form'] == '10-K']
# print(netincome_df_filtered)
# print(netincome_df_filtered.count()) # 133 rows 2007-09-29 - 2023-09-30
# print(netincome_df_filtered['form'].unique()) # return ['10-K']

# sort data by end and filed dates
netincome_df_filtered2 = netincome_df_filtered2.sort_values(by=['end', 'filed'])

# remove quarterly data # 45 rows
netincome_df_filtered2['start'] = pd.to_datetime(netincome_df_filtered2['start'])
netincome_df_filtered2['end'] = pd.to_datetime(netincome_df_filtered2['end'])
netincome_df_filtered2['months_diff'] = ((netincome_df_filtered2['end'] - netincome_df_filtered2['start']) / pd.Timedelta(days=30)).astype(int)
netincome_df_filtered2 = netincome_df_filtered2[netincome_df_filtered2['months_diff'] >= 12] # 17 rows end date 2007-09-29-2023-09-30
netincome_df_filtered2 = netincome_df_filtered2.drop(columns=['months_diff'])

# remove duplicated rows of the same period and keep the row with the last filed.
netincome_df_filtered2 = netincome_df_filtered2.drop_duplicates(subset=['end'], keep='last')

# drop start date, we only need end date
netincome_df_filtered2 = netincome_df_filtered2.drop(columns='start')
# print(netincome_df_filtered2) # 16 rows end 2008-02-02-2023-01-28

""" Summary and graph"""
desc_rev2 = revenue_df_filtered2.describe()
print(desc_rev2['val'])
# mean 310,421,142,857.143
# min  229,234,000,000.000
# max  394,328,000,000.000

# create visual
rev_plot2 = px.line(revenue_df_filtered2,
                  title='KR Revenues',
                  x='end',
                  y='val')
rev_plot2.show()

desc_assets2 = assets_df_filtered2.describe()
print(desc_assets2['val'])
# mean 34,408,000,000.000
# min  23,126,000,000.000
# max  49,623,000,000.000

# what is the assets trend?
assets_plot2 = px.line(assets_df_filtered2,
                      title=f"KR Assets",
                      x="end",
                      y="val")
assets_plot2.show()

desc_cur_assets2 = cur_assets_df2.describe()
print(desc_cur_assets2)
# mean 9,771,908,333.333
# min  6,706,000,000.000
# max  13,439,000,000.000

cur_assets_plot2 = px.line(cur_assets_df_filtered2,
                      title=f"KR Current Assets",
                      x="end",
                      y="val")
cur_assets_plot2.show() # upward trends with some dips in 2011, 2018, and 2021

desc_liabilities2 = liabilities_df_filtered2.describe()
print(desc_liabilities2['val'])
# mean 12,344,583,333.333
# min  7,629,000,000.000
# max  17,738,000,000.000

# what is the liabilities trend look like?
liabilities_plot2 = px.line(liabilities_df_filtered2,
                      title=f"KR Liabilities",
                      x="end",
                      y="val")
liabilities_plot2.show() # gradually upward trend between 2009-2017, plateau between 2017-2019 then a sharp spike in 2019-2020.

desc_cur_liabilities2 = cur_liabilities_df2.describe()
print(desc_cur_liabilities2)
# mean 6,760,208,333.333
# min  3,761,000,000.000
# max  11,209,000,000.000

cur_liabilities_plot2 = px.line(cur_liabilities_df_filtered2,
                      title=f"AAPL Current Liabilities",
                      x="end",
                      y="val")
cur_liabilities_plot2.show() # upward trends, steady upward since 2020

desc_equity2 = equity_df2.describe()
print(desc_equity2)
# mean 6,760,208,333.333
# min  3,761,000,000.000
# max  11,209,000,000.000

equity_plot2 = px.line(equity_df_filtered2,
                      title=f"KR Stockholder Equity",
                      x="end",
                      y="val")
equity_plot2.show() # a dip between 2011-2012 then upward trend

desc_netincome2 = netincome_df_filtered2.describe()
print(desc_netincome2['val'])
# mean 1,635,250,000.000
# min  70,000,000.000
# max  3,110,000,000.000

# what is the netincome trend?
netincome_plot2 = px.line(netincome_df_filtered2,
                      title=f"KR Net Income & Loss",
                      x="end",
                      y="val")
netincome_plot2.show() # fluctuation

# merge total assets and total liabilities using end column for calculate current ratio
merged_asst_lib_df2 = pd.merge(assets_df_filtered2, liabilities_df_filtered2, on=['end'], how='inner')
merged_asst_lib_df2 = merged_asst_lib_df2.drop(merged_asst_lib_df2.columns[9:], axis=1)
# print(merged_asst_lib_df2) # 15 rows 2009-01-31 - 2023-01-28

merged_asst_lib_df2 = merged_asst_lib_df2.rename(columns={'val_x': 'assets', 'val_y': 'liabilities'})
print(merged_asst_lib_df2) # 15 rows 2009-01-31 - 2023-01-28

# get summaries of merged dataframe
desc_merged_asst_lib_df2 = merged_asst_lib_df2.describe()
print(desc_merged_asst_lib_df2[['assets', 'liabilities']])

# what is the liabilities trend?
merged_plot12 = px.bar(merged_asst_lib_df2,
                      x='end', y=['assets', 'liabilities'],
                      title="KR Assets & Liabilities", barmode='group')
merged_plot12.update_layout(yaxis_title="Value in $")
merged_plot12.update_layout(xaxis_title="Date")

merged_plot12.show() # assets and liabilities go parallel to each other

# merge total assets and total liability with shareholders' equity to calculate D/E ratio
# filed date for the same period appears to be different from each other so using end date to join the two data
merged_asst_lib_eq_df2 = pd.merge(merged_asst_lib_df2, equity_df_filtered2, on='end')
merged_asst_lib_eq_df2 = merged_asst_lib_eq_df2.drop(merged_asst_lib_eq_df2.columns[10:], axis=1)
merged_asst_lib_eq_df2 = merged_asst_lib_eq_df2.rename(columns={'val': 'equity'})
print(merged_asst_lib_eq_df2) # 15 rows 2009-01-31 - 2023-01-28

desc_merged_asst_lib_eq_df2 = merged_asst_lib_eq_df2.describe()
print(desc_merged_asst_lib_eq_df2[['liabilities', 'equity']])

# plot graph, check the trends
merged_plot22 = px.line(merged_asst_lib_eq_df2,
                      x='end', y=['liabilities', 'equity'],
                      title="KR Total Liabilities & Shareholders' Equity")
merged_plot22.update_layout(yaxis_title="Value in $")
merged_plot22.update_layout(xaxis_title="Date")
merged_plot22.show() # equity appears to be pateau, liabilities has gradually increased with a spike in 2019

# merge net income for calculate ROE
# filed date can be different for the same period so join using end date instead of accn
# update the end date type to datetime to join the data
merged_asst_lib_eq_df2['end'] = pd.to_datetime(merged_asst_lib_eq_df2['end'])

# merge data
merged_asst_lib_eq_net_df2 = pd.merge(merged_asst_lib_eq_df2, netincome_df_filtered2, on='end')
merged_asst_lib_eq_net_df2 = merged_asst_lib_eq_net_df2.drop(merged_asst_lib_eq_net_df2.columns[11:], axis=1)
merged_asst_lib_eq_net_df2 = merged_asst_lib_eq_net_df2.rename(columns={'val': 'netincome'})
print(merged_asst_lib_eq_net_df2) # 15 rows 2009-01-31 - 2023-01-28
# print(merged_asst_lib_eq_net_df2.columns)

desc_merged_asst_lib_eq_net_df2 = merged_asst_lib_eq_net_df2.describe()
print(desc_merged_asst_lib_eq_net_df2[['netincome', 'equity']])

# plot graph, check the trend
merged_plot32 = px.line(merged_asst_lib_eq_net_df2,
                      x='end', y=['netincome', 'equity'],
                      title="KR Net Income & Shareholders' Equity")

# Update layout to set x-axis and y-axis title
merged_plot32.update_layout(yaxis_title="Value in $")
merged_plot32.update_layout(xaxis_title="Date")

# Show the plot
merged_plot32.show()

# merge sales revenue data
# print(merged_asst_lib_eq_net_df2['end'], revenue_df_filtered2['end'])
# print(merged_asst_lib_eq_net_df2)
# print(revenue_df_filtered2)

# end date in other data points are at the beginning of month different than in the revenue file which is at the end of Sept, need to extract year to join by year.
merged_asst_lib_eq_net_df2['year'] = merged_asst_lib_eq_net_df2['end'].dt.year
revenue_df_filtered2['year'] = revenue_df_filtered2['end'].dt.year

# merge revenue data to the other data
merged_asst_lib_eq_net_rev_df2 = pd.merge(merged_asst_lib_eq_net_df2, revenue_df_filtered2, on='year')
# print(merged_asst_lib_eq_net_rev_df2.columns)
merged_asst_lib_eq_net_rev_df2 = merged_asst_lib_eq_net_rev_df2.drop(merged_asst_lib_eq_net_rev_df2.columns[14:], axis=1)
merged_asst_lib_eq_net_rev_df2 = merged_asst_lib_eq_net_rev_df2.rename(columns={'val': 'revenue', 'end_x':'end'})

# drop unused columns
merged_asst_lib_eq_net_rev_df2 = merged_asst_lib_eq_net_rev_df2.drop(columns=['year', 'end_y'])

print(merged_asst_lib_eq_net_rev_df2) # 7 rows

desc_merged_asst_lib_eq_net_rev_df2 = merged_asst_lib_eq_net_rev_df2.describe()
print(desc_merged_asst_lib_eq_net_rev_df2[['netincome', 'revenue']])

# what is the liabilities trend?
merged_plot42 = px.line(merged_asst_lib_eq_net_rev_df2,
                      x='end', y=['netincome', 'revenue'],
                      title="KR Net Income & Total Revenue")

# Update layout to set x-axis and y-axis title
merged_plot42.update_layout(yaxis_title="Value in $")
merged_plot42.update_layout(xaxis_title="Date")

# Show the plot
merged_plot42.show()

# merge current assets and current liabilities
# print(cur_assets_df_filtered2)
# print(cur_liabilities_df_filtered2)
merged_cur_asst_lib_df2 = pd.merge(cur_assets_df_filtered2, cur_liabilities_df_filtered2, on=['accn', 'end'], how='inner')
merged_cur_asst_lib_df2 = merged_cur_asst_lib_df2.drop(merged_cur_asst_lib_df2.columns[9:], axis=1)
merged_cur_asst_lib_df2 = merged_cur_asst_lib_df2.rename(columns={'val_x': 'current_assets', 'val_y': 'current_liabilities'})
print(merged_cur_asst_lib_df2) # 15 rows end 2008-09-27 to 2023-09-30

# get summaries of merged dataframe
desc_merged_cur_asst_lib_df2 = merged_cur_asst_lib_df2.describe()
print(desc_merged_cur_asst_lib_df2[['current_assets', 'current_liabilities']])

# what is the liabilities trend?
merged_plot52 = px.line(merged_cur_asst_lib_df2,
                      x='end', y=['current_assets', 'current_liabilities'],
                      title="KR Current Assets & Current Liabilities")

# Update layout to set x-axis and y-axis title
merged_plot52.update_layout(yaxis_title="Value in $")
merged_plot52.update_layout(xaxis_title="Date")

# Show the plot
merged_plot52.show() # upward trend almost parallel to each other. less working capital between 2009-2011 then increasing over time.

""" Ratios """
# 1. Current ratio = Current Assets / Current Liabilities
# this ratio help us understand the company's finanical strength, how likely the company can meet its' obligations.

merged_cur_asst_lib_df2['current_ratio'] = merged_cur_asst_lib_df2['current_assets']/ merged_cur_asst_lib_df2['current_liabilities']
# print(merged_asst_lib_df)

# create a table
current_ratio_table2 = tabulate(merged_cur_asst_lib_df2[['end', 'current_ratio']], headers='keys', tablefmt='pretty')
print(current_ratio_table2)

# normalized to based year
merged_cur_asst_lib_df2['end'] = pd.to_datetime(merged_cur_asst_lib_df2['end'])
merged_cur_asst_lib_df_filtered2 = merged_cur_asst_lib_df2.loc[merged_cur_asst_lib_df2['end'] > '2016-01-01']
print(merged_cur_asst_lib_df_filtered2)

current_ratio_plot2 = px.line(merged_cur_asst_lib_df_filtered2,
                      x='end', y='current_ratio',
                      title="KR Current Ratio")
current_ratio_plot2.update_yaxes(range=[0, max(merged_cur_asst_lib_df_filtered2['current_ratio']+1)])

# Update y-axis interval to 0.5 to align with the first company
current_ratio_plot2.update_layout(yaxis=dict(dtick=0.5, range=[0, 3.5]))

# Update layout to set x-axis and y-axis title
current_ratio_plot2.update_layout(yaxis_title="Ratio")
current_ratio_plot2.update_layout(xaxis_title="Date")

current_ratio_plot2.show()

# create a combo chart to show Assets, Liabilities, and Current Ratio

# Create a bar chart for assets and liabilities
bar_chart = go.Figure()
bar_chart.add_trace(go.Bar(x=merged_cur_asst_lib_df_filtered2['end'],
                           y=merged_cur_asst_lib_df_filtered2['current_assets'],
                           name='Assets'))
bar_chart.add_trace(go.Bar(x=merged_cur_asst_lib_df_filtered2['end'],
                           y=merged_cur_asst_lib_df_filtered2['current_liabilities'],
                           name='Liabilities'))

# Create a line chart for current ratio
line_chart = go.Figure()
line_chart.add_trace(go.Scatter(x=merged_cur_asst_lib_df_filtered2['end'],
                                y=merged_cur_asst_lib_df_filtered2['current_ratio'],
                                mode='lines',
                                name='Current Ratio'))

# combining bar and line charts
combo_chart = go.Figure()

for trace in bar_chart.data:
    combo_chart.add_trace(trace)

combo_chart.add_trace(line_chart.data[0])

# Update layout
combo_chart.update_layout(barmode='stack', title='Combo Graph: Assets, Liabilities, and Current Ratio')

combo_chart.show()


# check growth rate
merged_cur_asst_lib_df_filtered2['currentratio_growthrate'] = ((merged_cur_asst_lib_df_filtered2['current_ratio'].shift(-1) - merged_cur_asst_lib_df_filtered2['current_ratio']) / merged_cur_asst_lib_df_filtered2['current_ratio']) * 100
print(merged_cur_asst_lib_df_filtered2[['end', 'current_ratio', 'currentratio_growthrate']])

# 2. Debt-to-Equity Ratio (D/E) = Total liabilities / Total shareholders' Equity
# this ratio help us understand the net worth of the company by comparing the total shareholders' equity to its total liabilities

merged_asst_lib_eq_df2['debt_to_equity_ratio'] = merged_asst_lib_eq_df2['liabilities']/merged_asst_lib_eq_df2['equity']
print(merged_asst_lib_eq_df2)

# normalized to based year
merged_asst_lib_eq_df2['end'] = pd.to_datetime(merged_asst_lib_eq_df2['end'])
merged_asst_lib_eq_df_filtered2 = merged_asst_lib_eq_df2.loc[merged_asst_lib_eq_df2['end'] > '2016-01-01']
# print(merged_asst_lib_eq_df_filtered)

debt_to_equity_ratio_plot2 = px.line(merged_asst_lib_eq_df_filtered2,
                      x='end', y='debt_to_equity_ratio',
                      title="KR Debt-to-Equity Ratio",
                                    labels={
                                        "debt_to_equity_ratio": "Debt-to-Equity Ratio",
                                        "end": "Date"
                                    })
# debt_to_equity_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_df_filtered2['debt_to_equity_ratio'])])

# Update y-axis interval to 0.5 to align with the first company
debt_to_equity_ratio_plot2.update_layout(yaxis=dict(dtick=1, range=[0, 6]))

debt_to_equity_ratio_plot2.show()

# check growth rate
merged_asst_lib_eq_df_filtered2['DE_growthrate'] = ((merged_asst_lib_eq_df_filtered2['debt_to_equity_ratio'].shift(-1) - merged_asst_lib_eq_df_filtered2['debt_to_equity_ratio']) / merged_asst_lib_eq_df_filtered2['debt_to_equity_ratio']) * 100
print(merged_asst_lib_eq_df_filtered2[['end', 'debt_to_equity_ratio','DE_growthrate']])

# 3. Return on Equity = Net Income / Shareholder Equity (ref, https://www.investopedia.com/ask/answers/070914/how-do-you-calculate-return-equity-roe.asp)
# this ratio provides insight into the efficiently of company on managing shareholders' equity. it indicates how much money shareholders make on their investment.

merged_asst_lib_eq_net_df2['roe_ratio'] = merged_asst_lib_eq_net_df2['netincome'] / merged_asst_lib_eq_net_df2['equity']
# print(merged_asst_lib_eq_net_df2)

# normalized to based year
merged_asst_lib_eq_net_df2['end'] = pd.to_datetime(merged_asst_lib_eq_net_df2['end'])
merged_asst_lib_eq_net_df_filtered2 = merged_asst_lib_eq_net_df2.loc[merged_asst_lib_eq_net_df2['end'] > '2016-01-01']
# print(merged_asst_lib_eq_net_df_filtered2)

roe_ratio_plot2 = px.line(merged_asst_lib_eq_net_df_filtered2,
                      x='end', y='roe_ratio',
                      title="KR Return on Equity Ratio",
                                    labels={
                                        'roe_ratio': "Return on Equity Ratio",
                                        "end": "Date"
                                    })
roe_ratio_plot2.update_yaxes(range=[0, max(merged_asst_lib_eq_net_df_filtered2['roe_ratio'])])

# Update y-axis interval to align with the first company
roe_ratio_plot2.update_layout(yaxis=dict(dtick=0.05, range=[0, 2]))

roe_ratio_plot2.show()

# check growth rate
merged_asst_lib_eq_net_df_filtered2['roe_growthrate'] = ((merged_asst_lib_eq_net_df_filtered2['roe_ratio'].shift(-1) - merged_asst_lib_eq_net_df_filtered2['roe_ratio']) / merged_asst_lib_eq_net_df_filtered2['roe_ratio']) * 100
print(merged_asst_lib_eq_net_df_filtered2[['end', 'roe_ratio','roe_growthrate']])

# 4. Net Profit Margin = Net Income/Total Revenue
merged_asst_lib_eq_net_rev_df2['netprofitmargin_ratio'] = merged_asst_lib_eq_net_rev_df2['netincome'] / merged_asst_lib_eq_net_rev_df2['revenue']
# print(merged_asst_lib_eq_net_rev_df2)

# create a table
netprofitmargin_ratio_table2 = tabulate(merged_asst_lib_eq_net_rev_df2[['end', 'netprofitmargin_ratio']], headers='keys', tablefmt='pretty')
print(netprofitmargin_ratio_table2)

netprofmargin_ratio_plot2 = px.line(merged_asst_lib_eq_net_rev_df2,
                      x='end', y='netprofitmargin_ratio',
                      title="KR Net Profit Margin Ratio",
                                    labels={
                                        'netprofitmargin_ratio': "Net Profit Margin Ratio",
                                        "end": "Date"
                                    })
# netprofmargin_ratio_plot2.update_yaxes(range=[0, max(merged_asst_lib_eq_net_rev_df2['netprofitmargin_ratio'])])

# Update y-axis interval to align with the first company
netprofmargin_ratio_plot2.update_layout(yaxis=dict(dtick=0.004, range=[0, 0.26]))
netprofmargin_ratio_plot2.show()

# check growth rate
merged_asst_lib_eq_net_rev_df2['netprofitmargin_growthrate'] = ((merged_asst_lib_eq_net_rev_df2['netprofitmargin_ratio'].shift(-1) - merged_asst_lib_eq_net_rev_df2['netprofitmargin_ratio']) / merged_asst_lib_eq_net_rev_df2['netprofitmargin_ratio']) * 100
print(merged_asst_lib_eq_net_rev_df2[['end', 'netprofitmargin_ratio','netprofitmargin_growthrate']])


# 5. Asset Turnover Ratio = Total Revenue / (Beginning Assets + Ending Assets)/2)
# Calculate rolling average of total assets
window_size = 2
merged_asst_lib_eq_net_rev_df2['rolling_avg_assets'] = merged_asst_lib_eq_net_rev_df2['assets'].rolling(window=window_size).mean()

# Calculate asset turnover
merged_asst_lib_eq_net_rev_df2['asset_turnover_ratio'] = merged_asst_lib_eq_net_rev_df2['revenue'] / merged_asst_lib_eq_net_rev_df2['rolling_avg_assets']
print(merged_asst_lib_eq_net_rev_df2)

# create a table
asset_turnover_ratio_table2 = tabulate(merged_asst_lib_eq_net_rev_df2[['end', 'asset_turnover_ratio']], headers='keys', tablefmt='pretty')
print(asset_turnover_ratio_table2)

asset_turnover_ratio_plot2 = px.line(merged_asst_lib_eq_net_rev_df2,
                      x='end', y='asset_turnover_ratio',
                      title="KR asset_turnover Ratio",
                                    labels={
                                        'asset_turnover_ratio': "Asset Turnover Ratio",
                                        "end": "Date"
                                    })
asset_turnover_ratio_plot2.update_yaxes(range=[0, max(merged_asst_lib_eq_net_rev_df2['asset_turnover_ratio'])])

# Update y-axis interval to align with the first company
asset_turnover_ratio_plot2.update_layout(yaxis=dict(dtick=0.5, range=[0, 8.5]))
asset_turnover_ratio_plot2.show()

# growth rate
merged_asst_lib_eq_net_rev_df2['assetsturnover_growthrate'] = ((merged_asst_lib_eq_net_rev_df2['asset_turnover_ratio'].shift(-1) - merged_asst_lib_eq_net_rev_df2['asset_turnover_ratio']) / merged_asst_lib_eq_net_rev_df2['asset_turnover_ratio']) * 100
print(merged_asst_lib_eq_net_rev_df2[['end', 'asset_turnover_ratio','assetsturnover_growthrate']])

# 6.Equity Ratio = Shareholder's Equity / Total Assets
# a leverage ratio that measures the portion of company resources that are funded by contributions of its equity participants and its earnings. Companies with a high equity ratio are known as “conservative” companies.
merged_asst_lib_eq_net_rev_df2['equity_ratio'] = merged_asst_lib_eq_net_rev_df2['equity'] / merged_asst_lib_eq_net_rev_df2['assets']
print(merged_asst_lib_eq_net_rev_df2)

# normalized to based year
merged_asst_lib_eq_net_rev_df2['end'] = pd.to_datetime(merged_asst_lib_eq_net_rev_df2['end'])
merged_asst_lib_eq_net_rev_df_filtered2 = merged_asst_lib_eq_net_rev_df2.loc[merged_asst_lib_eq_net_rev_df2['end'] > '2016-01-01']
# print(merged_asst_lib_eq_net_df_filtered2)

equity_ratio_plot2 = px.line(merged_asst_lib_eq_net_rev_df_filtered2,
                      x='end', y='equity_ratio',
                      title="KR Equity Ratio",
                                    labels={
                                        'equity_ratio': "Equity Ratio",
                                        "end": "Date"
                                    })
equity_ratio_plot2.update_yaxes(range=[0, max(merged_asst_lib_eq_net_rev_df_filtered2['equity_ratio'])])

# Update y-axis interval to align with the first company
equity_ratio_plot2.update_layout(yaxis=dict(dtick=0.05, range=[0, 0.35]))
equity_ratio_plot2.show()

equity_ratio_plot2.show()

# Growth Rate
merged_asst_lib_eq_net_rev_df_filtered2['equity_growthrate'] = ((merged_asst_lib_eq_net_rev_df_filtered2['equity_ratio'].shift(-1) - merged_asst_lib_eq_net_rev_df_filtered2['equity_ratio']) / merged_asst_lib_eq_net_rev_df_filtered2['equity_ratio']) * 100
print(merged_asst_lib_eq_net_rev_df_filtered2[['end', 'equity_ratio','equity_growthrate']])

# print ratios and growth rate
# Current Ratio
merged_cur_asst_lib_df_filtered2['end'] = pd.to_datetime(merged_cur_asst_lib_df_filtered2['end'])
merged_cur_asst_lib_df_filtered2['year'] = merged_cur_asst_lib_df_filtered2['end'].dt.year.astype(str)
current_ratio_table2 = tabulate(merged_cur_asst_lib_df_filtered2[['year', 'current_ratio', 'currentratio_growthrate']], headers='keys', tablefmt='pretty')
print(current_ratio_table2)

# D/E
merged_asst_lib_eq_df_filtered2.loc[merged_asst_lib_eq_df_filtered2['end'] > '2017-01-01', 'year'] = merged_asst_lib_eq_df_filtered2['end'].dt.year.astype(str)
DE_ratio_table2 = tabulate(merged_asst_lib_eq_df_filtered2[['year', 'debt_to_equity_ratio', 'DE_growthrate']], headers='keys', tablefmt='pretty')
print(DE_ratio_table2)

# Return on Equity
# using loc to avoid warning
merged_asst_lib_eq_net_df_filtered2.loc[merged_asst_lib_eq_net_df_filtered2['end'] > '2017-01-01', 'year'] = merged_asst_lib_eq_net_df_filtered2['end'].dt.year.astype(str)
roe_ratio_table2 = tabulate(merged_asst_lib_eq_net_df_filtered2[['year', 'roe_ratio', 'roe_growthrate']], headers='keys', tablefmt='pretty')
print(roe_ratio_table2)

# Net profit margin
merged_asst_lib_eq_net_rev_df2['year'] = merged_asst_lib_eq_net_rev_df2['end'].dt.year.astype(str)
netprofitmargin_ratio_table2 = tabulate(merged_asst_lib_eq_net_rev_df2[['year', 'netprofitmargin_ratio', 'netprofitmargin_growthrate']], headers='keys', tablefmt='pretty')
print(netprofitmargin_ratio_table2)


# Asset turnover ratio
merged_asst_lib_eq_net_rev_df2['year'] = merged_asst_lib_eq_net_rev_df2['end'].dt.year.astype(str)
assetsturnover_ratio_table2 = tabulate(merged_asst_lib_eq_net_rev_df2[['year', 'asset_turnover_ratio', 'assetsturnover_growthrate']], headers='keys', tablefmt='pretty')
print(assetsturnover_ratio_table)

# Equity ratio
merged_asst_lib_eq_net_rev_df_filtered2['year'] = merged_asst_lib_eq_net_rev_df_filtered2['end'].dt.year.astype(str)
equity_ratio_table2 = tabulate(merged_asst_lib_eq_net_rev_df_filtered2[['year', 'equity_ratio', 'equity_growthrate']], headers='keys', tablefmt='pretty')
print(equity_ratio_table2)

# combine ratio results
merged_df2 = pd.merge(merged_cur_asst_lib_df_filtered2[['year', 'current_ratio', 'currentratio_growthrate']], merged_asst_lib_eq_df_filtered2[['year', 'debt_to_equity_ratio', 'DE_growthrate']], on='year', how='outer')
merged_df2 = pd.merge(merged_df2, merged_asst_lib_eq_net_df_filtered2[['year', 'roe_ratio', 'roe_growthrate']], on='year', how='outer')
merged_df2 = pd.merge(merged_df2, merged_asst_lib_eq_net_rev_df2[['year', 'netprofitmargin_ratio', 'netprofitmargin_growthrate']], on='year', how='outer')
merged_df2 = pd.merge(merged_df2, merged_asst_lib_eq_net_rev_df2[['year', 'asset_turnover_ratio', 'assetsturnover_growthrate']], on='year', how='outer')
merged_df2 = pd.merge(merged_df2, merged_asst_lib_eq_net_rev_df_filtered2[['year', 'equity_ratio', 'equity_growthrate']], on='year', how='outer')
merged_df_table2 = tabulate(merged_df2, headers='keys', tablefmt='pretty')
print(merged_df_table2)

print('End of code. Thank you.')
