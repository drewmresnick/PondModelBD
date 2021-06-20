# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#             Single layer mixed pond
#             morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity

import numpy as np
import datetime as dt
import pandas as pd
import math


#Setting constant values 

pi = 3.1415 
sigma = 2.07e-7 ##stefan boltzman constant
N = 5.0593 ##empirical coefficient unit m^-2km^-1 mmHg^-1
water_heat_capacity = 4.184 #joules
pond_depth = 1.5204 #meters
water_density = 997 #kg/m3
T_wk = 287.15 #first day water temp at khulna 
srad_names = ['SRAD00', 'SRAD03', 'SRAD06', 'SRAD09','SRAD12', 'SRAD15', 'SRAD18', 'SRAD21']

# lambda, solar altitude angle
#for lambda install and import package pysolar to use function solar.get_altitude
#for now use values for lambda from Shammuns code

lambda_s = [0,0,1,30.41,54.59,36.7,1,0]

#should we set sequence values as arrays instead of lists - for efficiency? 
#for this i think a list will suffice 
#lambda_s = np.array(lambda_s)

#setting variables
#time_of_day = [0,3,6,9,12,15,18,21]
time_of_day = np.arange(0,24,3) #array of 3 hourly windows in a day 

#reading in input csv file as array (question for drew: let me know if you want to work with dataframe instead)
# I separated the two districts into two files for ease for now, not sure if we want to keep them together

#open csv file using pandas to create pandas dataframe 
data = pd.read_csv("input_data_for_simulation_2017_2019_khulna.csv") 
air_temp_data = pd.read_csv("diurnal_air_temp_khulna_daily.csv") #this value is in kelvin
relative_humidity = pd.read.csv("khulna_relativeHumidity_2m.csv") 


#create a function to get month and year based on integer sequence input
#using package datetime makes it easier to get month, year (this is also dependant on the the way the data
# file is set up)
#data.day[i] needs= float for timedelta() func; (data.day[i] = int in pandas df) 
def find_day_month_year(input_day, start_day = dt.date(2016,12,31)):
    computed_day = start_day + dt.timedelta(days = float(input_day))
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)

    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later

def read_dataline(day_argue):
    
    day, day_mon_year = find_day_month_year(day_argue)
    year = day_mon_year.year
    
    selected_data = data[(data['day']== day) & (data['year'] == year)]
            
    return selected_data      
             
#setting functions for energy variables in the energy flux equation
#calculate phi_sn pr penetrating short-wae solar radiation

def calculate_phi_sn(day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['wind_speed_2m']
    
    R_s = 0.38 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed #wind velocity in m/s
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = daily_data['SRAD']  #Kj/m2/hr

    phi_sn = float(phi_s * (1-R))
    
    return phi_sn

#create function to open air_temp file for day month and year

def read_air_temp(day_argue):
    day, day_mon_year = find_day_month_year(day_argue)
    year = day_mon_year.year
    
    selected_air_data = air_temp_data[(air_temp_data['day']== day) & (air_temp_data['year'] == year)]
  
    return selected_air_data 

#creating a function for phi_at atmospheric radiation following the equation in variables excel sheet
#shammun includes cloud fraction in the equation

def calculate_phi_at(day_argue):
    air_temp_line = read_air_temp(day_argue)
    T_ak = air_temp_line['avg_temp'] #in kelvin
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))
    r = 0.03 # reflectance of the water surface to longwave radiation
    phi_at = float((1-r)*e*sigma*((T_ak)**4))

    return(phi_at)

#create function for phi_ws water surface radiation
#this equation need water surface temp T_wk (kelvin), this will be initialized using the t-1 timestep value
# from the water temp data file (ideally Jan 1st 2018, morning water temp)

def calculate_phi_ws(T_wk, day_argue):
    

# set T_wk such that it reads the final output water temp from results in a loop
    
    phi_ws = float(0.97 * sigma * ((T_wk)**4))

    return(phi_ws)

#create function for phi_e evaporative heat loss
#here, we use average dailt dew point temp in place of relative humidity values

def calculate_phi_e(T_wk,day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['wind_speed_2m']

    W_2 = wind_speed * 3.6
    air_temp_line = read_air_temp(day_argue)
    T_ak = air_temp_line['avg_temp'] #kelvin
    T_ac = T_ak -273.15 #degree celcius

# e_s, saturated vapor pressure needs to be in T_wc deg celcius

    T_wc = T_wk - 273.15
    e_s = 25.374 * math.exp(17.62 - 5271/T_wc)
    
    RH = relative_humidity[(relative_humidity['day']== day_argue)]

    RH = RH['RH2M']

# e_a, water vapor pressure above the pond surface; unit mmHg
    
    e_a = RH * 25.374 * math.exp(17.62 - 5271/T_ac)     

    phi_e = float(N* W_2 * (e_s- e_a))
    return(phi_e)

#create function for phi_c sensible heat transfer

def calculate_phi_c(T_wk, day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['wind_speed_2m']

    W = float(wind_speed) #m/s per C&B paper
    
    air_temp_line = read_air_temp(day_argue)
    T_ak = air_temp_line['avg_temp'] #kelvin
    
    T_wc = T_wk - 273.15 #convert to deg celcius
    T_ac = T_ak - 273.15 

    phi_c = float(1.5701 * W * (T_wc-T_ac))

    return(phi_c)

############### Creating simulation loop for daily values #############################
# Energy Flux equation: phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c   
# Heat at t-1 time step: H_t_1 = T_wk * water_heat_capacity * water_density
# Heat at t: H_t = H_t_1 + phi_net
# T_w = H_t/ (water_heat_capacity * water_density)

# loop for energy flux equation 

for day_argue in list(range(1, 731)):
                     
    for hour_period in list(range(1,9)):
        
        phi_sn = calculate_phi_sn(day_argue, hour_period)
        phi_at = calculate_phi_at(day_argue, hour_period)
        phi_ws = calculate_phi_ws(T_wk, day_argue, hour_period)
        phi_e = calculate_phi_e(T_wk, day_argue, hour_period)
        phi_c = calculate_phi_c(T_wk, day_argue, hour_period)
        
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c 

        print(phi_net)



phi_sn = calculate_phi_sn(1, 3)
phi_at = calculate_phi_at(1, 3)
phi_ws = calculate_phi_ws(T_wk, 1, 3)
phi_e = calculate_phi_e(T_wk, 1, 3)
phi_c = calculate_phi_c(T_wk, 1, 3)
        
phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c
    