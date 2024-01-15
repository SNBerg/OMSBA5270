"""
Class: OMSBA 5270 01 24 WQ
Author: Sirina Berg
Source : https://www.sec.gov/edgar/sec-api-documentation
"""

# import modules

import requests
import pandas as pd

# create a request header
# using seattlu accoun to identify me as a user who makes a request

headers = {'User-Agent' : "sberg@seattleu.edu"}

# get all companies data from the company_tickers.json
# this will return a set of dictionary with cik_str (cik number), ticker (company symbol), title (company name)
# for example {'0': {'cik_str': 320193, 'ticker': 'AAPL', 'title': 'Apple Inc.'}, '1': {'cik_str': 789019, 'ticker': 'MSFT', 'title': 'MICROSOFT CORP'},...

companyTickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
print(companyTickers.json())


# put it into the dataframe
# note, input cik_str has no leading zeros

companyCIK = pd.DataFrame.from_dict(companyTickers.json(), orient='index')
print(companyCIK)

# Per SEC document, need to add leading zeros to the cik_str (Cetnral Index Key). It is requird to be a 10-digit key.

companyCIK['cik_str'] = companyCIK['cik_str'].astype(str).str.zfill(10)
print(companyCIK)

# check cik_str in the first index key

cik = companyCIK[0:1].cik_str[0]
print(cik)

cik = companyCIK[0:2].ticker[1]
print(cik)

# try search by company symbol and get cik number to use later, store it in cik variable

search_comp = 'MSFT'

cik_str_result = companyCIK.loc[companyCIK['ticker'] == search_comp, 'cik_str'].iloc[0]
cik = str(cik_str_result).zfill(10)
print(cik)

"""
data.sec.gov/submissions/
Each entity’s current filing history is available at the following URL:

https://data.sec.gov/submissions/CIK##########.json
"""

# check what data is available for us in the submission endpoint
# replace the ########## with cik number from above

companyFiling = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers)
print(companyFiling.json())

# check what data is available for us in the submission endpoint
# replace the ########## with cik number from above

companyFiling = requests.get(f"https://data.sec.gov/submissions/CIK{cik}.json", headers=headers)
print(companyFiling.json())

# inspect data under the filings key
print(companyFiling.json()['filings'].keys())

# more dictionary under 'recent' e.g. accessionNumber, filingDate, reportDate,..., form, etc
print(companyFiling.json()['filings']['recent'].keys())

# Explore data in the filing's recent
print(companyFiling.json()['filings']['recent'])

# create a dataframe for all filing in recent

allFilings = pd.DataFrame.from_dict(companyFiling.json()['filings']['recent'])
print(allFilings)

# zoom in to see a row of data
#allFilings.iloc[1]

"""
Exploring company facts
data.sec.gov/api/xbrl/companyfacts/
This API returns all the company concepts data for a company into a single API call:

https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json

create dataframe for all data 
1. Assets
2. Revenues
3. AssetsCurrent
4. AccountsPayableCurrent
5. LiabilitiesCurrent
"""

# make a call to get data from companyFacts endpoint
companyFacts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=headers)

# print(companyFacts.json())
print(companyFacts.json().keys())
# dict_keys(['cik', 'entityName', 'facts'])

# Explore facts data
# this returns tons of data
print(companyFacts.json()['facts'])

# check the keys in the facts
print(companyFacts.json()['facts'].keys())
# result: dict_keys(['dei', 'us-gaap'])

# explore the keys in each one to see what in there
print(companyFacts.json()['facts']['dei'].keys())
# result: dict_keys(['EntityCommonStockSharesOutstanding', 'EntityListingParValuePerShare', 'EntityPublicFloat'])

print(companyFacts.json()['facts']['us-gaap'].keys())
# sample result: dict_keys(['AccountsPayableCurrent', 'AccountsReceivableNet', 'AccountsReceivableNetCurrent', 'AccountsReceivableNetNoncurrent', 'AccruedIncomeTaxesCurrent', 'AccruedIncomeTaxesNoncurrent', 'AccumulatedDepreciationDepletionAndAmortizationPropertyPlantAndEquipment', 'AccumulatedOtherComprehensiveIncomeLossAvailableForSaleSecuritiesAdjustmentNetOfTax', 'AccumulatedOtherComprehensiveIncomeLossCumulativeChangesInNetGainLossFromCashFlowHedgesEffectNetOfTax', 'AccumulatedOtherComprehensiveIncomeLossForeignCurrencyTranslationAdjustmentNetOfTax', 'AccumulatedOtherComprehensiveIncomeLossNetOfTax', 'AcquiredFiniteLivedIntangibleAssetAmount', 'AcquiredFiniteLivedIntangibleAssetWeightedAverageUsefulLife', 'AdvertisingExpense', 'AllocatedShareBasedCompensationExpense', 'AllowanceForDoubtfulAccountsReceivableCurrent', 'AmortizationOfIntangibleAssets', 'AntidilutiveSecuritiesExcludedFromComputationOfEarningsPerShareAmount', 'AssetImpairmentCharges', 'Assets', 'AssetsCurrent',
# e.g. 'Assets', 'AssetsCurrent', 'Revenues', , 'AccountsPayableCurrent', 'AccruedLiabilitiesCurrent', etc.

""" Data Exploration """
# 1. Assets data
print(companyFacts.json()['facts']['us-gaap']['Assets'])
print(companyFacts.json()['facts']['us-gaap']['Assets'].keys())
# result: dict_keys(['label', 'description', 'units'])

print(companyFacts.json()['facts']['us-gaap']['Assets']['description'])
# result: Sum of the carrying amounts as of the balance sheet date of all assets that are recognized.
# Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.

print(companyFacts.json()['facts']['us-gaap']['Assets']['units'])
# result: {'USD': [{'end': '2009-06-30', 'val': 77888000000, 'accn': '0001193125-09-212454', 'fy': 2010, 'fp': 'Q1', 'form': '10-Q', 'filed': '2009-10-23'},
# {'end': '2009-06-30', 'val': 77888000000, 'accn': '0001193125-10-015598', 'fy': 2010, , ...

print(companyFacts.json()['facts']['us-gaap']['Assets']['units']['USD'][0])
# result: {'end': '2009-06-30', 'val': 77888000000, 'accn': '0001193125-09-212454', 'fy': 2010, 'fp': 'Q1', 'form': '10-Q', 'filed': '2009-10-23'}

# restructure data to Panda's dataframe
assetsDF = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Assets']['units']['USD'])
print(assetsDF)
# notes, have some NaN in the frame

# checking what forms are in here
print(assetsDF.form)
# have form 10-Q and 10-k

# filter for form 10-k and filed year from 2013 (10 years data)
# print(assetsDF['filed'].unique())
assets2013 = assetsDF[assetsDF['filed'] >= '2013-07-30']
#print(assets2013['form'].unique())
assets10k2013 = assets2013[assets2013['form'] == '10-K']
#print(assets10k2013.form)

# reorder the index
assets10k2013 = assets10k2013.reset_index(drop=True)

# 2. Revenues data
print(companyFacts.json()['facts']['us-gaap']['Revenues'])
print(companyFacts.json()['facts']['us-gaap']['Revenues'].keys())
# result: dict_keys(['label', 'description', 'units'])

print(companyFacts.json()['facts']['us-gaap']['Revenues']['description'])
# result: Amount of revenue recognized from goods sold, services rendered, insurance premiums, or other activities that constitute an earning process. Includes, but is not limited to,
# investment and interest income before deduction of interest expense when recognized as a component of revenue,
# and sales and trading gain (loss).

print(companyFacts.json()['facts']['us-gaap']['Revenues']['units']['USD'][0])
# result: {'start': '2007-07-01', 'end': '2007-09-30', 'val': 13762000000, 'accn': '0001193125-10-171791', 'fy': 2010, 'fp': 'FY', 'form': '10-K', 'filed': '2010-07-30', 'frame': 'CY2007Q3'}

# restructure data to Panda's dataframe
revenuesDF = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['Revenues']['units']['USD'])
print(revenuesDF)
# notes, have some NaN in the frame

# filter for form 10-k and filed year from 2013 (10 years data)
# print(revenuesDF['filed'].unique())
# notes, limited dataset. ['2010-07-30' '2009-10-23' '2010-01-28' '2010-04-22' '2010-10-28' '2011-01-27']

#print(assets2013['form'].unique())
revenues10k = revenuesDF[revenuesDF['form'] == '10-K']
print(revenues10k)

# reorder the index
revenues10k = revenues10k.reset_index(drop=True)

# 3. AssetsCurrent data
print(companyFacts.json()['facts']['us-gaap']['AssetsCurrent'])
print(companyFacts.json()['facts']['us-gaap']['AssetsCurrent'].keys())
# result: dict_keys(['label', 'description', 'units'])

print(companyFacts.json()['facts']['us-gaap']['AssetsCurrent']['description'])
# result: Sum of the carrying amounts as of the balance sheet date of all assets that are expected to be realized in cash, sold,
# or consumed within one year (or the normal operating cycle, if longer).
# Assets are probable future economic benefits obtained or controlled by an entity as a result of past transactions or events.

#print(companyFacts.json()['facts']['us-gaap']['AssetsCurrent']['units'].keys())
# result: dict_keys(['USD'])
print(companyFacts.json()['facts']['us-gaap']['AssetsCurrent']['units']['USD'][0])
# result: {'end': '2009-06-30', 'val': 49280000000, 'accn': '0001193125-09-212454', 'fy': 2010, 'fp': 'Q1', 'form': '10-Q', 'filed': '2009-10-23'}

# restructure data to Panda's dataframe
assetsCurDF = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['AssetsCurrent']['units']['USD'])
print(assetsCurDF)
# notes, have some NaN in the frame

# checking what forms are in here
print(assetsCurDF['form'].unique())
# have form ['10-Q' '10-K' '10-Q/A' '8-K']

# filter for form 10-k and filed year from 2013 (10 years data)
print(assetsCurDF['filed'].unique())
# notes, data filed from '2009-10-23'-'2023-10-24'

# print(assetsCurDF['form'].unique())
# ['10-Q' '10-K' '10-Q/A' '8-K']

assetsCur2013 = assetsCurDF[assetsCurDF['filed'] >= '2013-07-30']
# print(assetsCur2013)
assetsCur10k2013 = assetsCur2013[assetsCur2013['form'] == '10-K']
print(assetsCur10k2013)

# reorder the index
assetsCur10k2013 = assetsCur10k2013.reset_index(drop=True)

# 4. AccountsPayableCurrent data
print(companyFacts.json()['facts']['us-gaap']['AccountsPayableCurrent'])
print(companyFacts.json()['facts']['us-gaap']['AccountsPayableCurrent'].keys())
# result: dict_keys(['label', 'description', 'units'])

print(companyFacts.json()['facts']['us-gaap']['AccountsPayableCurrent']['description'])
# result: Carrying value as of the balance sheet date of liabilities incurred (and for which invoices have typically been received)
# and payable to vendors for goods and services received that are used in an entity's business.
# Used to reflect the current portion of the liabilities (due within one year or within the normal operating cycle if longer).

print(companyFacts.json()['facts']['us-gaap']['AccountsPayableCurrent']['units']['USD'][0])
# result: {'end': '2009-06-30', 'val': 3324000000, 'accn': '0001193125-09-212454', 'fy': 2010, 'fp': 'Q1', 'form': '10-Q', 'filed': '2009-10-23'}

# restructure data to Panda's dataframe
acctPayCurDF = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['AccountsPayableCurrent']['units']['USD'])
print(acctPayCurDF)
# notes, have some NaN in the frame

# checking what forms are in here
#print(acctPayCurDF['form'].unique())
# have form ['10-Q' '10-K' '10-Q/A' '8-K']
#print(acctPayCurDF['filed'].unique())
# note, filed date between '2009-10-23'-'2023-10-24'

# filter for form 10-k and filed year from 2013 (10 years data)
acctPayCur2013 = acctPayCurDF[acctPayCurDF['filed'] >= '2013-07-30']
# print(assetsCur2013)
acctPayCur10k2013 = acctPayCur2013[acctPayCur2013['form'] == '10-K']
#print(assetsCur10k2013['form'].unique())

# reorder the index
acctPayCur10k2013 = acctPayCur10k2013.reset_index(drop=True)

# 5. LiabilitiesCurrent data
print(companyFacts.json()['facts']['us-gaap']['LiabilitiesCurrent'])
print(companyFacts.json()['facts']['us-gaap']['LiabilitiesCurrent'].keys())

print(companyFacts.json()['facts']['us-gaap']['LiabilitiesCurrent']['description'])
# result: Total obligations incurred as part of normal operations that are expected to be paid during the following twelve months
# or within one business cycle, if longer.

print(companyFacts.json()['facts']['us-gaap']['LiabilitiesCurrent']['units']['USD'][0])
# result: {'end': '2009-06-30', 'val': 27034000000, 'accn': '0001193125-09-212454', 'fy': 2010, 'fp': 'Q1', 'form': '10-Q', 'filed': '2009-10-23'}

# restructure data to Panda's dataframe
liabCurDF = pd.DataFrame.from_dict(companyFacts.json()['facts']['us-gaap']['LiabilitiesCurrent']['units']['USD'])
print(liabCurDF)

# checking what forms are in here
# print(liabCurDF['form'].unique())
# have form ['10-Q' '10-K' '10-Q/A' '8-K']
# print(liabCurDF['filed'].unique())
# note, filed date between '2009-10-23'-'2023-10-24'

# filter for form 10-k and filed year from 2013 (10 years data)
liabCurDF2013 = liabCurDF[liabCurDF['filed'] >= '2013-07-30']
# print(assetsCur2013)
liabCurDF10k2013 = liabCurDF2013[liabCurDF2013['form'] == '10-K']
#print(liabCurDF10k2013['form'].unique())

# reorder the index
liabCurDF10k2013 = liabCurDF10k2013.reset_index(drop=True)
