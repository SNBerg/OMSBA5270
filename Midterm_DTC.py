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

# setup display so it shows all columns
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

pd.options.plotting.backend = 'plotly'

# set number float format
pd.options.display.float_format = '{:.3f}'.format

# function to get cik_str for the selected company
def search_comp(ticker):
    return(companyCIK.loc[companyCIK['ticker'] == ticker, 'cik_str'].iloc[0])

""" Data pre-processing """
# create a request header
# using seattlu account to identify me as a user who makes a request
headers = {'User-Agent' : "sberg@seattleu.edu"}

# get all companies data from the company_tickers.json
# this will return a set of dictionary with cik_str (cik number), ticker (company symbol), title (company name)
# for example {'0': {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'}, '1': {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'},...
companyTickers = requests.get(f"https://www.sec.gov/files/company_tickers.json", headers=headers)
# print(companyTickers.json())

companyCIK = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
# print(companyCIK)

# adding leading 0s
companyCIK['cik_str'] = companyCIK['cik_str'].astype(str).str.zfill(10)
# print(companyCIK)

# First company = Apple Inc. (AAPL)
cik = search_comp('AAPL')  # call function search_comp to get cik_str
# print(companyCIK[companyCIK['cik_str'] == cik])

""" EDA """
"""
Source: data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:

https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
"""

companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
# print(companyFacts.json()['facts']['us-gaap']['SalesRevenueGoodsNet']['units'])

# get revenues data
"""
SalesRevenueGoodsNet
Aggregate revenue during the period from the sale of goods in the normal course of business, after deducting returns, allowances and discounts.
"""

revenue_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['SalesRevenueGoodsNet']['units']['USD'])
revenue_df = revenue_df.sort_values(by=['start'])
# check data structure
print(revenue_df.info())
# no null data
# print(revenue_df) # 201 rows start date between 2007-02-04-2017-11-05
# has data both in annual and quarterly, has multiple forms

# statistics summary
print(revenue_df.describe())

# observation: frame appears to show calendar year period however this column has na
# data has the same filed date

# remove na
# revenue_df = revenue_df[revenue_df.frame.notna()]

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

# statistics summary
print(assets_df.describe())
# print(assets_df.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(assets_df['form'].unique()) # has multiple form ['10-K' '10-Q' '8-K']

# observation: there are NaN in the dataset.
# There could be more than one data filed at the same time. For example 2009-10-27 has two end years – 2008-09-27 and 2009-09-26.

# check data to understand what accn column contain
# assets_df = assets_df.sort_values(by=['accn', 'end'])
# print(assets_df.iloc[0])

# observation: fy and fp is based on filed date.
# accn are the same for the data that filed on the same date.
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
# statistics summary
print(cur_assets_df.describe())

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

# statistics summary
print(liabilities_df.describe())

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

# statistics summary
print(cur_liabilities_df.describe())

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

# statistics summary
print(equity_df.describe())

# get net income
"""
revenueLoss
The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
"""
revenue_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['revenueLoss']['units']['USD'])
print(revenue_df) # 302 rows end 2007-09-29-2023-09-30
print(revenue_df.info())
# print(revenue_df.columns) # Index(['start', 'end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(revenue_df['form'].unique()) # has multiple form ['10-K' '10-K/A' '10-Q' '8-K']

# statistics summary
print(revenue_df.describe())

"""
Data cleaning and wrangling - cleanup duplicated row and prepare data for the next step
"""
# filter for 10-K
revenue_df_filtered = revenue_df[revenue_df['form'] == '10-K']
# print(revenue_df_filtered)
# print(revenue_df_filtered.count()) # 91 rows 2008-02-02 - 2018-02-03


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
# print(revenue_df_filtered) # 11 rows, 2008-02-02 - 2018-02-03

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

""" Summary and graph"""
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

desc_revenue = revenue_df_filtered.describe()
print(desc_revenue['val'])
# mean 46304294117.647
# min  3496000000.000
# max  99,803,000,000.000

# what is the assets trend?
revenue_plot = px.line(revenue_df_filtered,
                      title=f"AAPL Net Income & Loss",
                      x="end",
                      y="val")
revenue_plot.show()

# merge total assets and total liabilities using accn column for calculate current ratio
# print(assets_df_filtered)
# print(liabilities_df_filtered)
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
# print(revenue_df_filtered)
# update the end date type to datetime to join the data
merged_asst_lib_eq_df['end'] = pd.to_datetime(merged_asst_lib_eq_df['end'])

# merge data
merged_asst_lib_eq_net_df = pd.merge(merged_asst_lib_eq_df, revenue_df_filtered, on='end')
merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.drop(merged_asst_lib_eq_net_df.columns[12:], axis=1)
merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.rename(columns={'val': 'revenue'})
merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.drop(columns='start')
print(merged_asst_lib_eq_net_df) # 16 rows
# print(merged_asst_lib_eq_net_df.columns)

desc_merged_asst_lib_eq_net_df = merged_asst_lib_eq_net_df.describe()
print(desc_merged_asst_lib_eq_net_df[['revenue', 'equity']])

# what is the liabilities trend?
merged_plot3 = px.line(merged_asst_lib_eq_net_df,
                      x='end', y=['revenue', 'equity'],
                      title="AAPL Net Income & Shareholders' Equity")

# Update layout to set x-axis and y-axis title
merged_plot3.update_layout(yaxis_title="Value in $")
merged_plot3.update_layout(xaxis_title="Date")

# Show the plot
merged_plot3.show()

# merge current assets and current liabilities
print(cur_assets_df_filtered)
print(cur_liabilities_df_filtered)
merged_cur_asst_lib_df = pd.merge(cur_assets_df_filtered, cur_liabilities_df_filtered, on=['accn', 'end'], how='inner')
merged_cur_asst_lib_df = merged_cur_asst_lib_df.drop(merged_cur_asst_lib_df.columns[9:], axis=1)
merged_cur_asst_lib_df = merged_cur_asst_lib_df.rename(columns={'val_x': 'current_assets', 'val_y': 'current_liabilities'})
print(merged_cur_asst_lib_df) # 16 rows end 2008-09-27 to 2023-09-30
# print(merged_cur_asst_lib_df.columns)

# get summaries of merged dataframe
desc_merged_cur_asst_lib_df = merged_cur_asst_lib_df.describe()
print(desc_merged_cur_asst_lib_df[['current_assets', 'current_liabilities']])

# what is the liabilities trend?
merged_plot4 = px.line(merged_cur_asst_lib_df,
                      x='end', y=['current_assets', 'current_liabilities'],
                      title="AAPL Current Assets & Current Liabilities")

# Update layout to set x-axis and y-axis title
merged_plot4.update_layout(yaxis_title="Value in $")
merged_plot4.update_layout(xaxis_title="Date")

# Show the plot
merged_plot4.show()

""" Ratios """
# 1. Current ratio = Current Assets / Current Liabilities
# this ratio help us understand the company's finanical strength, how likely the company can meet its' obligations.

merged_cur_asst_lib_df['current_ratio'] = merged_cur_asst_lib_df['current_assets']/ merged_cur_asst_lib_df['current_liabilities']
# print(merged_asst_lib_df)

current_ratio_plot = px.line(merged_cur_asst_lib_df,
                      x='end', y='current_ratio',
                      title="AAPL Current Ratio")
current_ratio_plot.update_yaxes(range=[0, max(merged_cur_asst_lib_df['current_ratio']+1)])

# Update layout to set x-axis and y-axis title
current_ratio_plot.update_layout(yaxis_title="Value in $")
current_ratio_plot.update_layout(xaxis_title="Date")

current_ratio_plot.show()

# 2. Debt-to-Equity Ratio (D/E) = Total liabilities / Total shareholders' Equity
# this ratio help us understand the net worth of the company by comparing the total shareholders' equity to its total liabilities

merged_asst_lib_eq_df['debt_to_equity_ratio'] = merged_asst_lib_eq_df['liabilities']/merged_asst_lib_eq_df['equity']
print(merged_asst_lib_eq_df)
debt_to_equity_ratio_plot = px.line(merged_asst_lib_eq_df,
                      x='end', y='debt_to_equity_ratio',
                      title="AAPL Debt-to-Equity Ratio",
                                    labels={
                                        "debt_to_equity_ratio": "Debt-to-Equity Ratio",
                                        "end": "Date"
                                    })
debt_to_equity_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_df['debt_to_equity_ratio'])])

debt_to_equity_ratio_plot.show()

# 3. Leverage = Total Assets / Total Equity
# Equity multiplier. This tell us the leverage impact of the debt and the increasing business risk

merged_asst_lib_eq_df['leverage_ratio'] = merged_asst_lib_eq_df['assets'] / merged_asst_lib_eq_df['equity']
# print(merged_asst_lib_eq_df)

leverage_ratio_plot = px.line(merged_asst_lib_eq_df,
                      x='end', y='leverage_ratio',
                      title="AAPL Leverage Ratio",
                                    labels={
                                        'leverage_ratio': "Leverage Ratio",
                                        "end": "Date"
                                    })
leverage_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_df['leverage_ratio'])])

leverage_ratio_plot.show()

# 4. Return on Equity = Net Income / Shareholder Equity (ref, https://www.investopedia.com/ask/answers/070914/how-do-you-calculate-return-equity-roe.asp)
# this ratio provides insight into the efficiently of company on managing shareholders' equity. it indicates how much money shareholders make on their investment.

merged_asst_lib_eq_net_df['roe_ratio'] = merged_asst_lib_eq_net_df['revenue'] / merged_asst_lib_eq_net_df['equity']
# print(merged_asst_lib_eq_net_df)

roe_ratio_plot = px.line(merged_asst_lib_eq_net_df,
                      x='end', y='roe_ratio',
                      title="AAPL Return on Equity Ratio",
                                    labels={
                                        'roe_ratio': "Return on Equity Ratio",
                                        "end": "Date"
                                    })
roe_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_eq_net_df['roe_ratio'])])

roe_ratio_plot.show()

print('End of code. Thank you.')
