# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#             Single layer mixed pond


import numpy as np
import datetime as dt
import pandas as pd
import math
import matplotlib.pyplot as plt

#Setting constant values 

pi = 3.1415 
sigma = 2.07e-7 ##stefan boltzman constant
N = 5.0593 ##empirical coefficient unit m^-2km^-1 mmHg^-1
water_heat_capacity = 4.184 #joules
pond_depth = 1.5204 #meters
water_density = 997 #kg/m3
T_wk = 287.51 #first day water temp at khulna 
T_wC_vecmin = []
T_wC_vecmax = []
srad_names = ['SRAD00', 'SRAD03', 'SRAD06', 'SRAD09','SRAD12', 'SRAD15', 'SRAD18', 'SRAD21']
volume = 6153.05 #m3
area = 4047 #m2
t = 24 #hrs
T_wc_0 = 19.3

#open csv file using pandas to create pandas dataframe 
data = pd.read_csv("new_data.csv") 
relative_humidity = pd.read_csv("khulna_relativeHumidity_2m.csv") 
observedtemp = pd.read_csv('Air_water_temp_dataset_Sylhet_Khulna_modified.csv')

#create a function to get month and year based on integer sequence input
#using package datetime makes it easier to get month, year (this is also dependant on the the way the data
# file is set up)
#data.day[i] needs= float for timedelta() func; (data.day[i] = int in pandas df) 
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
             
#setting functions for energy variables in the energy flux equation
#calculate phi_sn pr penetrating short-wae solar radiation


#############Minimum###############

def calculate_phi_sn(day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = float(daily_data['WS2M'])
    
    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed  #wind velocity in m/s
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = float(daily_data['SRAD_kj'])  #Kj/day

    phi_sn = phi_s * (1-R)
    
    
    return phi_sn


#create function to open air_temp file for day month and year

#creating a function for phi_at atmospheric radiation following the equation in variables excel sheet
#shammun includes cloud fraction in the equation


def calculate_phi_at(day_argue):
    daily_data = read_dataline(day_argue)
    
    T_ak = float(daily_data['air_min']) +273.15
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))

    r = 0.035 # reflectance of the water surface to longwave radiation
    phi_at = (1-r)*e*sigma*((T_ak)**4)
    

    return(phi_at)

#create function for phi_ws water surface radiation
#this equation need water surface temp T_wk (kelvin), this will be initialized using the t-1 timestep value
# from the water temp data file (ideally Jan 1st 2018, morning water temp)

def calculate_phi_ws(T_wk, day_argue):
    

# set T_wk such that it reads the final output water temp from results in a loop
    
    phi_ws = 0.97 * sigma * ((T_wk)**4)
    


    return(phi_ws)

#create function for phi_e evaporative heat loss
#here, we use average dailt dew point temp in place of relative humidity values

def calculate_phi_e(T_wk,day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = float(daily_data['WS2M'])

    W_2 = wind_speed 
    

    T_ak = float(daily_data['air_min']) +273.15

    
# e_s, saturated vapor pressure needs to be in T_wc deg celcius

    
    e_s = 25.374 * math.exp(17.62 - 5271/T_wk)
    
    RH = float(daily_data['RH2M']) 


# e_a, water vapor pressure above the pond surface; unit mmHg
    
    e_a = RH * 25.374 * math.exp(17.62 - 5271/T_ak)     

    phi_e = float(N* W_2 * (e_s- e_a))
    
    
    
    return(phi_e)

#create function for phi_c sensible heat transfer

def calculate_phi_c(T_wk, day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['WS2M']

    W = float(wind_speed)  #m/s per C&B paper
    
    T_ac = float(daily_data['air_min'])
    
    T_wc = T_wk - 273.15 #convert to deg celcius
    
    phi_c = float(1.5701 * W * (T_wc-T_ac))
    
 

    return(phi_c)

############### Creating simulation loop for daily values #############################
# Energy Flux equation: phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c   
# Heat at t-1 time step: H_t_1 = T_wk * water_heat_capacity * water_density
# Heat at t: H_t = H_t_1 + phi_net
# T_w = H_t/ (water_heat_capacity * water_density)

# loop for energy flux equation 
def main_simulation_loop():
    
    global T_wk
    count = 0
    for day_argue in list(range(1, 558)):
        
        
        count = count + 1

        print(f"Iteration {count} start - T_wk: {T_wk}")

        phi_sn = calculate_phi_sn(day_argue)
        print(f'phi_sn: {phi_sn}')
        phi_at = calculate_phi_at(day_argue)
        print(f'phi_at: {phi_at}')
        phi_ws = calculate_phi_ws(T_wk, day_argue)
        print(f'phi_ws: {phi_ws}')  
        phi_e = calculate_phi_e(T_wk, day_argue)
        print(f'phi_e: {phi_e}')
        phi_c = calculate_phi_c(T_wk, day_argue)
        print(f'phi_c: {phi_c}')
        
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c 
        
       

        print(f'iteration: {count}, phi_net: {phi_net}')
        
        T_wC = T_wk - 273.15 #change to degree celcius   


        #H_t_1 = T_wC * volume * water_heat_capacity * water_density
        #check if K or C
        #print(f'iteration: {count}, H_t_1: {H_t_1}')

        #H_t = H_t_1 + (phi_net * area)
        T_w = T_wc_0 + ((phi_net * area)/ (volume * water_heat_capacity * water_density))
                    
        print(f'iteration: {count}, T_w: {T_w}')

        #add T_w to a list somehow
        T_wC_vecmin.append(T_w)

        T_wk = T_w + 273.15 #convert back to kelvin
        print(T_wk)



    print(T_wC_vecmin)
    
    T_wC = np.array(T_wC_vecmin)

    #df = pd.DataFrame(T_wC)
    
    #df1= pd.concat([data, df], axis = 1)
    
    #df1.to_csv('Water_temp_daily.csv',index=False)

    plt.plot(T_wC, label = 'Simulated Water temp')
    plt.plot(observedtemp['min_air_temp_khu'], label = 'Observed Minimum Air temp')
    plt.plot(observedtemp['morning_water_temp_khu'], label = 'Observed Minimum Water temp')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()



if __name__ == '__main__':
    main_simulation_loop()
    


#############Maximum###############

def calculate_phi_sn(day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = float(daily_data['WS2M'])
    
    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed  #wind velocity in m/s
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = float(daily_data['SRAD_kj'])  #Kj/day

    phi_sn = phi_s * (1-R)
    
    
    return phi_sn

#create function to open air_temp file for day month and year

#creating a function for phi_at atmospheric radiation following the equation in variables excel sheet
#shammun includes cloud fraction in the equation


def calculate_phi_at(day_argue):
    daily_data = read_dataline(day_argue)
    
    T_ak = float(daily_data['air_max']) +273.15
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))

    r = 0.035 # reflectance of the water surface to longwave radiation
    phi_at = (1-r)*e*sigma*((T_ak)**4)
    

    return(phi_at)

#create function for phi_ws water surface radiation
#this equation need water surface temp T_wk (kelvin), this will be initialized using the t-1 timestep value
# from the water temp data file (ideally Jan 1st 2018, morning water temp)

def calculate_phi_ws(T_wk, day_argue):
    

# set T_wk such that it reads the final output water temp from results in a loop
    
    phi_ws = 0.97 * sigma * ((T_wk)**4)
    


    return(phi_ws)

#create function for phi_e evaporative heat loss
#here, we use average dailt dew point temp in place of relative humidity values

def calculate_phi_e(T_wk,day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = float(daily_data['WS2M'])

    W_2 = wind_speed 
    

    T_ak = float(daily_data['air_max']) +273.15

    
# e_s, saturated vapor pressure needs to be in T_wc deg celcius

    
    e_s = 25.374 * math.exp(17.62 - 5271/T_wk)
    
    RH = float(daily_data['RH2M']) 


# e_a, water vapor pressure above the pond surface; unit mmHg
    
    e_a = RH * 25.374 * math.exp(17.62 - 5271/T_ak)     

    phi_e = float(N* W_2 * (e_s- e_a))
    
    
    
    return(phi_e)

#create function for phi_c sensible heat transfer

def calculate_phi_c(T_wk, day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['WS2M']

    W = float(wind_speed)  #m/s per C&B paper
    
    T_ac = float(daily_data['air_max'])
    
    T_wc = T_wk - 273.15 #convert to deg celcius
    
    phi_c = float(1.5701 * W * (T_wc-T_ac))
    
 

    return(phi_c)

############### Creating simulation loop for daily values #############################
# Energy Flux equation: phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c   
# Heat at t-1 time step: H_t_1 = T_wk * water_heat_capacity * water_density
# Heat at t: H_t = H_t_1 + phi_net
# T_w = H_t/ (water_heat_capacity * water_density)

# loop for energy flux equation 
def main_simulation_loop():
    
    global T_wk
    count = 0
    for day_argue in list(range(1, 558)):
        
        
        count = count + 1

        print(f"Iteration {count} start - T_wk: {T_wk}")

        phi_sn = calculate_phi_sn(day_argue)
        print(f'phi_sn: {phi_sn}')
        phi_at = calculate_phi_at(day_argue)
        print(f'phi_at: {phi_at}')
        phi_ws = calculate_phi_ws(T_wk, day_argue)
        print(f'phi_ws: {phi_ws}')  
        phi_e = calculate_phi_e(T_wk, day_argue)
        print(f'phi_e: {phi_e}')
        phi_c = calculate_phi_c(T_wk, day_argue)
        print(f'phi_c: {phi_c}')
        
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c 
        
       

        print(f'iteration: {count}, phi_net: {phi_net}')
        
        T_wC = T_wk - 273.15 #change to degree celcius   


        #H_t_1 = T_wC * volume * water_heat_capacity * water_density
        #check if K or C
        #print(f'iteration: {count}, H_t_1: {H_t_1}')

        #H_t = H_t_1 + (phi_net * area)
        T_w = T_wc_0 + ((phi_net * area)/ (volume * water_heat_capacity * water_density))
                    
        print(f'iteration: {count}, T_w: {T_w}')

        #add T_w to a list somehow
        T_wC_vecmin.append(T_w)

        T_wk = T_w + 273.15 #convert back to kelvin
        print(T_wk)



    print(T_wC_vecmin)
    
    T_wC = np.array(T_wC_vecmin)

    #df = pd.DataFrame(T_wC)
    
    #df1= pd.concat([data, df], axis = 1)
    
    #df1.to_csv('Water_temp_daily.csv',index=False)

    plt.plot(T_wC, label = 'Simulated Water temp')
    plt.plot(observedtemp['max_air_temp_khu'], label = 'Observed Maximum Air temp')
    plt.plot(observedtemp['afternoon_water_temp_khu'], label = 'Observed Maximum Water temp')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()



if __name__ == '__main__':
    main_simulation_loop()
    
