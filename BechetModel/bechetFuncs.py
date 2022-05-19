#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import datetime as dt
import pandas as pd
import math
import matplotlib.pyplot as plt
import bechetVars

#find the day of the model
def find_day_month_year(input_day, start_date):
    start_date = dt.datetime.strptime(start_date, "%d/%m/%Y")
    computed_day = (start_date + dt.timedelta(days = float(input_day))).date()
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)
    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later
def read_dataline(day_argue, hour,data):
    day, day_mon_year = find_day_month_year(day_argue,bechetVars.start_date)
    year = day_mon_year.year
    selected_data = data[(data[bechetVars.dyVar]== day) & (data[bechetVars.hrVar] == hour)& (data[bechetVars.yrVar] == year)]
    return selected_data 

#pond radiation, pp.3703, eqn.2 (Béchet et al 2011)
#Qra,p = -εwσTp4S 
def calculate_Qrap(T_wk):
    ew = 0.97 #water emissivity

    roh1 = 5.67 * (10**(-8)) #Wm-2K-4

    SA = 4047 #m2 area
    Qrap = -ew * roh1 * SA * (T_wk**4) 
    return Qrap

#solar radiation, pp.3703, eqn.3 (Béchet et al 2011)
#Qra,s = (1-fa)HsS
def calculate_Qras(day_argue, hour,data):
    daily_data = read_dataline(day_argue, hour,data)
    solrad = float(daily_data[bechetVars.sradVar])
    
    fa = 0 #% algae absorption

    Hs =  solrad #solar radiation W/m2
    
    SA = 4047 #m2 area
    Qras = (1-fa) * Hs * SA
    return Qras

#air radiation, pp.3703, eqn.4 (Béchet et al 2011)
#Qra,a = εw εa σTa4S
def calculate_Qraa(day_argue, hour,data):
    daily_data = read_dataline(day_argue, hour,data)
    T_a = float(daily_data[bechetVars.t2mVar])+ 273.15 #kelvin
    
    ew = 0.97 #water emissivity
    
    ea = 0.807 #air emissivity
    
    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4

    SA = 4047 #m2 area
    Qraa = ew * ea* roh1* (T_a**4) * SA #*3600

    return Qraa

#evaporation, pp.7303-3704, eqns.5-12 (Béchet et al 2011)
#Qevap = -meLwS 
def calculate_Qevap(day_argue, hour,T_wk,data):
    daily_data = read_dataline(day_argue, hour,data)
    T_a = float(daily_data[bechetVars.t2mVar]) +273.15#kelvin
    RH = float(daily_data[bechetVars.rhVar]) / 100 #needs to be value btwn 0 and 1 not percentage
    v = float(daily_data[bechetVars.windVar]) #m/s
    
    Lw = 2.45 * (10**6) #water latent heat J/kg 
    Dw = 2.42 * (10**(-3)) #(10**-5) #m2/s 

    l = 63.616#pond length in m
    va = 1.5 *(10**(-5)) #m2/s
    
    Rel = (l*v)/va
    Sch = va/Dw
    
    if Rel >= (4*(10**5)):
        SH= 0.035 * (Rel**0.8) * (Sch**(1/3))
    elif Rel <= (4*(10**5)):
        SH= 0.628 * (Rel**0.5) * (Sch**(1/3))
        
    K = (SH * Dw)/l
    R = 8.314 # m3/mol K   
             
    Pw = 3385.5 * math.exp(-8.0929+0.97608*((T_wk +42.607 -273.15)**0.5))
    Pa = 3385.5 * math.exp(-8.0929+0.97608*((T_a +42.607 -273.15)**0.5))

    Mw = 0.018 #kg/mol
    
    me = K *((Pw/T_wk) - ((RH*Pa)/T_a)) *(Mw/R)

    SA = 4047 #m2 area
    Qevap = -me * Lw * SA

    return Qevap

#convection, pp.3704, eqn.13-15 (Béchet et al 2011) 
#Qconv = hconv(Ta – Tp)S
def calculate_Qconv(day_argue, hour,data):
    daily_data = read_dataline(day_argue, hour,data)
    T_a = float(daily_data[bechetVars.t2mVar])+273.15 #kelvin
    v = float(daily_data[bechetVars.windVar]) #m/s
    l = 63.61#pond length in m
    va = 1.5 *(10**(-5)) #m2/s
    alpha = 1.4558 * (10**(-4))#2.2 * (10**(-5))
    lambda_a = .026
    
    Pr = va/alpha
    Rel = (l*v)/va
    if Rel >= (4 * (10**5)):
        Nu = 0.035* (Rel**0.8) * (Pr**(1/3))
    elif Rel <= (4 * (10**5)):
        Nu = 0.628* (Rel**0.5) * (Pr**(1/3))
    h = lambda_a * Nu / l
    SA = 4047 #m2 area
    
    Qconv = h * (T_a-T_wk)* SA
    return Qconv

def finalDataFrame(T_wk_vec,data,element_df):
    hourly_output = pd.DataFrame(element_df).rename(columns={0:'Qrap', 1:'Qras', 2:'Qraa', 3:'Qevap', 4:'Qconv', 5:'Qnet', 6:'T_wk'})
    T_wK = np.array(T_wk_vec)
    T_wC = T_wK.astype(float) - 273.15
    df = pd.DataFrame(T_wC).rename(columns={0:'T_wC'})
    fullDf= pd.concat([data, hourly_output, df], axis = 1)
    fullDf = fullDf[fullDf['T_wC'].notna()]    
    
    finalDf = fullDf
    return finalDf
  
def modelOutputs(T_wk_vec,data,observed):  
    df1 = finalDataFrame(T_wk_vec, data, element_df)
    
    max_temp = df1.groupby(bechetVars.dayCNTvar).max().reset_index()
    min_temp = df1.groupby(bechetVars.dayCNTvar).min().reset_index()
    mean_temp = df1.groupby(bechetVars.dayCNTvar).mean().reset_index()
    daily_dataMean = data.groupby(bechetVars.dayCNTvar).mean()
    daily_dataMax = data.groupby(bechetVars.dayCNTvar).max()
    daily_dataMin = data.groupby(bechetVars.dayCNTvar).min()
    
    df2 = pd.DataFrame(data={'date': pd.date_range(start=bechetVars.start_date,end=bechetVars.end_date,freq='D')})
    df2['modelH20_max'] = max_temp['T_wC']
    df2['modelH20_min'] = min_temp['T_wC']
    df2['modelH20_mean'] = mean_temp['T_wC']
    df2['airTemp_mean'] = daily_dataMean[bechetVars.t2mVar]
    df2['airTemp_max'] = daily_dataMax[bechetVars.t2mVar]
    df2['airTemp_min'] = daily_dataMin[bechetVars.t2mVar]
        
    plt.plot(max_temp.index, max_temp['T_wC'], label="max water temp (modelled)")
    plt.plot(min_temp.index, min_temp['T_wC'], label="min water temp (modelled)")
    plt.plot(daily_dataMean.index, daily_dataMean[bechetVars.t2mVar], label="average air temp (measured)")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare daily model data to avg observed air temp")
    plt.legend()
    
    if bechetVars.saveFile == "y":
        plt.savefig(f'{bechetVars.outputPath}{bechetVars.outputFileNameHr}_modelVairtemp_bechet.png')
        plt.show()
    elif bechetVars.saveFile == "n":
        plt.show()
        
    if isinstance(observed, pd.DataFrame):
        mergeDf = df2.merge(observed, how='inner', on = ['date'])
        return df1,mergeDf
    else:
        return df1, df2
        
        
def modelVSobserved(T_wk_vec,data,observed): #compare daily avg water temp to obs
    
    df1 = finalDataFrame(T_wk_vec, data, element_df)
    
    max_temp = df1.groupby(bechetVars.dayCNTvar).max()
    min_temp = df1.groupby(bechetVars.dayCNTvar).min()
    
    plt.plot(max_temp.index, max_temp['T_wC'], label="max water temp (modelled)")
    plt.plot(min_temp.index, min_temp['T_wC'], label="min water temp (modelled)")
    plt.plot(observed.index, observed['avg_water_temp'], label="average water temp (observed)")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare daily model data to avg observed water temp")
    plt.legend()
    
    if bechetVars.saveFile == "y":
        plt.savefig(f'{bechetVars.outputPath}{bechetVars.outputFileNameHr}_modelVobserved_bechet.png')
        plt.show()
    elif bechetVars.saveFile == "n":
        plt.show()

# loop for energy flux equation hourly
def main_simulation_loop(data,observed,T_wk0,filesPath,numberDays,saveFile,outputPath):
    
    global element_df
    global T_wk
    global hourly_output
    
    element_df = [] 
    T_wk_vec = [] 
    
    count = 0
    T_wk = T_wk0
    
    for day_argue in list(range(0, numberDays)):
        
        for hour in list(range(0, 24)):
            
            count = count + 1

            Qrap = calculate_Qrap(T_wk)
            Qras = calculate_Qras(day_argue,hour,data)
            Qraa = calculate_Qraa(day_argue,hour,data)
            Qevap = calculate_Qevap(day_argue,hour,T_wk,data)
            Qconv = calculate_Qconv(day_argue,hour,data)

            Qnet = Qrap + Qras + Qraa + Qevap + Qconv
            
            net_temp =(Qnet / (bechetVars.water_density * bechetVars.Volume * bechetVars.specific_heat)) * 60 * 60
            
            T_wk_new = net_temp + T_wk

            T_wk_vec.append(T_wk_new)
    
            T_wk = T_wk_new 
            
            element_df.append([Qrap, Qras, Qraa, Qevap, Qconv, Qnet, T_wk])
        
    modelOutput = modelOutputs(T_wk_vec,data,observed)
    if saveFile == "y":
        modelOutput[0].to_csv(f'{outputPath}{bechetVars.outputFileNameHr}_hourlyBechet.csv',index=False)
        modelOutput[1].to_csv(f'{outputPath}{bechetVars.outputFileNameDy}_dailyBechet.csv', index=False)
        if isinstance(observed, pd.DataFrame):
            modelVSobserved(T_wk_vec,data,observed)
    elif saveFile == "n":
        modelOutput[0]
        if isinstance(observed, pd.DataFrame):
            modelVSobserved(T_wk_vec,data,observed)
        
def climatology_simulation_loop(data,T_wk0,filesPath,numberDays,saveFile,outputPath,observed='NA'):

    global element_df
    element_df = []
    T_wk_vec = []
    global T_wk
    global hourly_output  
    
    T_wk = T_wk0
    count = 0

    for day_argue in list(range(0, numberDays)):
        for hour in list(range(0, 24)):
            
            count = count + 1
            
            Qrap = calculate_Qrap(T_wk)
            Qras = calculate_Qras(day_argue,hour,data)
            Qraa = calculate_Qraa(day_argue,hour,data)
            Qevap = calculate_Qevap(day_argue,hour,T_wk,data)
            Qconv = calculate_Qconv(day_argue,hour,data)

            Qnet = Qrap + Qras + Qraa + Qevap + Qconv
            
            net_temp =(Qnet / (bechetVars.water_density * bechetVars.Volume * bechetVars.specific_heat)) * 60 * 60
            
            T_wk_new = net_temp + T_wk

            T_wk_vec.append(T_wk_new)
    
            T_wk = T_wk_new 
            
            element_df.append([Qrap, Qras, Qraa, Qevap, Qconv, Qnet, T_wk])
        
    modelOutput = modelOutputs(T_wk_vec,data,observed)           
    if saveFile == "y":
        modelOutput[0].to_csv(f'{outputPath}{bechetVars.outputFileNameHr}_hourlyBechet.csv',index=False)
        modelOutput[1].to_csv(f'{outputPath}{bechetVars.outputFileNameDy}_dailyBechet.csv', index=False)
    elif saveFile == "n":
        modelOutput[0]
