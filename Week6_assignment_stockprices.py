'''
Class: OMSBA 5270 01 24 WQ
Author: Sirina Berg
Source : https://www.sec.gov/edgar/sec-api-documentation

Week 6: 
'''
import requests
import pandas as pd
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta

import plotly.io as pio
pio.renderers.default = "svg" # default to plot in the plot pane

# setup display so it shows all columns
pd.options.display.width= None
pd.options.display.max_columns= None
pd.set_option('display.max_rows', 3000)
pd.set_option('display.max_columns', 3000)

pd.options.plotting.backend = 'plotly'

# function to get cik_str for the selected company
def search_comp(ticker):
    return(companyCIK.loc[companyCIK['ticker'] == ticker, 'cik_str'].iloc[0])

# API call 

# create a request header
headers = {'User-Agent':"sberg@seattleu.edu"}

# get all companies data
companyTickers = requests.get(f"https://www.sec.gov/files/company_tickers.json", headers=headers)
# print(companyTickers.json())

companyCIK = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
# print(companyCIK)

# adding leading 0s
companyCIK['cik_str'] = companyCIK['cik_str'].astype(str).str.zfill(10)
print(companyCIK)

ticker_symbol = 'AAPL'
# get the first company
cik = search_comp(ticker_symbol)
print(cik) #MSFT 0000789019 APPL 0000320193 COST 0000909832 KR 0000056873
print(companyCIK[companyCIK['cik_str']==cik]) #0  0000789019   MSFT  MICROSOFT CORP

# get index for 
comp_index = companyCIK.loc[companyCIK['cik_str'] == cik].index[0] 
print(comp_index)

companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)

revenues_df = pd.DataFrame(companyFacts.json()['facts']['us-gaap']['Revenues']['units']['USD'])
print(revenues_df)

graph = revenues_df.plot(x='end', y='val',
                        title=f"MSFT revenues",
                        labels = {
                            "val": "Value in $",
                            "end": "Quater End Date"
                        })
graph.show()

# start date for the api call
start_date_str = '2010-07-30' # first filted date

# convert str to datetime
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

# calculate the delta
end_date = start_date + timedelta(days=30) # get end date 30 day after the filed date

# convert end date back to str to feed to yfinance
end_date_str = end_date.strftime('%Y-%m-%d')
print(end_date, end_date_str)

# create a y finance ticker object
ticker = yf.Ticker(ticker_symbol)

# pull yfinance historical data
historical_data = ticker.history(period='id', start=start_date_str)

# create historical dataframe
historical_df = pd.DataFrame(historical_data)
print(historical_df)

# create empty column to add stock price 
revenues_df['closing_stock_price'] = 0

for index, row in revenues_df.iterrows():
    value = row['filed']
    
    # get tickers symbol
    ticker_symbol = companyCIK['ticker'][0]
    # print(ticker_symbol)

    # start date for the api call
    start_date_str = '2010-07-30' # first filted date

    # convert str to datetime
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    # calculate the delta
    end_date = start_date + timedelta(days=30) # get end date 30 day after the filed date

    # convert end date back to str to feed to yfinance
    end_date_str = end_date.strftime('%Y-%m-%d')
    # print(end_date, end_date_str)

    # create a y finance ticker object
    ticker = yf.Ticker(ticker_symbol)

    # pull yfinance historical data
    historical_data = ticker.history(period='id', start=start_date_str)

    # create historical dataframe
    historical_df = pd.DataFrame(historical_data)
    
    # need the first row of the closing date
    specific_data = historical_data.iloc[0]['Close'] 
    
    revenues_df.at[index,'stock_price'] = specific_data
    
    print(specific_data)
    
print(revenues_df)
    




