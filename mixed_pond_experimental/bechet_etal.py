#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 13:41:53 2021

@author: sanketa
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 12:19:35 2021

@author: sanketa
"""
import numpy as np
import datetime as dt
import pandas as pd
import math
import cmath
import matplotlib.pyplot as plt

#Setting constant values 
numberDays = 1096 #1096 for the test dataset
pond_depth = 1.5204 #meters
water_density = 997 #kg/m3
T_0 = 287.51
T_wk = 287.51 #first day water temp at khulna 
T_wc_0 = 19.3
T_wk_vec = []


specific_heat = 4.18 * (10**3)
Volume = 6153.05 #m3
area = 4047 #m2


#Tp: pond temp (K)
#Pw: density (kh m-3)
#Cpw: specific heat capacity (J kg-1 K-1)
#V: pond volume (m3)
#Qra,p: radiation from pond surface (W)
#Qra,s: total (direct and diffuse) solar radiation (W)
#Qra,a: radiation from air to pond (W)
#Qev: evaporative heat flux (W)
#Qconv: convective flux at pond surface (W)
#Qcond: conductive flux with ground at pond bottom (W) #not using
#Qi: heat flux associated with water inflow (W)
#Qr: heat flux induced by rain (W) #not using


#open csv file using pandas to create pandas dataframe 
data = pd.read_csv("/Users/drewr/git_drewr/ACToday/bangladesh/pondModel/sanketa_model/PondModelBD/mixed_pond_experimental/bechet_etal_input.csv") 
observed = pd.read_csv("/Users/drewr/git_drewr/ACToday/bangladesh/pondModel/sanketa_model/PondModelBD/mixed_pond_experimental/observed_khulna.csv")

def find_day_month_year(input_day, start_day = dt.date(2016,12,31)):
    computed_day = start_day + dt.timedelta(days = float(input_day))
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)

    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later

def read_dataline(day_argue, hour):
    
    day, day_mon_year = find_day_month_year(day_argue)
    #year = day_mon_year.year
    
    selected_data = data[(data['DAY']== day) & (data['HR'] == hour)]
        
    return selected_data 

#pond radiation

def calculate_Qrap(T_wk):
    
    #Qra,p = -εwσTp4S 
    ew = 0.97 #water emissivity

    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4
    
    #roh = roh1 #joule/hr*m2*K4
    SA = 4047 #m2 area
    Qrap = -ew * roh1 * SA * (T_wk**4) *3600
    
    return Qrap

#solar radiation
#Qra,s = (1-fa)HsS

def calculate_Qras(day_argue, hour):
    daily_data = read_dataline(day_argue, hour)
    solrad = float(daily_data['SRAD']) #/ 3600
    
    fa = 0 #% algae absorption

    Hs =  solrad #solar radiation Wh/m2
    
    SA = 4047 #m2 area
    Qras = (1-fa) * Hs* SA *3600
    
    return Qras

#air radiation
#Qra,a = εw εa σTa4S

def calculate_Qraa(day_argue, hour):
    daily_data = read_dataline(day_argue, hour)
    T_a = float(daily_data['T2M'])+ 273.15 #kelvin
    
    ew = 0.97 #water emissivity
    
    ea = 0.8 #air emissivity
    
    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4
    
    #roh = roh1 * 3600 #joule/day*m2*K4

    
    SA = 4047 #m2 area
    Qraa = ew * ea* roh1* (T_a**4) * SA *3600
    
    return Qraa

#evaporation
#Qevap = -meLwS 

def calculate_Qevap(day_argue, hour,T_wk):
    daily_data = read_dataline(day_argue, hour)
    T_a = float(daily_data['T2M']) +273.15#kelvin
    RH = float(daily_data['RH2M']) / 100 #needs to be value btwn 0 and 1 not percentage
    v = float(daily_data['WS2M']) #m/s
    
    Lw = 2.45 * (10**6) #water latent heat J/kg 
    #this is site specific check with Drew
    Dw = 2.4 * (10**-5) #m2/s 

    l = 63.61#pond length in m
    va = 1.5 *(10**-5) #m2/s
    
    Rel = (l*v)/va
    #print(f"Rel: {Rel}")
    
    Sch = va/Dw
    #print(f"Sch: {Sch}")
    
    #SH= 0.035 * (Rel**0.8) * (Sch**1/3)
    
    if Rel >= (4*(10**5)):
        SH= 0.035 * (Rel**0.8) * (Sch**1/3)
    elif Rel <= (4*(10**5)):
        SH= 0.628 * (Rel**0.5) * (Sch**1/3)
    #print(f"f:{SH}")
    
    K = (SH * Dw)/l
    #print(f"K: {K}")
    
    R = 8.314 # m3/mol K                
    Pw = 3385.5 * cmath.exp(-8.0929+0.97608*((T_wk +42.607 -273.15)**0.5))
    Pa = 3385.5 * cmath.exp(-8.0929+0.97608*((T_a +42.607 -273.15)**0.5))
    Mw = 0.018 #kg/mol
    
    me = K *((Pw/T_wk) - ((RH*Pa)/T_a)) *(Mw/R)
    #print(f"me: {me}")
    
    SA = 4047 #m2 area
    Qevap = -me * Lw * SA *3600
    #print(f"Qevp: {Qevap}")
    
    return Qevap

#convection 
#Qconv = hconv(Ta – Tp)S
def calculate_Qconv(day_argue, hour):
    daily_data = read_dataline(day_argue, hour)
    T_a = float(daily_data['T2M'])+273.15 #kelvin
    
    v = float(daily_data['WS2M']) #m/s
    l = 63.61#pond length in m
    va = 1.5 *(10**-5) #m2/s
    alpha = 2.2 * (10**-5)
    lambda_a = 2.6 * (10 **-2)
    
    Pr = va/alpha
    
    Rel = (l*v)/va
    
    Nu = 0.035* (Rel**0.8) * (Pr**(1/3))
    
    h = lambda_a * Nu / l
    SA = 4047 #m2 area
    
    Qconv = h * (T_a-T_wk)* SA *3600
   
    return Qconv


# loop for energy flux equation hourly
def main_simulation_loop():
    element_df = []
    global T_wk
    count = 0
    for day_argue in list(range(0, numberDays)):
        
        for hour in list(range(0, 24)):
            
            count = count + 1
            
            print(f"Iteration {count} start - T_wk: {T_wk}")

            Qrap = calculate_Qrap(T_wk)
            #print(f'Qrap: {Qrap}')
            Qras = calculate_Qras(day_argue, hour)
            #print(f'Qras: {Qras}')
            Qraa = calculate_Qraa(day_argue, hour)
            #print(f'Qraa: {Qraa}')  
            Qevap = calculate_Qevap(day_argue, hour,T_wk)
            #print(f'Qevap: {Qevap}')
            Qconv = calculate_Qconv(day_argue, hour)
            #print(f'Qconv: {Qconv}')

            Qnet = Qrap + Qras + Qraa + Qevap + Qconv #+ Qi 
            
            #print(f'iteration: {count}, Qnet: {Qnet}')
            
            rate_temp =Qnet / (water_density * Volume * specific_heat) #NOT ACTUALLY A RATE
            print(f'iteration: {count}, rate_temp: {rate_temp}')
            
            T_wk_new = rate_temp + T_wk

            T_wk_vec.append(T_wk_new)
    
            T_wk = T_wk_new 
            #print(f'iteration: {count}, T_wk: {T_wk}')
            
            element_df.append([Qrap, Qras, Qraa, Qevap, Qconv, Qnet, T_wk])
            
            hourly_output = pd.DataFrame(element_df)
            #hourly_series = pd.DataFrame(hourly_output, columns=["Qrap","Qras","Qraa","Qevap","Qconv","Qnet","T_wK"])
                
    hourly_output.to_csv("/Users/drewr/RemoteData/ACToday/Bangladesh/BDaquaculture/sensitivity_analysis_Bechet/model_outputs.csv")
    return T_wk_vec 

    
def modelOutputs(T_wk_vec,data):  
    T_wK = np.array(T_wk_vec)
    
    T_wC = T_wK.astype(float) - 273.15

    df = pd.DataFrame(T_wC).rename(columns={0:'T_wC'})
    
    df1= pd.concat([data, df], axis = 1).drop(['T2M','SRAD','WS2M','RH2M'], axis=1)
    
    df1 = df1[df1['T_wC'].notna()]
    
    max_temp = df1.groupby('DAY').max()
    min_temp = df1.groupby('DAY').min()
    daily_data = data.groupby('DAY').mean()
    
    #df1.to_csv('simulated_hourly.csv',index=False)
    
    plt.plot(max_temp.index, max_temp['T_wC'], label="max water temp (modelled)")
    plt.plot(min_temp.index, min_temp['T_wC'], label="min water temp (modelled)")
    plt.plot(daily_data.index, daily_data['T2M'], label="average air temp (measured)")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare daily model data to avg observed air temp")
    plt.legend()
    plt.show()
    
def modelVSobserved(T_wk_vec, observed):
    T_wK = np.array(T_wk_vec)
    
    T_wC = T_wK.astype(float) - 273.15

    df = pd.DataFrame(T_wC).rename(columns={0:'T_wC'})
    
    df1= pd.concat([data, df], axis = 1).drop(['T2M','SRAD','WS2M','RH2M'], axis=1)
    
    df1 = df1[df1['T_wC'].notna()]
    
    max_temp = df1.groupby('DAY').max()
    min_temp = df1.groupby('DAY').min()
    
    #df1.to_csv('simulated_hourly.csv',index=False)
    
    plt.plot(max_temp.index, max_temp['T_wC'], label="max water temp (modelled)")
    plt.plot(min_temp.index, min_temp['T_wC'], label="min water temp (modelled)")
    plt.plot(observed.index, observed['avg_water_temp'], label="average water temp (observed)")
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare daily model data to avg observed temp")
    plt.legend()
    plt.show()    
 

if __name__ == '__main__':
    main_simulation_loop()
    modelOutputs(T_wk_vec,data)
    modelVSobserved(T_wk_vec, observed)
  
# water_density * Volume * specific_heat * dTp/dt 
#= Qrap + Qras + Qraa + Qevap + Qconv + Qi 

#plt.plot(joined.index, joined['T_wK'])
#plt.title('Temperature hourly')
#plt.xlabel('hours from start')
#plt.ylabel('Temp (K)')
#plt.show()

