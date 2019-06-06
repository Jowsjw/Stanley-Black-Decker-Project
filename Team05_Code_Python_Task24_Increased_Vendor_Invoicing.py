# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 09:35:20 2018

@author: ltt's pc
"""
# import the modules
import pandas as pd
from itertools import product
from datetime import timedelta
import math
import numpy as np
# Read files into python
BSAK_BKPF = pd.read_csv('BSAK_BKPF_AltColTitles.CSV',dtype='str')
T001 = pd.read_csv('T001_AltColTitles.CSV',dtype='str')
LFA1 = pd.read_csv('LFA1_AltColTitles.CSV',dtype='str')

# Join tables
BSAK_BKPF = BSAK_BKPF.loc[BSAK_BKPF['Document_Type'].isin(['KZ', 'ZP'])==False]
T001['Company_Code'] = T001['Company_Code'].astype('str')
df_invoice = pd.merge(BSAK_BKPF, T001, on='Company_Code',suffixes=['BSAK','T001'])
invoice = pd.merge(df_invoice, LFA1, on='Account_Number_of_Vendor_or_Creditor', suffixes=['BSAK','LFA1'])

# Subset the data that could be useful for #24
df = invoice[['Company_Code'
        ,'Name_of_Company_Code_or_Company'
        , 'Account_Number_of_Vendor_or_Creditor'
        ,'Debit_Credit_Indicator'
        , 'Amount_in_Local_Currency'
        ,'Amount_in_Document_Currency'
        , 'Currency_KeyT001'
        ,'Currency_KeyBSAK'
        ,'Reference_Document_Number'
        ,'Document_Date_in_Document'
        ]]


# Convert dates to the datatime 
df['Document_Date_in_Document'] = pd.to_datetime(df['Document_Date_in_Document'])
# Sort the table first by Account_Number_of_Vendor_or_Creditor, and then Document_Date_in_Document
df = df.sort_values(by=['Account_Number_of_Vendor_or_Creditor','Document_Date_in_Document'])

# For natural periods
df.loc[:,'Year'] = df['Document_Date_in_Document'].dt.year
df.loc[:,'Quarter'] = df['Document_Date_in_Document'].dt.quarter
df.loc[:,'Month'] = df['Document_Date_in_Document'].dt.month
df.loc[:,'Week'] = df['Document_Date_in_Document'].dt.week

# For a user defined days
n_days = input('Enter the day range you want to check: ')
n_days=int(n_days)
# get the number of periods
end = df['Document_Date_in_Document'].max()
start = df['Document_Date_in_Document'].min()
df.loc[:,'user_defined_period'] = 0
total_days = end - start
total_days=total_days.days+1
periods = math.ceil(total_days/n_days)
# set a range
rng = pd.date_range(start, periods=periods,freq= str(n_days)+'D') #rng is range
#calculate the period for each date and store it in df
n = 0
for i in rng:    
    start_date = i
    end_date = i + timedelta(days=n_days) 
    mask = (df['Document_Date_in_Document'] >= start_date) & (df['Document_Date_in_Document'] < end_date)
    n += 1
    df.loc[mask,'user_defined_period'] = n
# Create list for all occurences in the data. This is used to flag vendors without invoice activity for certain period
lperiods = df['user_defined_period'].unique().tolist()
lvendor = df['Account_Number_of_Vendor_or_Creditor'].unique().tolist()
lyear = df['Year'].unique().tolist()
lquarter = df['Quarter'].unique().tolist()
lmonth = df['Month'].unique().tolist()
lweek = df['Week'].unique().tolist()
# The variables to be aggregate
agg_dict = {'Reference_Document_Number': 'count'
            ,'Amount_in_Local_Currency': 'sum'}




# Now all the variables are ready to be used
# The things you may want to change-------------------------------------------------------start
# Use month as a example
# The variables you want to groupby is in the grouper_list you can change it to year, quarter, or user_defined_period
grouper_list = ['Account_Number_of_Vendor_or_Creditor','Year','Month']
# product list is used to create a table of all occurences in the df, and to flag those vendor without invoice activity
# put an 'l' before the period in the product_list
product_list = [lvendor, lyear, lmonth]
# The things you may want to change--------------------------------------------------------end





# group the df using grouper_list
group = pd.DataFrame(df.groupby(grouper_list).agg(agg_dict))
group.reset_index(inplace=True)

# For a given vendor there could be no records in that period
# Create a table of all combinations
full =pd.DataFrame(list(product(*product_list)), columns=grouper_list)
# Calculate each vendor's frequency of invoice and total amounts
result = pd.merge(full, group, how='left', on=grouper_list)
result = result.sort_values(by=grouper_list)


# Flag the period of the vendor without activity and store the result in a new column
result.loc[:,'no_invoice_flag'] = result['Reference_Document_Number'].isnull()


# Calculate the pct use the last available invoice count and store it as pct_last
result.loc[:,'pct_last'] = result.groupby(grouper_list[:-1])['Reference_Document_Number'].pct_change()
# Calculate the pct and use null values for the period of the vendor without activity and store it as pct
result.loc[:,'calc'] = result['Reference_Document_Number'].fillna(0.0000000000001)
result.loc[:, 'pct'] = result.groupby(grouper_list[:-1])['calc'].pct_change()
result.loc[:, 'pct'] = (result['pct']+result['pct_last'])/2
result.loc[result['pct']>1000000000, 'pct'] = np.nan
result = result.drop('calc', axis=1)

# A user defined variable for frequency change threshold the output file with only contains rows exceeds the threshold
threshold = input('Enter a X%: ')
threshold = float(threshold)

#Output the result in print in console and an csv file
print(result[result['pct']>(threshold/100)])

result.to_csv('result_pct.csv',index=False)
print('Output file is in the workdir, please check')
