#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 12:19:35 2021

@author: sanketa, Drew

Model elements:
    
Qra,p: radiation from pond surface (W)
Qra,s: total (direct and diffuse) solar radiation (W)
Qra,a: radiation from air to pond (W)
Qev: evaporative heat flux (W)
Qconv: convective flux at pond surface (W)
Qcond: conductive flux with ground at pond bottom (W) #not using
Qi: heat flux associated with water inflow (W)
Qr: heat flux induced by rain (W) #not using

This file will ask for three inputs when run:
    1. number of days to run the model
    2. directory path to where files are held
    3. if you would like to save the outputs (enter (y) if you would like to run
                                              accompanying diagnostics file 
                                              for the model)

"""
import numpy as np
import datetime as dt
import pandas as pd
import math
import matplotlib.pyplot as plt
from configparser import ConfigParser

config = ConfigParser()
config.read('Bechet_config.ini')

outputFilesPath = config.get('data', 'outputFilesPath')

#data vars
hrVar =config.get('inputVarNames','hrVar')
doyVar = config.get('inputVarNames','doyVar')
yrVar = config.get('inputVarNames','yrVar')
start_date = config.get('data','start_date')

dayCNTvar = config.get('inputVarNames','dayCNTvar')
windVar = config.get('inputVarNames','windVar')
sradVar = config.get('inputVarNames','sradVar')
airTempInputVar = config.get('inputVarNames','airTempInputVar')
rhVar = config.get('inputVarNames','rhVar')
airTempCompareVar = config.get('inputVarNames','airTempCompareVar')
waterTempVar = config.get('obsVarNames', 'waterTempVar')

    
#Pond specific values
pond_depth =config.getfloat('modelConstants', 'pondDepth') #meters
T_wk = config.getfloat('modelConstants', 'initialTemp') #first day water temp at khulna 
T_wk_vec = []
Volume =  config.getfloat('modelConstants', 'pondVolume') #m3
area = config.getfloat('modelConstants', 'pondArea') #m2

#Constants
water_density = 998 #kg/m3
specific_heat = 4.18 * (10**3)

def find_day_month_year(input_day, start_day = dt.date(2017,1,1)):
    computed_day = start_day + dt.timedelta(days = float(input_day))
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)
    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later
def read_dataline(day_argue, hour,data):
    day, day_mon_year = find_day_month_year(day_argue)
    year = day_mon_year.year
    selected_data = data[(data[doyVar]== day) & (data[hrVar] == hour)& (data[yrVar] == year)]    
    return selected_data 

#pond radiation
def calculate_Qrap(T_wk):
    
    #Qra,p = -εwσTp4S 
    ew = 0.97 #water emissivity

    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4

    SA = 4047 #m2 area
    Qrap = -ew * roh1 * SA * (T_wk**4) #*3600
    
    return Qrap

#solar radiation
#Qra,s = (1-fa)HsS
def calculate_Qras(day_argue, hour,data):
    daily_data = read_dataline(day_argue, hour,data)
    print(daily_data)
    solrad = float(daily_data[sradVar])
    
    fa = 0 #% algae absorption

    Hs =  solrad #/ area#solar radiation Wh/m2
    
    SA = 4047 #m2 area
    Qras = (1-fa) * Hs * SA #*3600
    
    return Qras

#air radiation
#Qra,a = εw εa σTa4S
def calculate_Qraa(day_argue, hour,data):
    daily_data = read_dataline(day_argue, hour,data)
    T_a = float(daily_data[t2mVar])+ 273.15 #kelvin
    
    ew = 0.97 #water emissivity
    
    ea = 0.8 #air emissivity
    
    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4

    SA = 4047 #m2 area
    Qraa = ew * ea* roh1* (T_a**4) * SA #*3600
    
    return Qraa

#evaporation
#Qevap = -meLwS 
def calculate_Qevap(day_argue, hour,T_wk,data):
    daily_data = read_dataline(day_argue, hour,data)
    T_a = float(daily_data[t2mVar]) +273.15#kelvin
    RH = float(daily_data[rhVar]) / 100 #needs to be value btwn 0 and 1 not percentage
    v = float(daily_data[windVar]) #m/s
    
    Lw = 2.45 * (10**6) #water latent heat J/kg 
    Dw = 2.4 * (10**-5) #m2/s 

    l = 63.61#pond length in m
    va = 1.5 *(10**-5) #m2/s
    
    Rel = (l*v)/va
    
    Sch = va/Dw
    
    if Rel >= (4*(10**5)):
        SH= 0.035 * (Rel**0.8) * (Sch**1/3)
    elif Rel <= (4*(10**5)):
        SH= 0.628 * (Rel**0.5) * (Sch**1/3)
    
    K = (SH * Dw)/l
    
    R = 8.314 # m3/mol K                
    Pw = 3385.5 * math.exp(-8.0929+0.97608*((T_wk +42.607 -273.15)**0.5))
    Pa = 3385.5 * math.exp(-8.0929+0.97608*((T_a +42.607 -273.15)**0.5))
    Mw = 0.018 #kg/mol
    
    me = K *((Pw/T_wk) - ((RH*Pa)/T_a)) *(Mw/R)
    
    SA = 4047 #m2 area
    Qevap = -me * Lw * SA #*3600
    
    return Qevap

#convection 
#Qconv = hconv(Ta – Tp)S
def calculate_Qconv(day_argue, hour,data):
    daily_data = read_dataline(day_argue, hour,data)
    T_a = float(daily_data[t2mVar])+273.15 #kelvin
    
    v = float(daily_data[windVar]) #m/s
    l = 63.61#pond length in m
    va = 1.5 *(10**-5) #m2/s
    alpha = 2.2 * (10**-5)
    lambda_a = 2.6 * (10 **-2)
    
    Pr = va/alpha
    
    Rel = (l*v)/va
    
    Nu = 0.035* (Rel**0.8) * (Pr**(1/3))
    
    h = lambda_a * Nu / l
    SA = 4047 #m2 area
    
    Qconv = h * (T_a-T_wk)* SA #*3600
   
    return Qconv

def finalDataFrame(T_wk_vec,data,element_df):
    hourly_output = pd.DataFrame(element_df).rename(columns={0:'Qrap', 1:'Qras', 2:'Qraa', 3:'Qevap', 4:'Qconv', 5:'Qnet', 6:'T_wk'})
    T_wK = np.array(T_wk_vec)
    T_wC = T_wK.astype(float) - 273.15
    df = pd.DataFrame(T_wC).rename(columns={0:'T_wC'})
    fullDf= pd.concat([data, df,hourly_output], axis = 1).drop([t2mVar,sradVar,windVar,rhVar], axis=1)
    fullDf = fullDf[fullDf['T_wC'].notna()]    
    
    finalDf = fullDf
    return finalDf
  
def modelOutputs(T_wk_vec,data,observed):  
    df1 = finalDataFrame(T_wk_vec, data, element_df)
    
    max_temp = df1.groupby(dayCNTvar).max().reset_index()
    min_temp = df1.groupby(dayCNTvar).min().reset_index()
    mean_temp = df1.groupby(dayCNTvar).mean().reset_index()
    daily_data = data.groupby(doyVar).mean()
    
    df2 = pd.DataFrame(data={'date': pd.date_range(start='2017-1-1',end='2019-12-31',freq='D')})
    df2['daily_maxModel'] = max_temp['T_wC']
    df2['daily_minModel'] = min_temp['T_wC']
    df2['daily_meanModel'] = mean_temp['T_wC']
    mergeDf = df2.merge(observed, how='inner', on = ['date'])
    
    plt.plot(max_temp.index, max_temp['T_wC'], label="max water temp (modelled)")
    plt.plot(min_temp.index, min_temp['T_wC'], label="min water temp (modelled)")
    plt.plot(daily_data.index, daily_data[t2mVar], label="average air temp (measured)")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare daily model data to avg observed air temp")
    plt.legend()
    plt.show() 

    return df1,mergeDf
        
def modelVSobserved(T_wk_vec,data,observed): #compare daily avg water temp to obs
    df1 = finalDataFrame(T_wk_vec, data, element_df)
    
    max_temp = df1.groupby(dayCNTvar).max()
    min_temp = df1.groupby(dayCNTvar).min()
    
    plt.plot(max_temp.index, max_temp['T_wC'], label="max water temp (modelled)")
    plt.plot(min_temp.index, min_temp['T_wC'], label="min water temp (modelled)")
    plt.plot(observed.index, observed['avg_water_temp'], label="average water temp (observed)")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare daily model data to avg observed water temp")
    plt.legend()
    plt.show()

# loop for energy flux equation hourly
def main_simulation_loop(data,observed,filesPath,numberDays,saveFile,outputPath):

    global element_df
    element_df = []
    global T_wk
    global hourly_output
    
    count = 0
    for day_argue in list(range(0, numberDays)):
        
        for hour in list(range(0, 24)):
            
            count = count + 1
            
            print(f"Iteration {count} start - T_wk: {T_wk}")

            Qrap = calculate_Qrap(T_wk)
            Qras = calculate_Qras(day_argue, hour,data)
            Qraa = calculate_Qraa(day_argue, hour,data)
            Qevap = calculate_Qevap(day_argue, hour,T_wk,data)
            Qconv = calculate_Qconv(day_argue, hour,data)

            Qnet = Qrap + Qras + Qraa + Qevap + Qconv
            
            net_temp =(Qnet / (water_density * Volume * specific_heat)) * 60 * 60
            print(f'iteration: {count}, net_temp: {net_temp}')
            
            T_wk_new = net_temp + T_wk

            T_wk_vec.append(T_wk_new)
    
            T_wk = T_wk_new 
            
            element_df.append([Qrap, Qras, Qraa, Qevap, Qconv, Qnet, T_wk])
        
    modelOutput = modelOutputs(T_wk_vec,data,observed)
    if saveFile == "y":
        modelOutput[0].to_csv(f'{filesPath}{outputPath}simulated_hourly.csv',index=False)
        modelOutput[1].to_csv(f'{filesPath}{outputPath}simulatedVobserved_daily.csv', index=False)
        modelVSobserved(T_wk_vec,data,observed)
    elif saveFile == "n":
        modelOutput[0]
        modelVSobserved(T_wk_vec,data,observed)
        
def climatology_simulation_loop(data,filesPath,numberDays,saveFile,outputPath):
    