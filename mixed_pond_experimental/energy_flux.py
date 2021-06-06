# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#             Single layer mixed pond
#             morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity

import numpy as np
import datetime as dt
import csv
import pandas as pd
import math

#Setting constant values 

pi = 3.1415 
sigma = 2.07*10**(-7)  ##stefan boltzman constant
N = 5.0593 ##empirical coefficient unit m^-2km^-1 mmHg^-1
water_heat_capacity = 4.184 #joules
pond_depth = 1.5204 #meters
water_density = 997 #kg/m3

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
air_temp_data = pd.read_csv("diurnal_air_temp_khulna.csv") 

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

def calculate_phi_sn(day_argue, hour_period):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['wind_speed_2m']
    #solar_daily?
    
    
    lambda_value = lambda_s[hour_period] #remember hour period integer corresponds to lamba value
    R_s = 2.2*((180*lambda_value)/pi)**(-0.97)
    
    W_z = wind_speed * 3.6
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = int(float(daily_data[8+hour_period]))   #8th column plus number of hour gets us sol rad for that hour units watts/m square
    #have to convert string to integer and then to float everytime is there a better way to handle this? (question for drew)

    phi_sn = phi_s * (1-R)
    
    return phi_sn

#create function to open air_temp file for day month and year

def read_air_temp(day_argue,hour_period):
    day, day_mon_year = find_day_month_year(day_argue)
    year = day_mon_year.year
    
    time = time_of_day[hour_period] 
    
    selected_air_data = air_temp_data[(air_temp_data['day']== day) & (air_temp_data['year'] == year)]
    selected_air_data = selected_air_data[(selected_air_data['time']== time)]        
    return selected_air_data  


#creating a function for phi_at atmospheric radiation following the equation in variables excel sheet
#shammun includes cloud fraction in the equation

def calculate_phi_at(day_argue, hour_period):
    air_temp_line = read_air_temp(day_argue, hour_period)
    T_ak = air_temp_line['air_temp'] #in kelvin
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))
    r = 0.03 # reflectance of the water surface to longwave radiation
    sigma = 2.07 * (10 ** (-7)) # Stefan-Boltzman constant, unit Kg/m2/hr/K^4
    phi_at = (1-r)*e*sigma*((T_ak)**4)

    return(phi_at)

#create function for phi_ws water surface radiation
#this equation need water surface temp T_wk (kelvin), this will be initialized using the t-1 timestep value
# from the water temp data file (ideally Jan 1st 2018, morning water temp)

def calculate_phi_ws(T_wk, day_argue, hour_period):
    
    T_wk = 291.65  #first value

# set T_wk such that it reads the final output water temp from results in a loop
    
    phi_ws = 0.97 * sigma * ((T_wk)**4)

    return(phi_ws)

#create function for phi_e evaporative heat loss
#here, we use average dailt dew point temp in place of relative humidity values

def calculate_phi_e(day_argue, hour_period):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['wind_speed_2m']

    W_2 = wind_speed * 3.6

    T_min_air = daily_data['min_temp']  #already in kelvin

    T_d = T_min_air - 275.15 # T_d is the average daily dew-point temperature.From page 235 of the Culberson paper.

# e_s, saturated vapor pressure at T_wc or T_wk; unit mmHg
    T_wk = 291.65 #first value

    e_s = 25.374 * math.exp(17.62 - 5271/T_wk)

# e_a, water vapor pressure above the pond surface; unit mmHg
#e(millibars) = 6.1078 exp( (17.269*T) / (237.3+T) )
          #where,
#e is saturated vapor pressure in millibars
#T is temperature in degrees C
    
    phi_e = N* W_2 * (e_s- e_a)
    return(phi_e)

#create function for phi_c sensible heat transfer

def calculate_phi_c(day_argue, hour_period):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['wind_speed_2m']

    W = wind_speed * 3.6 # Convert ms-1 to Kmhr-1 #check units for all variables ask drew

    air_temp_line = read_air_temp(day_argue, hour_period)
    T_ak = air_temp_line['air_temp'] #already in kelvin

    T_wk = 291.65 #first value

    phi_c = 1.5701 * W * (T_wk-T_ak)

    return(phi_c)
