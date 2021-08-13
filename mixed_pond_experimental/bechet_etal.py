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
import matplotlib.pyplot as plt

#Setting constant values 


water_heat_capacity = 4.184 #joules
pond_depth = 1.5204 #meters
water_density = 997 #kg/m3
T_wk = 287.51 #first day water temp at khulna 
T_wC_vecmin = []
T_wC_vecmax = []

volume = 6153.05 #m3
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
#Qcond: conductive flux with ground at pond bottom (W)
#Qi: heat flux associated with water inflow (W)
#Qr: heat flux induced by rain (W)


#open csv file using pandas to create pandas dataframe 
data = pd.read_csv("new_data.csv") 

def find_day_month_year(input_day, start_day = dt.date(2017,12,31)):
    computed_day = start_day + dt.timedelta(days = float(input_day))
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)

    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later

def read_dataline(day_argue):
    
    day, day_mon_year = find_day_month_year(day_argue)
    year = day_mon_year.year
    
    selected_data = data[(data['DOY']== day) & (data['YEAR'] == year)]
            
    return selected_data 

#pond radiation

def calculate_Qrap(T_wk):
    
    #Qra,p = -εwσTp4S 
    ew = 0.97 #water emissivity

    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4
    
    roh = roh1 * 86400 #joule/day*m2*K4
    SA = 4047 #m2 area
    Qrap = -ew * roh * SA * (T_wk**4)
    
    return Qrap

#solar radiation
#Qra,s = (1-fa)HsS

def calculate_Qras(day_argue):
    daily_data = read_dataline(day_argue)
    solrad = float(daily_data['SRAD'])
    
    fa = 2.5 #% algae absorption

    Hs =  solrad #solar radiation W/m2 or joule/second*m2
    
    SA = 4047 #m2 area
    Qras = (1-fa) * Hs* SA
    
    return Qras

#air radiation
#Qra,a = εw εa σTa4S

def calculate_Qraa(day_argue):
    daily_data = read_dataline(day_argue)
    T_a = float(daily_data['air_temp_max']) #check this #kelvin
    
    ew = 0.97 #% algae absorption
    
    ea = 0.8 #air emissivity
    
    roh1 = 5.67 * (10**(-8)) #Wm-2K-4 or Joule/second*m2K4
    
    roh = roh1 * 86400 #joule/day*m2*K4

    
    SA = 4047 #m2 area
    Qraa = ew * ea* roh* (T_a**4) * SA
    
    return Qraa

#evaporation
#Qevap = -meLwS 

def calculate_Qevap(day_argue):
    daily_data = read_dataline(day_argue)
    T_a = float(daily_data['air_temp_max']) #kelvin
    RH = float(daily_data['RH'])
    
    Lw = 2.45 * (10**6) #water latent heat J/kg 
    #this is site specific check with Drew
    Dw = 2.4 * (10**-5) #m/s 
    K = (SH * Dw)/L
    
    R = 8.314 #Pa m3/mol K                
    Pw = 998 #kg/m3
    Pa = 1.9 * (10**3) #kg/m3
    Mw = 0.018 #kg/mol
    
    me = K *((Pw/T_wk) - ((RH*Pa)/T_a)) *(Mw/R)

    SA = 4047 #m2 area
    Qevap = -me * Lw * SA 
    
    return Qevap

#convection 
#Qconv = hconv(Ta – Tp)S

#conduction
#Qcond = KsSA(dTs/dz)

#inflow heat flux
#Qi = water_density *specific_heat * inflow_rate (Ti - T_wk)

#rain heat flux
#Qr = water_density *specific_heat *rainwaterflow (T_a -T_wk)SA


# water_density * Volume * specific_heat * dTp/dt 
#= Qrap + Qras + Qraa + Qevap + Qconv + Qcond + Qi + Qr




