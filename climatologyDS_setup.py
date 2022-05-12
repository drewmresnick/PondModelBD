#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from datetime import datetime

#DAILY DATA
df = pd.read_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_GM/dataFiles_GaoMerrick/POWER_Point_Daily_19900101_20201231_022d7833N_089d5330E_LST.csv",skiprows=12)
climatology = df.groupby(['DOY']).mean()
climatology.reset_index(inplace=True)
climatology = climatology.rename(columns = {'DOY':'day','YEAR':'year','ALLSKY_SFC_SW_DWN':'SRAD'})
climatology['T2M'] = climatology['T2M'] + 273.15
climatology['date'] = pd.date_range(start='1/1/2017',periods=len(climatology),freq='D')
climatology['month'] = pd.DatetimeIndex(climatology['date']).month
climatology = climatology.drop('date',1)


perc95 = df['T2M'].quantile(q=0.95)
perc05 = df['T2M'].quantile(q=0.05)

df95 = df[(df['T2M'] >= perc95)]
df05 = df[(df['T2M'] <= perc05)]

climatology.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_GM/dataFiles_GaoMerrick/climatology.csv",index=False)
df95.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_GM/dataFiles_GaoMerrick/allYears_95.csv",index=False)
df05.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_GM/dataFiles_GaoMerrick/allYears_05.csv",index=False)


#HOURLY DATA
df = pd.read_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_Bechet/climatology/POWER_Point_Hourly_20010102_20211230_022d7833N_089d5333E_LST.csv")
climatology = df.groupby(['MO','DY','HR']).agg({'ALLSKY_SFC_SW_DWN':['mean'],'T2M':['mean'],'RH2M':['mean'],'WS2M':['mean']})
climatology.columns = ['ALLSKY_SFC_SW_DWN','T2M','RH2M','WS2M']
climatology = climatology.reset_index()
climatology['T2M'] = climatology['T2M']
climatology['DAY'] = ""
#climatology = climatology[(climatology['MO']!=2) & (climatology['DY']!=29)]

for index in climatology.index:
    row = index
    day = climatology['DY'][row]
    month = climatology['MO'][row]
    date = f"{day}/{month}/2017"
    date = datetime.strptime(date,'%d/%m/%Y').timetuple().tm_yday
    climatology['DAY'][row] = date
    
perc95 = df['T2M'].quantile(q=0.95)
perc05 = df['T2M'].quantile(q=0.05)

df95 = df[(df['T2M'] >= perc95)]
df05 = df[(df['T2M'] <= perc05)]

climatology.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_Bechet/climatology/climatology.csv",index=False)
df95.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_Bechet/climatology/allYears_95.csv",index=False)
df05.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/dataFiles_Bechet/climatology/allYears_05.csv",index=False)


    