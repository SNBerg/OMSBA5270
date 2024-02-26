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
import plotly.express as px
from tabulate import tabulate # to create ratio tables
import plotly.graph_objects as go # for combo chart
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
    dffiltered = df[df['form'] == form]
    dffiltered = dffiltered.reset_index(drop=True)
    # print(dffiltered)
    
    # exploring data
    print(df.info())
    print(df.count(), min(df['end']), max(df['end']))

    return(df, dffiltered)

# get revenues data
"""
RevenueFromContractWithCustomerExcludingAssessedTax
Amount, excluding tax collected from customer, of revenue from satisfaction of performance obligation by transferring promised good or service to customer.
Tax collected from customer is tax assessed by governmental authority that is both imposed on and concurrent with specific revenue-producing transaction, 
including, but not limited to, sales, use, value added and excise.
"""

#revenue_df, revenue_df_filtered = getdata('RevenueFromContractWithCustomerExcludingAssessedTax', '10-K')
revenue_df, revenue_df_filtered = getdata('Revenues', '10-K')

# observation: no null data, 288 rows start date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# has data both in annual and quarterly, has NaN in frame column - need to clean up

# get Assets and convert the facts on assets to a dataframe
"""
Assets 
Sum of the carrying amounts as of the balance sheet date of all assets that are recognized. 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
assets_df, assets_df_filtered = getdata('Assets', '10-K')

# observation: no null data, 288 rows start date between 2008-08-31 - 2023-11-26 - need to align period with other data points
# has data both in annual and quarterly, has NaN in frame column - need to clean up

# get current assets
"""
AssetsCurrent
Sum of the carrying amounts as of the balance sheet date of all assets that are expected to be realized in cash, sold, or consumed within one year (or the normal operating cycle, if longer). 
Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.
"""
cur_assets_df, cur_assets_df_filtered = getdata('AssetsCurrent', '10-K')

# get liabilities data and convert the facts on assets to a dataframe
"""
Liabilities
Sum of the carrying amounts as of the balance sheet date of all liabilities that are recognized. 
Liabilities are probable future sacrifices of economic benefits arising from present obligations of an entity to transfer assets 
or provide services to other entities in the future.
"""
liabilities_df, liabilities_df_filtered = getdata('Liabilities', '10-K')

# get current liabilities
"""
LiabilitiesCurrent
Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months or within one business cycle, if longer.
"""
cur_liabilities_df. cur_libilities_df_filtered = getdata('LiabilitiesCurrent', '10-K') 

# get stockholders' equity
"""
StockholdersEquity
Total of all stockholders' equity (deficit) items, net of receivables from officers, directors, owners, and affiliates of the entity which are attributable to the parent.
The amount of the economic entity's stockholders' equity attributable to the parent excludes the amount of stockholders' equity 
which is allocable to that ownership interest in subsidiary equity which is not attributable to the parent (noncontrolling interest, minority interest). 
This excludes temporary equity and is sometimes called permanent equity.
"""
equity_df, equity_df_filtered = getdata('StockholdersEquity', '10-K') 

# get net income
"""
NetIncomeLossLoss
The portion of profit or loss for the period, net of income taxes, which is attributable to the parent.
"""
netincome_df, netincome_df_filtered = getdata('NetIncomeLoss', '10-K') 