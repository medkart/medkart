import streamlit as st

import pandas as pd
import numpy as np
from datetime import datetime,date,timedelta,time
import streamlit as st
from pyxlsb import open_workbook as open_xlsb
from io import BytesIO

def to_excel(df,df1):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='PK Data')
    df1.to_excel(writer,index=False,sheet_name='Unique Items')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


st.title("PickNote removed Item list")

Picknote = st.file_uploader("Please upload Picknote file", ".csv")

if Picknote is not None:
  Picknote = pd.read_csv(Picknote,skiprows=3)
  if st.checkbox("Show Picknote Data"):
      st.write(Picknote)
      Picknote = Picknote.loc[:,['EntryNumber','ProductName','Quantity','Shelf','TransferTo','TransferToCode']]

ItemMaster = st.file_uploader("Upload product list", ".csv")
if ItemMaster is not None:
  ItemMaster = pd.read_csv(ItemMaster,skiprows=5)
  ItemMaster = ItemMaster.loc[:,['ProductCode','ProductName']]
  

CS = st.file_uploader("Upload Company sales report",'.csv')
if CS is not None:
  CS = pd.read_csv(CS,skiprows=5)
  if st.checkbox("Show Company Sales Data"):
      st.write(CS)
  CS = CS.loc[:,['ProductCode',"CustomerName"]]


Trnsfr =  st.file_uploader("TransferOut Report", '.csv')
if Trnsfr is not None:
  Trnsfr = pd.read_csv(Trnsfr)
  if st.checkbox("Show TransferOut Data"):
      st.write(Trnsfr)
  Trnsfr = Trnsfr.loc[:,['ProductCode','ToLocation']]


Stock =  st.file_uploader("Upload StockReport", '.csv')
if Stock is not None:
    Stock = pd.read_csv(Stock,skiprows=5)
    if st.checkbox("Show Stock Data"):
          st.write(Stock)

if Picknote is not None and ItemMaster is not None and Trnsfr is not None and CS is not None and Stock is not None:
    PickNote1  = pd.merge(Picknote,ItemMaster,on='ProductName',how='left')
    PickNote1 = PickNote1[PickNote1['TransferTo'].notnull()]
    PickNote1['TransferToCode'] = PickNote1['TransferToCode'].astype('float64').astype('int64')
    PickNote1['TransferToCode'] = PickNote1['TransferToCode'].astype('str')
    
    if PickNote1['ProductCode'].dtype=='float64':
        NotFound = PickNote1[PickNote1['ProductCode'].isnull()]
        l2 = []
        if len(list(NotFound['ProductName'].unique()))<1000:
            st.error('Please update Product List')
            for name in list(NotFound['ProductName'].unique()):
                st.write(name)
                try:
                    x = st.text_input(f"please enter productCode of {name}:")
                    if x is not None:
                        if type(x)=='int32'| type(x)=='int64'
                            l2.append(x)
                except:
                    print("Please Run Again Module")
                    break
        else:
            print('Please update the product list')
    
        d1 = dict(zip(NotFound['ProductName'].unique(),l2))
        
        for i,j in d1.items():
            PickNote1['ProductCode']  = np.where(PickNote1['ProductName']==i,j,PickNote1['ProductCode'])
        PickNote1['ProductCode'] = PickNote1['ProductCode'].astype('float64').astype('int64')
    
    else: 
        PickNote1['ProductCode'] = PickNote1['ProductCode'].astype('float64').astype('int64')


    PickNote1['ProductCode'] = PickNote1['ProductCode'].astype('str')

    PickNote1['Key'] = PickNote1['ProductCode'] + PickNote1['TransferTo']

    Trnsfr['ProductCode'] = Trnsfr['ProductCode'].astype('str')
    Trnsfr['Key'] = Trnsfr['ProductCode']+Trnsfr['ToLocation']
    
    PickNote1 = PickNote1.merge(Trnsfr,on='Key',how='left',suffixes=(None,'_x'))
    PickNote1  = PickNote1[PickNote1['ToLocation'].isnull()]

    CS['ProductCode'] = CS['ProductCode'].astype('str')
    CS['Key'] = CS['ProductCode']+CS['CustomerName']

    PickNote2 = PickNote1.merge(CS,on='Key',how='left',suffixes=(None,'_y'))
    PickNote2 = PickNote2[PickNote2['CustomerName'].isnull()]


    PickNote3 = PickNote2.loc[:,['EntryNumber','ProductName','ProductCode','Quantity','Shelf','TransferTo','TransferToCode']]
    df= pd.DataFrame(PickNote3['TransferTo'].value_counts()).reset_index()
    
    l1 = list(df[df['TransferTo']>100]['index'])
    
    
    PickNote4 = PickNote3[~PickNote3['TransferTo'].isin(l1)]
    PickNote4[['ProductCode','TransferToCode']] = PickNote4[['ProductCode','TransferToCode']].astype('int64')
    
    PickNote4['Count'] = PickNote4['ProductName']
    
    
    PickNote5 = PickNote4.groupby(['ProductCode','ProductName']).agg({'Quantity':'sum','Count':'count'}).reset_index()
    PickNote5['ProductCode'] = PickNote5['ProductCode'].astype('int64')
     
    Stock = Stock.loc[:,['ProductCode','Stock']]
    
    Stock1  = Stock.groupby('ProductCode').agg({'Stock':'sum'}).reset_index()
    Stock1['Stock']  =Stock1['Stock'].astype('int64')
    
    PickNote6 = PickNote5.merge(Stock1,on='ProductCode',how='left')
    PickNote4 = PickNote4.drop('Count',1)


    if PickNote4 is not None and PickNote6 is not None:
        df_xlsx = to_excel(PickNote4,PickNote6)
        st.download_button(label='📥 Download Current Result',
                                        data=df_xlsx , file_name= 'PickNote Removed list.xlsx')
