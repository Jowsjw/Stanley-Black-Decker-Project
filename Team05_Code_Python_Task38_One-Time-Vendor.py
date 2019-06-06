
# coding: utf-8

#Author:Jinwei Wang
#Date revised: 10-18-2018



#Import Library
import pandas as pd


# # Start with BSAK Table

#Read the dataset
df = pd.read_csv("BSAK_BKPF_AltColTitles.csv")

df.columns

#Filter the ZP & KZ
BSAK = df.loc[(df.Document_Type.str.contains('ZP')== False) & (df.Document_Type.str.contains('KZ')== False)]

#Change the type of Company_code for later table join
BSAK['Company_Code'] = BSAK['Company_Code'].astype('str')

BSAK.head()


# # Merge T001 Table

#Read T001 table
T001 = pd.read_csv("T001_AltColTitles.csv")

T001.columns

#Change the type of Company_code for later table join
T001['Company_Code'] = T001['Company_Code'].astype('str')

#Merge Bask table and T001 table on Company_code
BSAK_T001 = pd.merge(BSAK,T001,on = 'Company_Code',suffixes=[' - BSAK',' - T001'])

BSAK_T001.head()


# # Merge LFA1 Table

#Read LFA1 table
LFA1 = pd.read_csv("LFA1_AltColTitles.csv")

#Change Date to 'date' type
LFA1['Date_on_which_the_Record_Was_Created'] = pd.to_datetime(LFA1['Date_on_which_the_Record_Was_Created'])

#Only retain those dates betwee 01-01-2018 to 06-30-2018
LFA1 = LFA1.loc[(LFA1.Date_on_which_the_Record_Was_Created > '01-01-2018') & (LFA1.Date_on_which_the_Record_Was_Created < '06-30-2018')]


#Merge 3 tables
BSAK_T001_LFA1 = pd.merge(BSAK_T001,LFA1,on='Account_Number_of_Vendor_or_Creditor',suffixes=[' - BSAK',' - LFA1'])

BSAK_T001_LFA1.head()


# Check the shape of new table
BSAK_T001_LFA1.shape

BSAK_T001_LFA1.columns


#Also put all things into a function
def get_bsakt001lf1(bsakpath,t001path,lfapath):
####Read bsak first, and filter 'zp','kz'
    df = pd.read_csv(bsakpath)
    BSAK = df.loc[(df.Document_Type.str.contains('ZP')== False) & (df.Document_Type.str.contains('KZ')== False)]
    BSAK['Company_Code'] = BSAK['Company_Code'].astype('str')
####Read T001,filter 1001,join with bsak
    T001 = pd.read_csv(t001path)
    BSAK_T001 = pd.merge(BSAK,T001,on = 'Company_Code',suffixes=[' - BSAK',' - T001'])
####Read LFA1,filter dates,join with bsak_t001    
    LFA1 = pd.read_csv("LFA1_AltColTitles.csv")
    LFA1['Date_on_which_the_Record_Was_Created'] = pd.to_datetime(LFA1['Date_on_which_the_Record_Was_Created'])
    LFA1 = LFA1.loc[(LFA1.Date_on_which_the_Record_Was_Created > '1/1/2018') & (LFA1.Date_on_which_the_Record_Was_Created < '6/30/2018')]
    BSAK_T001_LFA1 = pd.merge(BSAK_T001,LFA1,on='Account_Number_of_Vendor_or_Creditor',suffixes=[' - BSAK',' - LFA1'])
    return BSAK_T001_LFA1


# # Filter multiple acc_doc_number

#Get the counts of the frequency of all accounting document number
count1 = pd.DataFrame(BSAK_T001_LFA1['Accounting_Document_Number'].value_counts())

#Drop the index
count1.reset_index(level=0, inplace=True)

#Rename the dataframe for future use
count1 = count1.rename(index=str, columns={"index": "Accounting_Document_Number", "Accounting_Document_Number": "Value_counts"})

#Check the shape before filtering
count1.shape

#Filter those account document number that appear more than 1 time
One_time_acc = count1.loc[count1.Value_counts==1]

#Check the result after applying filter
One_time_acc.shape


# # Find One-Time-Vendor (Filter multiple account numbers)

#Get the counts of the frequency of all accounting number(Vendor ID)
count = pd.DataFrame(BSAK_T001_LFA1['Account_Number_of_Vendor_or_Creditor'].value_counts())

#Drop the index
count.reset_index(level=0, inplace=True)

#Rename the dataframe for future use
count = count.rename(index=str, columns={"index": "Account_Number_of_Vendor_or_Creditor", "Account_Number_of_Vendor_or_Creditor": "Value_counts"})

#Filter those account number that appear more than 1 time
One_time_acc = count.loc[count.Value_counts==1]

One_time_acc.tail()

One_time_acc.shape

#Join the one-time vendor table to the Vendor incoice table(BSAK_TOO1_LFA1)
One_time_Vendor = pd.merge(BSAK_T001_LFA1,One_time_acc,on='Account_Number_of_Vendor_or_Creditor')


One_time_Vendor.info()

#Drop the counts
One_time_Vendor.drop(['Value_counts'],axis = 1,inplace = True)

#Putting all thing into a function
def get_one_time(BSAK_T001_LFA1):
    count1 = pd.DataFrame(BSAK_T001_LFA1['Accounting_Document_Number'].value_counts())
    count1.reset_index(level=0, inplace=True)
    count1 = count1.rename(index=str, columns={"index": "Accounting_Document_Number", "Accounting_Document_Number": "Value_counts"})
    One_time_acc = count1.loc[count1.Value_counts==1]
    count = pd.DataFrame(BSAK_T001_LFA1['Account_Number_of_Vendor_or_Creditor'].value_counts())
    count.reset_index(level=0, inplace=True)
    count = count.rename(index=str, columns={"index": "Account_Number_of_Vendor_or_Creditor", "Account_Number_of_Vendor_or_Creditor": "Value_counts"})
    One_time_acc = count.loc[count.Value_counts==1]
    One_time_Vendor = pd.merge(BSAK_T001_LFA1,One_time_acc,on='Account_Number_of_Vendor_or_Creditor')
    One_time_Vendor.drop(['Value_counts'],axis = 1,inplace = True)
    return One_time_Vendor


# # Enter a Threshold

#Input a threshold
amount = eval(input("Enter a threshold value\n"))

#Filter vendors that less than the threshold
Vendor_exceed_th = One_time_Vendor.loc[One_time_Vendor.Amount_in_Local_Currency > amount]

Vendor_exceed_th.tail()


# # Enter Date Range

import datetime

#Change Document_Date to 'Date' Type
One_time_Vendor['Document_Date_in_Document'] = pd.to_datetime(One_time_Vendor['Document_Date_in_Document'])

#Input Start_Date
start_date = input('Enter a Startdate in MM-DD-YYYY format\n')

#Input End_Date
end_date = input('Enter a Enddate in MM-DD-YYYY format\n')

#Filter transactions that happened outside the date range
Vendor_exceed_th = One_time_Vendor.loc[(One_time_Vendor.Document_Date_in_Document > start_date) & (One_time_Vendor.Document_Date_in_Document < end_date)]

Vendor_exceed_th.tail()

#Only Keep those import columns(Those columns are from AP_EN.PDF the document we received from SBD,page 13)
One_time_Vendor = One_time_Vendor[['Company_Code','Company_Code2','Name_of_Company_Code_or_Company','Account_Number_of_Vendor_or_Creditor','Debit_Credit_Indicator','Currency_Key - BSAK','Currency_Key - T001','Amount_in_Local_Currency','Amount_in_Document_Currency','Accounting_Document_Number','Accounting_Document_Number2','Document_Date_in_Document']]

#Save one_time_vendor to excel file
One_time_Vendor.to_excel("One_time_vendor.xlsx",index=False)

