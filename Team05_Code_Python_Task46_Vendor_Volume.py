import pandas as pd
from pandasql import sqldf #sqldf will be used to merge datasets using SQL queries

# read all the required files
bsak_data = pd.read_csv("BSAK_BKPF_AltColTitles.CSV")
lfa_data = pd.read_csv("LFA1_AltColTitles.CSV")
t_data = pd.read_csv("T001_with_CountryKey_AltColTitles.CSV")
payment_data = pd.read_excel("payment_type_xl.xlsx")


# filter for Document Type
bsak_filt = bsak_data[(bsak_data.Document_Type=='ZP') | (bsak_data.Document_Type=='KZ')]
payment_filt = payment_data[(payment_data['Document type for payment']=='ZP') | (payment_data['Document type for payment']=='KZ')]


# select only required c0lumns
bsak_select_list = ['Company_Code', 'Account_Number_of_Vendor_or_Creditor', 'Accounting_Document_Number', 'Document_Type', 
                    'Number_of_Line_Item_Within_Accounting_Document', 'Document_Number_of_the_Clearing_Document', 
                    'Fiscal_Year', 'Document_Date_in_Document', 'Clearing_Date', 
                    'Day_On_Which_Accounting_Document_Was_Entered', 'Debit_Credit_Indicator', 'Currency_Key', 
                    'Amount_in_Document_Currency', 'Amount_in_Local_Currency', 'Reverse_Document_Number', 'Payment_Method']

t_select_list = ['Company_Code', 'Name_of_Company_Code_or_Company', 'Country_Key']

bsak_filt = bsak_filt[bsak_select_list]
t_filt = t_data[t_select_list]


# SQL query to merge BSAK with T001
final_data_sql = """Select b.*, t.Name_of_Company_Code_or_Company, t.Country_Key from 
bsak_filt b
inner join t_filt t
on b.Company_Code = t.Company_Code
;"""
final_data = sqldf(final_data_sql)

# SQL query to grab payment method from Payments file
# Left join is used because not all rows have a payment type
final_data_sql = """Select f.*, p.`Name (in language of country)` from 
final_data f
left join payment_data p
on f.Payment_Method = p.`Payment Method`
and f.Country_Key = p.`Country Key`
;"""
fin_data2 = sqldf(final_data_sql)


# write the final data to a csv file
fin_data2.to_csv("final_data_task46.csv")
