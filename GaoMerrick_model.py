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
T_wk = 289.15 #first day water temp at khulna 
volume = 6153.05 #m3
area = 4047 #m2
t = 24 #hrs

T_wC_vec = []
T_wK_vec = []
phi_net_vec = []
phi_at_vec = []
phi_c_vec = []
phi_ws_vec = []
phi_e_vec = []
phi_sn_vec = []

#setting variables
#time_of_day = [0,3,6,9,12,15,18,21]
time_of_day = np.arange(0,24,3) #array of 3 hourly windows in a day 


#create a function to get month and year based on integer sequence input
#using package datetime makes it easier to get month, year (this is also dependant on the the way the data
# file is set up)
#data.day[i] needs= float for timedelta() func; (data.day[i] = int in pandas df) 
def find_day_month_year(input_day, data, start_day = dt.date(2017,12,31)): #dt.date(2016,12,31)):
    data=data
    computed_day = start_day + dt.timedelta(days = float(input_day))
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)

    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later

def read_dataline(day_argue,data):
    data=data
    day, day_mon_year = find_day_month_year(day_argue,data)
    year = day_mon_year.year
    
    selected_data = data[(data['day']== day) & (data['year'] == year)]
            
    return selected_data      
             
#setting functions for energy variables in the energy flux equation
#calculate phi_sn pr penetrating short-wae solar radiation

def calculate_phi_sn(day_argue,data):
    daily_data = read_dataline(day_argue,data)
    print(daily_data)
    wind_speed = float(daily_data['WS2M'])
    
    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed #wind velocity in m/s
    
    R= R_s *(1-0.08 * W_z)
    
    phi_s = float(daily_data['SRAD']) * (1000/24) #Kj/m2/hr in excel file says SRAD_MJ/m2day

    phi_sn = phi_s * (1-R)
    
    return phi_sn

#creating a function for phi_at atmospheric radiation following the equation in variables excel sheet
#shammun includes cloud fraction in the equation


def calculate_phi_at(day_argue,data):
    daily_data = read_dataline(day_argue,data)
    T_ak = float(daily_data['T2M'])
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))
    r = 0.03 # reflectance of the water surface to longwave radiation
    phi_at = (1-r)*e*sigma*((T_ak)**4)

    return(phi_at)

#create function for phi_ws water surface radiation
#this equation need water surface temp T_wk (kelvin), this will be initialized using the t-1 timestep value
# from the water temp data file (ideally Jan 1st 2018, morning water temp)

def calculate_phi_ws(T_wk, day_argue,data):
# set T_wk such that it reads the final output water temp from results in a loop
    
    phi_ws = 0.97 * sigma * ((T_wk)**4)

    return(phi_ws)

#create function for phi_e evaporative heat loss
#here, we use average dailt dew point temp in place of relative humidity values

def calculate_phi_e(T_wk,day_argue,data):
    daily_data = read_dataline(day_argue,data)
    wind_speed = float(daily_data['WS2M'])
    T_ak = float(daily_data['T2M'])
    RH = float(daily_data['RH2M']) / 100
    W_2 = wind_speed * 3.6

# e_s, saturated vapor pressure needs to be in T_wc deg celcius
    e_s = 25.374 * math.exp(17.62 - 5271/T_wk)

# e_a, water vapor pressure above the pond surface; unit mmHg
    e_a = RH * 25.374 * math.exp(17.62 - 5271/T_ak)     

    phi_e = float(N* W_2 * (e_s- e_a))
    return(phi_e)

#create function for phi_c sensible heat transfer

def calculate_phi_c(T_wk, day_argue,data):
    daily_data = read_dataline(day_argue,data)
    wind_speed = daily_data['WS2M']
    T_ak = float(daily_data['T2M'])

    W = float(wind_speed) #m/s per C&B paper
    
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
def main_simulation_loop(data,watertemp,filesPath):
    #global obsData
    global T_wk
    count = 0
    for day_argue in list(range(1, 730)): #730
        
        count = count + 1

        print(f"Iteration {count} start - T_wk: {T_wk}")

        phi_sn = calculate_phi_sn(day_argue,data)
        print(f'phi_sn: {phi_sn}')
        phi_at = calculate_phi_at(day_argue,data)
        print(f'phi_at: {phi_at}')
        phi_ws = calculate_phi_ws(T_wk, day_argue,data)
        print(f'phi_ws: {phi_ws}')  
        phi_e = calculate_phi_e(T_wk, day_argue,data)
        print(f'phi_e: {phi_e}')
        phi_c = calculate_phi_c(T_wk, day_argue,data)
        print(f'phi_c: {phi_c}')        
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c 

        phi_at_vec.append(phi_at)
        phi_ws_vec.append(phi_ws)
        phi_e_vec.append(phi_e)
        phi_c_vec.append(phi_c)
        phi_net_vec.append(phi_net)
        phi_sn_vec.append(phi_sn)

        print(f'iteration: {count}, phi_net: {phi_net}')
        
        T_wC = T_wk - 273.15 #change to degree celcius   


        H_t_1 = T_wC * volume * water_heat_capacity * water_density
        #check if K or C
        print(f'iteration: {count}, H_t_1: {H_t_1}')

        H_t = H_t_1 + (phi_net * area * t)
        T_w = H_t/ (volume * water_heat_capacity * water_density)
        print(f'iteration: {count}, T_w: {T_w}')

        #add T_w to a list somehow
        T_wC_vec.append(T_w)

        T_wk = T_w + 273.15 #convert back to kelvin
        T_wK_vec.append(T_wk)

    
    T_wC = np.array(T_wC_vec)
    
    fluxes = pd.DataFrame(phi_net_vec,columns=['phi_net'])
    fluxes['phi_at'] = phi_at_vec
    fluxes['phi_ws'] = phi_ws_vec
    fluxes['phi_e'] = phi_e_vec
    fluxes['phi_c'] = phi_c_vec
    fluxes['phi_sn'] = phi_sn_vec
    fluxes['phi_net'] = phi_net_vec
    fluxes['T_wC'] = T_wC_vec
    fluxes['observed_H20'] = data['tempObs_avg']
    
    fluxes.to_csv(f'{filesPath}/flux_outputsUnstratified.csv',index=True)    

    df1 = data
    df1['simTemp_C'] = T_wC_vec
    df1['simTemp_K'] = T_wK_vec
    
    df1.to_csv(f'{filesPath}/GaoMerrick_output.csv',index=True)

    plt.plot(T_wC, label = 'Simulated Water temp')
    plt.plot(data['tempObs_avg'], label = 'Observed Air temp')
    plt.plot(watertemp['day_avg'], label = 'Observed Water temp')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare model data to observed/measured temps")
    plt.legend()
    plt.show()
    
def climatology_simulation_loop(data,filesPath):
    #global obsData
    global T_wk
    count = 0
    for day_argue in list(range(1, 366)):
        
        count = count + 1

        print(f"Iteration {count} start - T_wk: {T_wk}")

        phi_sn = calculate_phi_sn(day_argue,data)
        print(f'phi_sn: {phi_sn}')
        phi_at = calculate_phi_at(day_argue,data)
        print(f'phi_at: {phi_at}')
        phi_ws = calculate_phi_ws(T_wk, day_argue,data)
        print(f'phi_ws: {phi_ws}')  
        phi_e = calculate_phi_e(T_wk, day_argue,data)
        print(f'phi_e: {phi_e}')
        phi_c = calculate_phi_c(T_wk, day_argue,data)
        print(f'phi_c: {phi_c}')        
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c 

        phi_at_vec.append(phi_at)
        phi_ws_vec.append(phi_ws)
        phi_e_vec.append(phi_e)
        phi_c_vec.append(phi_c)
        phi_net_vec.append(phi_net)
        phi_sn_vec.append(phi_sn)

        print(f'iteration: {count}, phi_net: {phi_net}')
        
        T_wC = T_wk - 273.15 #change to degree celcius   


        H_t_1 = T_wC * volume * water_heat_capacity * water_density
        #check if K or C
        print(f'iteration: {count}, H_t_1: {H_t_1}')

        H_t = H_t_1 + (phi_net * area * t)
        T_w = H_t/ (volume * water_heat_capacity * water_density)
        print(f'iteration: {count}, T_w: {T_w}')

        #add T_w to a list somehow
        T_wC_vec.append(T_w)

        T_wk = T_w + 273.15 #convert back to kelvin
        T_wK_vec.append(T_wk)      
    fluxes = pd.DataFrame(phi_net_vec,columns=['phi_net'])
    fluxes['phi_at'] = phi_at_vec
    fluxes['phi_ws'] = phi_ws_vec
    fluxes['phi_e'] = phi_e_vec
    fluxes['phi_c'] = phi_c_vec
    fluxes['phi_sn'] = phi_sn_vec
    fluxes['phi_net'] = phi_net_vec
    fluxes['T_wC'] = T_wC_vec
    
    fluxes.to_csv(f'{filesPath}/flux_outputsClimatology.csv',index=True)    

    df1 = data
    df1['simTemp_C'] = T_wC_vec
    df1['simTemp_K'] = T_wK_vec
    
    df1.to_csv(f'{filesPath}/GaoMerrick_outputClimatology.csv',index=True)

    plt.plot(T_wC_vec, label = 'Simulated Water temp')
    plt.plot(data['T2M_C'], label = 'Observed Air temp (climatology)')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare climatology model data to measured temps")
    plt.legend()
    plt.show()