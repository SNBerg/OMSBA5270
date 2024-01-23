"""
Class: OMSBA 5270 01 24 WQ
Author: Sirina Berg
Source : https://www.sec.gov/edgar/sec-api-documentation
Week 4 Graphing SEC API Call and EDA
- Conduct statistical summaries, averages, mean, modes, etc
- Create visualizations (like histograms, scatter plots, or line graphs)
- Calculate 3 ratios such as Price-to-Earnings (P/E), Debt-to-Equity (D/E), Return on Equity (ROE), and others using the EDGAR API data
"""

import requests
import pandas as pd
import plotly.express as px

# setup display so it shows all columns
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

pd.options.plotting.backend = 'plotly'

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

# get first company key cik_str
cik = companyCIK[0:1].cik_str[0]
# print(cik) #0000320193

"""
EDA
Exploring company facts
data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:

https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
"""

companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)
# print(companyFacts.json().keys()) #dict_keys(['cik', 'entityName', 'facts'])
# print(companyFacts.json()['facts'])
# print(companyFacts.json()['facts'].keys()) # dict_keys(['dei', 'us-gaap'])
# print(companyFacts.json()['facts']['us-gaap'].keys())
# print(companyFacts.json()['facts']['us-gaap']['Revenues'].keys()) # dict_keys(['label', 'description', 'units'])
# print(companyFacts.json()['facts']['us-gaap']['Revenues']['units'])

# get revenues data
revenue_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Revenues']['units']['USD'])
revenue_df = revenue_df.sort_values(by=['start'])
# print(revenue_df) # 11 rows star date between 2015-09-27-2018-07-01
# frame appears to show calendar year period however this column has na

# remove na
revenue_df = revenue_df[revenue_df.frame.notna()]
# print(revenue_df.columns) #Index(['start', 'end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(revenue_df['form'].unique()) # has only ['10-K']

# convert the facts on assets to a dataframe
assets_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Assets']['units']['USD'])

# sort data by filed date
assets_df = assets_df.sort_values(by='filed')

# check data to understand what accn column contain
# assets_df = assets_df.sort_values(by=['accn', 'end'])
# print(assets_df) # 124 rows end 2008-09-27-2023-09-30
# print(assets_df.iloc[0])

# remove na
assets_df = assets_df[assets_df.frame.notna()]
# print(assets_df) # 59 rows end 2008-09-27-2023-09-30
# print(assets_df.columns) # Index(['end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(assets_df['form'].unique()) # has multiple form ['10-K' '10-Q' '8-K']

curassets_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['AssetsCurrent']['units']['USD'])
print(curassets_df)

# pull liabilities to filter and later merge
# convert the facts on assets to a dataframe
liabilities_df = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Liabilities']['units']['USD'])
liabilities_df = liabilities_df.sort_values(by='filed')
# print(liabilities_df) # 122 rows end 2008-09-27-2023-09-30

# remove na
liabilities_df = liabilities_df[liabilities_df.frame.notna()]
# print(liabilities_df)
# print(liabilities_df.columns) # Index(['start', 'end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame'], dtype='object')
# print(liabilities_df['form'].unique()) # has multiple form ['10-K/A' '10-Q' '10-K' '8-K']

# filter for only 10-k
assets_df_filtered = assets_df[assets_df['form'] == '10-K']
# print(assets_df_filtered)
# print(assets_df_filtered.count()) # 14 rows
# print(assets_df_filtered['form'].unique()) # return ['10-K']

liabilities_df_filtered = liabilities_df[liabilities_df['form'] == '10-K']
# print(liabilities_df_filtered)
# print(liabilities_df_filtered.count()) # 13 rows
# print(liabilities_df_filtered['form'].unique()) # return ['10-K']

""" Summary and graph"""
desc_assets = assets_df_filtered.describe()
print(desc_assets['val'])

# what is the assets trend?
assets_plot = px.line(assets_df_filtered,
                      title=f"APPL Assets",
                      x="end",
                      y="val")
assets_plot.show()

# what is the liabilities trend?
liabilities_plot = px.line(liabilities_df_filtered,
                      title=f"APPL Liabilities",
                      x="end",
                      y="val")
liabilities_plot.show()

# merge assets and liabilities using accn column
merged_asst_lib_df = pd.merge(assets_df_filtered, liabilities_df_filtered, on='accn')
merged_asst_lib_df = merged_asst_lib_df.drop(merged_asst_lib_df.columns[10:], axis=1)
# print(merged_asst_lib_df) # 16 rows
# print(merged_asst_lib_df.columns)
# return Index(['end_x', 'val_x', 'accn', 'fy_x', 'fp_x', 'form_x', 'filed_x',
#        'frame_x', 'end_y', 'val_y'], dtype='object')

# get summaries of merged dataframe
desc_merged_asst_lib_df = merged_asst_lib_df.describe()
print(desc_merged_asst_lib_df[['val_x', 'val_y']])
print(assets_df_filtered.mode(dropna=False))
print(liabilities_df_filtered.mode(dropna=False))

merged_asst_lib_df = merged_asst_lib_df.rename(columns={'val_x': 'assets', 'val_y': 'liabilities'})
print(merged_asst_lib_df)

# what is the liabilities trend?
merged_plot = px.line(merged_asst_lib_df,
                      x='end_x', y=['assets', 'liabilities'],
                      title="APPL Assets & Liabilities")

# Update layout to set x-axis and y-axis title
merged_plot.update_layout(yaxis_title="Value in $")
merged_plot.update_layout(xaxis_title="Date")

# Show the plot
merged_plot.show()

# merged_rev_asst_lib_df = pd.merge(revenue_df, merged_asst_lib_df, on='accn')
# print(merged_rev_asst_lib_df)
# print(merged_rev_asst_lib_df.columns)
# return Index(['start', 'end', 'val', 'accn', 'fy', 'fp', 'form', 'filed', 'frame',
#        'end_x', 'val_x', 'fy_x', 'fp_x', 'form_x', 'filed_x', 'frame_x',
#        'end_y', 'val_y'], dtype='object')

# get summaries of merged dataframe
# desc_merged_df = merged_rev_asst_lib_df.describe()
# print(desc_merged_df[['val', 'val_x','val_y']])

""" Ratios """
# 1. Current ratio = Current Assets / Current Liabilities

# print(merged_asst_lib_df)
# print(merged_asst_lib_df.iloc[-1])

merged_asst_lib_df['current_ratio'] = merged_asst_lib_df['assets']/ merged_asst_lib_df['liabilities']
# print(merged_asst_lib_df)

current_ratio_plot = px.line(merged_asst_lib_df,
                      x='end_x', y='current_ratio',
                      title="APPL Current Ratio")
current_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_df['current_ratio']+1)])
current_ratio_plot.show()

# 2. Debt-to-Equity Ratio (D/E) = Total Debt / Total Equity
merged_asst_lib_df['total_equity'] = merged_asst_lib_df['assets'] - merged_asst_lib_df['liabilities']
# print(merged_asst_lib_df)
merged_asst_lib_df['debt_to_equity_ratio'] = merged_asst_lib_df['liabilities']/merged_asst_lib_df['total_equity']

debt_to_equity_ratio_plot = px.line(merged_asst_lib_df,
                      x='end_x', y='debt_to_equity_ratio',
                      title="APPL Debt-to-Equity Ratio",
                                    labels={
                                        "debt_to_equity_ratio": "Debt-to-Equity Ratio",
                                        "end_x": "Date"
                                    })
debt_to_equity_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_df['debt_to_equity_ratio']+1)])

debt_to_equity_ratio_plot.show()

# 3. Leverage = Total Assets / Total Equity
merged_asst_lib_df['leverage_ratio'] = merged_asst_lib_df['assets'] / merged_asst_lib_df['total_equity']
# print(merged_asst_lib_df)

leverage_ratio_plot = px.line(merged_asst_lib_df,
                      x='end_x', y='leverage_ratio',
                      title="APPL Leverage Ratio",
                                    labels={
                                        'leverage_ratio': "Leverage Ratio",
                                        "end_x": "Date"
                                    })
leverage_ratio_plot.update_yaxes(range=[0, max(merged_asst_lib_df['leverage_ratio'])])

leverage_ratio_plot.show()


