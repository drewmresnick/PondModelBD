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

pond_depth = 1.5204 #meters
water_density = 997 #kg/m3
T_wk = 287.51 #first day water temp at khulna 
T_wk_vec = []

specific_heat = 4.18 * (10**3)
Volume = 6153.05 #m3
area = 4047 #m2

T_wc_0 = 19.3


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
data = pd.read_csv("bechet_etal_input.csv") 

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
    solrad = float(daily_data['SRAD'])
    
    fa = 0 #% algae absorption

    Hs =  solrad #* 3600 #solar radiation W/m2 or joule/second*m2
    
    SA = 4047 #m2 area
    Qras = (1-fa) * Hs* SA *3600
    
    return Qras

#air radiation
#Qra,a = εw εa σTa4S

def calculate_Qraa(day_argue, hour):
    daily_data = read_dataline(day_argue, hour)
    T_a = float(daily_data['T2M'])+ 273.15 #check this #kelvin
    
    ew = 0.97 #% algae absorption
    
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
    RH = float(daily_data['RH2M'])
    v = float(daily_data['WS2M']) #*3600 #m/s
    
    Lw = 2.45 * (10**6) #water latent heat J/kg 
    #this is site specific check with Drew
    Dw = 2.4 * (10**-5) #*3600 #m/s 

    l = 63.61#pond length in m
    va = 1.5 *(10**-5) #*3600  #m2/s
    
    Rel = (l*v)/va
    
    Sch = va/Dw
    
    SH= 0.035 * (Rel**0.8) * (Sch**1/3)
    
    K = (SH * Dw)/l
    
    R = 8.314 # m3/mol K                
    Pw = 3385.5 * cmath.exp(-8.0929+0.97608*((T_wk +42.607 -273.15)**0.5))
    Pa = 3385.5 * cmath.exp(-8.0929+0.97608*((T_a +42.607 -273.15)**0.5))
    Mw = 0.018 #kg/mol
    
    me = K *((Pw/T_wk) - ((RH*Pa)/T_a)) *(Mw/R)
 
    SA = 4047 #m2 area
    Qevap = -me * Lw * SA *3600
    
    return Qevap

#convection 
#Qconv = hconv(Ta – Tp)S
def calculate_Qconv(day_argue, hour):
    daily_data = read_dataline(day_argue, hour)
    T_a = float(daily_data['T2M'])+273.15 #kelvin
    
    v = float(daily_data['WS2M']) #m/s
    l = 63.61#pond length in m
    va = 1.5 *(10**-5) #*3600  #m2/s
    alpha = 2.2 * (10**-5)
    lambda_a = 2.6 * (10 **-2)
    
    Pr = va/alpha
    
    Rel = (l*v)/va
    
    Nu = 0.035* (Rel**0.8) * (Pr**(1/3))
    
    h = lambda_a * Nu / l
    SA = 4047 #m2 area
    
    Qconv = h * (T_a-T_wk)* SA *3600
   
    return Qconv

#inflow heat flux
#Qi = water_density *specific_heat * inflow_rate (Ti - T_wk)
def calculate_Qi(day_argue, hour):
    qi = 1.5 * (10**-5)
    Qi = water_density *specific_heat * qi * T_wk *3600#(Ti - T_wk)
   
    return Qi

# loop for energy flux equation hourly
def main_simulation_loop():
    
    global T_wk
    count = 0
    for day_argue in list(range(1, 1096)):
        
        for hour in list(range(0, 24)):
            
            count = count + 1

            print(f"Iteration {count} start - T_wk: {T_wk}")

            Qrap = calculate_Qrap(T_wk)
            print(f'Qrap: {Qrap}')
            Qras = calculate_Qras(day_argue, hour)
            print(f'Qras: {Qras}')
            Qraa = calculate_Qraa(day_argue, hour)
            print(f'Qraa: {Qraa}')  
            Qevap = calculate_Qevap(day_argue, hour,T_wk)
            print(f'Qevap: {Qevap}')
            Qconv = calculate_Qconv(day_argue, hour)
            print(f'Qconv: {Qconv}')
            Qi = calculate_Qi(day_argue, hour)
            print(f'Qi: {Qi}')
            Qnet = Qrap + Qras + Qraa + Qevap + Qconv + Qi 
            
            print(f'iteration: {count}, Qnet: {Qnet}')
            
            #T_wC = T_wk - 273.15 #change to degree celcius 
            
            rate_temp =Qnet / (water_density * Volume * specific_heat) 
            print(f'iteration: {count}, rate_temp: {rate_temp}')
            
            T_wk_new = rate_temp *24  #T_wk + (rate_temp * 1)

            
            #add T_w to a list somehow
            T_wk_vec.append(T_wk_new)
    
            T_wk = T_wk_new 
            print(f'iteration: {count}, T_wk: {T_wk}')


    print(T_wk_vec)
    
    
    T_wK = np.array(T_wk_vec)


    df = pd.DataFrame(T_wK)
    
    df1= pd.concat([data, df], axis = 1)
    
    df1.to_csv('simulated_hourly.csv',index=False)

    plt.plot(T_wK)
    plt.show()


if __name__ == '__main__':
    main_simulation_loop()
  
# water_density * Volume * specific_heat * dTp/dt 
#= Qrap + Qras + Qraa + Qevap + Qconv + Qi 




