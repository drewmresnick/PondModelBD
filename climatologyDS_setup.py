#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 11:08:00 2022

@author: drewr
"""
import pandas as pd

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