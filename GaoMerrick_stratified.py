# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#             Single layer mixed pond
#             morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity

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
air_density = 1.224 #kg/m3 at sea level, 15C
#T_wk = 289.15 #first day water temp at khulna 
T_surface_wk = 289.15
T_subE1_wk = 289.15
T_subE2_wk = 289.15
T_surface_vec = []
T_subE1_vec = []
srad_names = ['SRAD00', 'SRAD03', 'SRAD06', 'SRAD09','SRAD12', 'SRAD15', 'SRAD18', 'SRAD21']
volume = 6153.05 #m3 
area = 4047 #m2
t = 24 #hrs
element_depths = [0,5,10,20,30,40,50]

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
filesPath = input("Input file path to where data files are located: ")
#open csv file using pandas to create pandas dataframe 
data = pd.read_csv(f"{filesPath}input_data_for_simulation_2018_2019_khulna.csv") 
air_temp_data = pd.read_csv(f"{filesPath}diurnal_air_temp_khulna_daily.csv") #this value is in kelvin
relative_humidity = pd.read_csv(f"{filesPath}khulna_relativeHumidity_2m.csv") 
watertemp = pd.read_csv(f'{filesPath}Realtime_watertemp.csv')

#create a function to get month and year based on integer sequence input
#using package datetime makes it easier to get month, year (this is also dependant on the the way the data
# file is set up)
#data.day[i] needs= float for timedelta() func; (data.day[i] = int in pandas df) 
def find_day_month_year(input_day, start_day = dt.date(2017,12,31)): #dt.date(2016,12,31)):
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
    wind_speed = float(daily_data['WS2M'])
    
    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed #wind velocity in m/s
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = float(daily_data['SRAD']) #Kj/m2/hr in excel file says SRAD_MJ/m2day

    phi_sn = phi_s * (1-R)
    
    return phi_sn


#function for solar irradiance at a depth z with light attenuation coefficient 
#to account for amount of light not transfered
def calculate_phi_snz(phi_sn, z, day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = float(daily_data['WS2M'])
    
    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita
    B = 0.4 
    n= 0.013
    
    W_z = wind_speed #wind velocity in m/s
    
    R= R_s *(1-0.08 * W_z)
    
    phi_snz = phi_sn*(1-R)*(1-B)*math.exp(-n*z)
    
    return phi_snz


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
    T_ak = float(air_temp_line['avg_temp']) #in kelvin
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))
    r = 0.03 # reflectance of the water surface to longwave radiation
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

    W_2 = wind_speed * 3.6
    air_temp_line = read_air_temp(day_argue)
    T_ak = float(air_temp_line['avg_temp']) #kelvin
    #T_ac = T_ak -273.15 #degree celcius

# e_s, saturated vapor pressure needs to be in T_wc deg celcius

    e_s = 25.374 * math.exp(17.62 - 5271/T_wk)
    
    RH = relative_humidity[(relative_humidity['day']== day_argue)]

    RH = float(RH['RH2M']) / 100

# e_a, water vapor pressure above the pond surface; unit mmHg
    
    e_a = RH * 25.374 * math.exp(17.62 - 5271/T_ak)     

    phi_e = float(N* W_2 * (e_s- e_a))
    return(phi_e)


#create function for phi_c sensible heat transfer
def calculate_phi_c(T_wk, day_argue):
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['WS2M']

    W = float(wind_speed) #m/s per C&B paper
    
    air_temp_line = read_air_temp(day_argue)
    T_ak = float(air_temp_line['avg_temp']) #kelvin
    
    T_wc = T_wk - 273.15 #convert to deg celcius
    T_ac = T_ak - 273.15 

    phi_c = float(1.5701 * W * (T_wc-T_ac))

    return(phi_c)


def calculate_phi_d(z,z_1,T_z_1,T_z,day_argue): #temperature for the volume element above and for the volume element (if z=2, need T z = 1 and T z = 2)
    daily_data = read_dataline(day_argue)
    wind_speed = daily_data['WS2M']
    z_half = (z - z_1) / 2 #gets the mid depth of the volume element depending on the upper and lower depth (see diagram L&P)
    C_z = 1.0*10**-3
    W = float(wind_speed) #m/s per C&B paper
    z_add = z + z_half 
    z_sub = z - z_half
    
    T_o = air_density * C_z * (W**2)
    W_v = (T_o / water_density)
    K = 6*(W**-1.84)
    U_s = 30*(W_v)
    
    E_z = ((W_v**2) / (U_s * K)) * math.exp(-K * z)
    
    phi_d = water_density * water_heat_capacity * E_z * (T_z_1 - T_z) / (z_add - z_sub)
    
    return phi_d


def calculate_phi_net(T_wk, day_argue):
    
    phi_sn = calculate_phi_sn(day_argue)
    phi_at = calculate_phi_at(day_argue)
    phi_ws = calculate_phi_ws(T_wk, day_argue)  
    phi_e = calculate_phi_e(T_wk, day_argue)
    phi_c = calculate_phi_c(T_wk, day_argue)      
    phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c
    
    return phi_net

           
    
############### Creating simulation loop for daily values #############################
# Energy Flux equation: phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c   
# Heat at t-1 time step: H_t_1 = T_wk * water_heat_capacity * water_density
# Heat at t: H_t = H_t_1 + phi_net
# T_w = H_t/ (water_heat_capacity * water_density)

# loop for energy flux equation 
def main_simulation_loop():
    
    global T_surface_wk
    global T_subE1_wk
    global T_subE2_wk
    count = 0
    for day_argue in list(range(1, 730)): #730
        
        count = count + 1
                
        T_surface_wC = T_surface_wk - 273.15
        T_subE1_wC = T_subE1_wk - 273.15
        T_subE2_wC = T_subE2_wk - 273.15
        
        #T_wC = T_wk - 273.15 #change to degree celcius  
        
        H_surface_t_1 = T_surface_wC * volume * water_heat_capacity * water_density
        H_subE1_t_1 = T_subE1_wC * volume * water_heat_capacity * water_density
        H_subE2_t_1 = T_subE2_wC * volume * water_heat_capacity * water_density
        #H_t_1 = T_wC * volume * water_heat_capacity * water_density

        #CALCS FOR EACH PHI FOR EACH LAYER 
        
        phi_net = calculate_phi_net(T_surface_wk, day_argue)
        print(f'phi net = {phi_net}')
        phi_sn = calculate_phi_sn(day_argue)
        print(f'phi sn = {phi_sn}')
        phi_sn_2 = calculate_phi_snz(phi_sn, 10, day_argue)
        print(f'phi sn2 = {phi_sn_2}')
        phi_d_2 = calculate_phi_d(10,0, T_surface_wC, T_subE1_wC, day_argue)
        print(f'phi d2 = {phi_d_2}')
        phi_sn_4 = calculate_phi_snz(phi_sn, 30, day_argue)
        print(f'phi sn4 = {phi_sn_4}')
        phi_d_4 = calculate_phi_d(30,10, T_subE1_wC, T_subE2_wC, day_argue)
        print(f'phi d4 = {phi_d_4}')
        
        #surface layer volume element = 1
        H_surface_t = H_surface_t_1 + ((phi_net - phi_sn_2 - phi_d_2) * area * t) #multiply by t because we are doing a daily timestep
        T_surface_w = H_surface_t/ (volume * water_heat_capacity * water_density)
        
        #subsurface layer volume elemt = 2
        H_subE1_t = H_subE1_t_1 + ((phi_sn_2 - phi_sn_4 + phi_d_2 - phi_d_4) * area * t) #multiply by t because we are doing a daily timestep
        T_subE1_w = H_subE1_t/ (volume * water_heat_capacity * water_density)
        
        #T_w = H_t/ (volume * water_heat_capacity * water_density)
        print(f'iteration: {count}, T_surface_w: {T_surface_w}')
        print(f'iteration: {count}, T_subE1: {T_subE1_w}')

        #add T_w to a list somehow
        T_surface_vec.append(T_surface_w)
        T_subE1_vec.append(T_subE1_w)
        
        T_surface_wk = T_surface_w + 273.15 #convert back to kelvin
        T_subE1_wk = T_subE1_w + 273.15

    
    T_surface_wC = np.array(T_surface_vec)
    T_subE1_wC = np.array(T_subE1_vec)

    df = pd.DataFrame(T_surface_wC,columns=['surface_temp'])
    df2 = pd.DataFrame(T_subE1_wC,columns=['E1_temp'])
    
    df1= pd.concat([data, df,df2], axis = 1)
    #df1 = df1.rename(columns={'0':'surface_temp', '1':'E1_temp'})
    
    df1.to_csv('GaoMerrick_output.csv',index=False)

    plt.plot(T_surface_wC, label = 'Simulated Surface Water temp')
    plt.plot(T_subE1_wC, label = 'Simulated subsurface water temp (E1)')
    plt.plot(data['tempObs_avg'], label = 'Observed Air temp')
    plt.plot(watertemp['day_avg'], label = 'Observed Water temp')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare model data to observed/measured temps")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main_simulation_loop()
    

    