# -*- coding: utf-8 -*-
"""
Created on Sat Sep 08 20:00:51 2018
@author: Huaxuan Huang
Task #14 Duplicate Purchase Order in Certain Time Period (User Input Values)
"""

import pandas as pd

#Change the format of the EKPO_EKKO Table
with open('EKPO_EKKO_AltColTitlesAltDelimiter2.csv', 'r') as infile, open('noquotes.csv', 'w') as outfile:
    temp = infile.read().replace("'", "")
    outfile.write(temp)

EKPOEKKO = pd.read_csv('noquotes.CSV',sep='|', encoding='latin-1',low_memory=False)
#Add Column Names according to the old version of the data
EKPOEKKO.columns=['Client','Purchasing_Document_Number','Item_Number_of_Purchasing_Document','Deletion_Indicator_in_Purchasing_Document','Purchasing_Document_Item_Change_Date','Short_Text','Material_Number','Company_Code','Plant','Purchase_Order_Quantity','Net_Price_in_Purchasing_Document__in_Document_Currency_','Net_Order_Value_in_PO_Currency','Delivery_Completed_Indicator','Final_Invoice_Indicator','Item_Category_in_Purchasing_Document','Goods_Receipt_Indicator','Date_of_Price_Determination','Purchasing_Document_Category','Customer','Profit_Center','Purchase_Requisition_Number','Client2','Purchasing_Document_Number2','Company_Code2','Purchasing_Document_Category2','Purchasing_Document_Type','Vendor_Account_Number','Currency_Key','Purchasing_Document_Date']
EKPOEKKO.head(10)
#Drop duplicated columns
EKPOEKKO=EKPOEKKO.drop(['Client2','Purchasing_Document_Number2','Company_Code2', 'Purchasing_Document_Category2'], axis=1)
  
#Read & Merging/join Tables, keep only the needed columns for further analysis
T001 = pd.read_csv('T001_AltColTitles.CSV',encoding='latin-1')
T001=T001[['Company_Code','Name_of_Company_Code_or_Company']]
#Did not join T001W table: we do not have the column for plant names
#Cannot Merge:there are more than one description for the same material, may cause potential mistakes when counting for duplicate POs.
   #MAKT = pd.read_csv('MAKT_AltColTitles_pipe.txt',sep='|',error_bad_lines=False, encoding='latin-1')
   #MAKT=MAKT[['Material_Number','Material_Description__Short_Text_']]
   #PO=pd.merge(EKKOEKPO,MAKT,how='inner', on="Material_Number")

#Change the data type for company_code column, so that we can join the two tables
T001['Company_Code'].head(10)
EKPOEKKO['Company_Code'].head(10)
T001['Company_Code']=T001['Company_Code'].astype('str')
EKPOEKKO['Company_Code']=EKPOEKKO['Company_Code'].astype('str')
PO=pd.merge(EKPOEKKO,T001, how='inner', on='Company_Code')
PO.shape
PO.head(10)

#df1.to_csv('PO.csv',index=False)
#PO=pd.read_csv('PO.CSV', encoding='latin-1')

#Change the data type for the date column
PO['Purchasing_Document_Date']=pd.to_datetime(PO['Purchasing_Document_Date'])

#Create a subset of data so that the records are within user interested time range
#Insert the start and end date you want to check, please make sure that start date is earlier than the end date
startDate=input("Enter the start date as YYYY-MM-DD: ") #Used 2018-01-01
endDate = input("Enter the end date as YYYY-MM-DD: ") #For visualization purpose, entered 2018-01-07 for 7 days, 2018-01-14 for 14 days and 2018-01-31 for a month

startDate=pd.to_datetime(startDate)
endDate=pd.to_datetime(endDate)

#Create a subset of data so that the records are within user interested time range
df = PO.loc[(PO['Purchasing_Document_Date'] >= startDate) & (PO['Purchasing_Document_Date'] < endDate)]

#The order amounts are not in local currency, so we changed the order amounts into USD. Exchange Rate are as of 2018-09-24
currency_dict = {'USD': 1, 'EUR': 1.17, 'GBP': 1.31 ,'JPY': 0.0089, 'CAD':0.77, 'DKK': 0.16}
df.loc[:,'Exchange'] = df['Currency_Key_x'].replace(currency_dict)
df['Net_Order_Value_in_PO_Currency'] = df['Net_Order_Value_in_PO_Currency'].astype('float')
df.loc[:,'Amount_in_USD'] = df['Net_Order_Value_in_PO_Currency']*df['Exchange']
df['Amount_in_USD'].round(2)

#Change the datatype of Profit Center so the numbers will display completely(Avoid Scientific Notation)
df['Profit_Center'].dtypes
df['Profit_Center']=df['Profit_Center'].astype(str).replace('\.0', '', regex=True)
#Avoid Scientific Notation of PO Quantity
df['Purchase_Order_Quantity']=df['Purchase_Order_Quantity'].astype(str).replace('\.0', '', regex=True)

#The following can be used for spliting the whole dataset into certain time periods (instead of subsetting):
'''
from datetime import timedelta
import math
    
n_days = input('Enter number of days you want to check')
n_days=int(n_days)

end = PO['Purchasing_Document_Date'].max()
start = PO['Purchasing_Document_Date'].min()

PO.loc[:,'n_days'] = 0
total_days = end - start
total_days=total_days.days

period = math.ceil(total_days/n_days)
period
rng = pd.date_range(start, periods=period,freq='300D') #rng is range

n = 0
for i in rng:
	start_date = i
	end_date = i + timedelta(days=300) 
	mask = (PO['Purchasing_Document_Date'] >= start_date) & (PO['Purchasing_Document_Date'] < end_date)
	n += 1
	PO.loc[mask,'n_days'] = n
'''


#Create a table for duplicate PO count
df1=df[['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity','Purchasing_Document_Date','Purchasing_Document_Number']]
df1.shape

a = pd.DataFrame(
        df1.groupby(['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity'])\
        ['Purchasing_Document_Number'].count())
a.reset_index(inplace=True)
a.shape
#only keep the ones with more than 1 count (keep the ones with duplicates)
a=a.loc[a['Purchasing_Document_Number']>1]
a.shape
a.rename(columns={'Purchasing_Document_Number':'PO Count'},inplace=True)
a['PO Count']=a['PO Count'].astype(int)

#Create a table to calculate the total dollar amount of duplicate POs
b=pd.DataFrame(
        df1.groupby(['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity'])\
        ['Amount_in_USD'].sum())
b.reset_index(inplace=True)
b.head(3)
b.rename(columns={'Amount_in_USD':'Duplicated PO Amount'},inplace=True)
#Avoid showing scientific notations
b['Duplicated PO Amount']=b['Duplicated PO Amount'].apply(lambda x: '{:10.2f}'.format(x))

#Create a table to calculate the average amount of duplicate POs
c=pd.DataFrame(
        df1.groupby(['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity'])\
        ['Amount_in_USD'].mean())
c.reset_index(inplace=True)
c.head(3)
c.rename(columns={'Amount_in_USD':'Average PO Amount'},inplace=True)
#Avoid showing scientific notations
c['Average PO Amount']=c['Average PO Amount'].apply(lambda x: '{:10.2f}'.format(x))

#Combine the counts and the amount
ab=pd.merge(a,b,how='inner', on=['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity'])
ab.shape

abc=pd.merge(ab,c,how='left', on=['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity'])
abc.shape

abc.to_csv('Duplicate PO combined.csv')

#Merge Back (show all the details of the duplicate orders)
abcdf=pd.merge(abc,df,how='inner', on=['Vendor_Account_Number','Material_Number','Purchase_Order_Quantity'])
abcdf.shape
abcdf.to_csv('Duplicated PO detail.csv')

