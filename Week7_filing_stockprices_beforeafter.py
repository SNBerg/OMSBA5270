# -*- coding: utf-8 -*-
"""
Class: OMSBA 5270 01 24 WQ
Author: Sirina Berg
Source : https://www.sec.gov/edgar/sec-api-documentation

Week 7:  Comparative Analysis of Financial Ratios and Stock Prices Using Python
- Select a Publicly Traded Financial Company.
- Choose a Filing Type. Select one type of SEC filing to focus on.
- Data Collection. Filings, Retrieve the dates of your chosen filing type for the past two years. Stock prices, Collect the stock price data of the selected company around the filing dates. Include data from at least one week before and after the filing date to capture any anticipatory or reactive movements.
- Graphical Analysis.
- Analysis and Interpretation. Write a short analysis (100-200 words) discussing your observations

"""

# import modules
import requests
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

# setup display so it shows all columns
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)

# create a request header
headers = {'User-Agent' : "sberg@seattleu.edu"}

# get all companies data
companyTickers = requests.get(f"https://www.sec.gov/files/company_tickers.json", headers=headers)
# print(companyTickers.json()['0']['cik_str'])

# convert to DataFrame
companyCIK = pd.DataFrame.from_dict(companyTickers.json(), orient='index')

# create a short version of the CIK # for building the URL to pull the XML file
# user the original CIK before adding the leading zeros
companyCIK_short = companyCIK['cik_str']
print(companyCIK_short)

print(companyCIK)

companyCIK['cik_str'] = companyCIK['cik_str'].astype(str).str.zfill(10)

print(companyCIK)

# get company cik_str
ticker_symbol = 'MSFT'
cik = companyCIK.loc[companyCIK['ticker'] == ticker_symbol, 'cik_str'].iloc[0]
print(cik) # 0000789019

# SEC filing API call
companyFiling = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers)
print(companyFiling.json()['filings'].keys())

# pull the past filing information, not individual financial information
allFilings = pd.DataFrame.from_dict(companyFiling.json()['filings']['files'])
print(allFilings)
print(allFilings['name'][0]) # CIK0000789019-submissions-001.json

# pull historic data from sec archive. Use the latest filing name
companyFiling_archive = requests.get(f"https://data.sec.gov/submissions/{allFilings['name'][0]}", headers=headers)
print(companyFiling_archive.json())

# convert the sec archive response into a dataframe
allFiling_archive_df= pd.DataFrame.from_dict(companyFiling_archive.json())
print(allFiling_archive_df)

#pull all the unique filing types
uniqueFiling_types = allFiling_archive_df['form'].unique()
print(uniqueFiling_types) 
#['4' '5' '8-K' '10-K' '11-K' 'SD' '10-Q' '3' 'SC 13G/A' '424B2' 'FWP'
 # 'DEFA14A' 'DEF 14A' 'NO ACT' 'PRE 14A' 'CERTNYS' '8-A12B' 'S-3ASR' 'ARS'
 # 'SC 13G' '305B2' 'UPLOAD' 'CORRESP' '3/A' '4/A' 'S-8 POS' '11-K/A'
 # '8-K/A' 'S-8' '10-Q/A' 'SC 13D' 'SC TO-T/A' 'SC TO-T' 'SC TO-C' '425'
 # 'SC TO-I/A' 'SC TO-I']

form_4_filings = allFiling_archive_df[allFiling_archive_df['form'] == '4']
print(form_4_filings)

# # get the last 2 years filing_date
# convert to datetime
form_4_filings['filingDate'] = pd.to_datetime(form_4_filings['filingDate'])
# print(form_4_filings.info())

# find the last date
last_filing_date = form_4_filings['filingDate'][0]
print(last_filing_date)

# find the last 2 years date
two_year_filing_date = last_filing_date - pd.DateOffset(years = 2)
print(two_year_filing_date)

# filter for the last 2 years of filing date
form_4_filings_filtered = form_4_filings[(form_4_filings['filingDate'] >= two_year_filing_date) & (form_4_filings['filingDate'] <= last_filing_date)]
print(form_4_filings_filtered)

# convert filingDate back to str
form_4_filings_filtered['filingDate'] = form_4_filings_filtered['filingDate'].dt.strftime('%Y-%m-%d')
# print(form_4_filings_filtered.info())

######################################
# pull the stock market price based upon the filing date

import yfinance as yf
from datetime import datetime, timedelta

# create empty columns to add stock price before and after
form_4_filings_filtered['stock_price_before'] = 0
form_4_filings_filtered['stock_price_after'] = 0

# loop through each filing date to get stock prices around those filing dates
for index, row in form_4_filings_filtered.iterrows():
    value = row['filingDate']
    print(value)

    # get start and end date before the filing date
    start_date_before = datetime.strptime(value, '%Y-%m-%d') # convert filing date str to datetime
    start_date_before = start_date_before - timedelta(weeks=1) # start date is 1 week date before the filing date
    start_date_str_before = start_date_before.strftime('%Y-%m-%d') # convert datetime back to str
    
    end_date_str_before = value # end date is the date of filing
    # print(start_date_before, end_date_str_after)

    # get start and end date after the filing date
    start_date_str_after = value # start date is the date of filing
    start_date_after = datetime.strptime(start_date_str_after, '%Y-%m-%d') # convert to datetime
    
    end_date_after = start_date_after + timedelta(weeks=1) # get end date 1 week after the filed date
    end_date_str_after = end_date_after.strftime('%Y-%m-%d') # convert end date back to str to feed to yfinance
    # print(start_date_after, end_date_after)

    # create a y finance ticker object
    ticker = yf.Ticker(ticker_symbol)

    # pull yfinance historical data
    historical_data_before = ticker.history(period='1d', start=start_date_str_before, end=end_date_str_before)
    historical_data_after = ticker.history(period='1d', start=start_date_str_after, end=end_date_str_after)

    # create historical dataframe
    historical_df_before = pd.DataFrame(historical_data_before)   
    historical_df_after = pd.DataFrame(historical_data_after)
    # print(historical_df_before, historical_df_after)
    
    # need the first row of the closing date
    specific_data_before = historical_data_before.iloc[0]['Close'] 
    specific_data_after = historical_data_after.iloc[0]['Close'] 
    print(specific_data_before, specific_data_after)
    
    # store the specific date data in the dataframe
    form_4_filings_filtered.at[index,'stock_price_before'] = specific_data_before
    form_4_filings_filtered.at[index,'stock_price_after'] = specific_data_after   


print(form_4_filings_filtered)

import plotly.express as px
import plotly

# graph filings date vs stock price
pd.options.plotting.backend = 'plotly'
graph = form_4_filings_filtered.plot(x='filingDate', y=['stock_price_before', 'stock_price_after'],
                            title=f'MSFT Stock Price vs Filing Date for {ticker_symbol}',                            
                            )
graph.update_layout(yaxis_title="Stock Price")
graph.update_layout(xaxis_title="Filing Date")
graph.update_layout(legend=dict(x=0.02, y=0.98, xanchor='left', yanchor='top'))
plotly.offline.plot(graph)

