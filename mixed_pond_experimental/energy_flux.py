# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#             Single layer mixed pond
#             morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity

import numpy as np
import datetime as dt
import csv
import pandas as pd

#Setting constant values 

pi = 3.1415 
sigma = 2.07*10**(-7)  ##stefan boltzman constant
N = 5.0593 ##empirical coefficient 
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
    wind_speed = int(float(daily_data.wind_speed_2m))
    #solar_daily?
    
    
    lambda_value = lambda_s[hour_period] #remember hour period integer corresponds to lamba value
    R_s = 2.2*((180*lambda_value)/pi)**(-0.97)
    
    W_z = wind_speed * 3.6
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = int(float(daily_data[8+hour_period]))   #8th column plus number of hour gets us sol rad for that hour
    #have to convert string to integer and then to float everytime is there a better way to handle this? (question for drew)

    phi_sn = phi_s * (1-R)
    
    return phi_sn
