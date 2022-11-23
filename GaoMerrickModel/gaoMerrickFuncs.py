import numpy as np
import datetime as dt
import math
import matplotlib.pyplot as plt
import gmVars

#create a function to get month and year based on integer sequence input
def find_day_month_year(input_day, start_date): #dt.date(2016,12,31)):
    start_date = dt.datetime.strptime(start_date, "%d/%m/%Y")
    computed_day = (start_date + dt.timedelta(days = float(input_day))).date()
    days_from_year_start = computed_day - dt.date(computed_day.year, 1, 1) + dt.timedelta(days = 1)

    return days_from_year_start.days, computed_day

#create a function to read data for particular day, month and year so we can use it to loop through all days later

def read_dataline(day_argue,data):
    day, day_mon_year = find_day_month_year(day_argue,gmVars.start_date)
    year = day_mon_year.year
    selected_data = data[(data[gmVars.dayVar]== day) & (data[gmVars.yearVar] == year)]
    return selected_data

#Solar radiation, pp.174 eqn.2 (Gao & Merrick 1996)
#phi_sn = phi_s * (1-R)
def calculate_phi_sn(day_argue,data):
    daily_data = read_dataline(day_argue,data)
    wind_speed = float(daily_data[gmVars.windVar])

    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed #wind velocity in m/s

    R= R_s *(1-0.08 * W_z)

    phi_s = float(daily_data[gmVars.sradVar]) * (1000/24) #Kj/m2/hr; in excel file says SRAD_MJ/m2day

    phi_sn = phi_s * (1-R)

    return phi_sn

#Solar radiation transmittance and attenuation, pp 201 eqn. 19 (Losordo & Piedrahita 1991)
#phi_sn,z = phi_sn(1-R)(1-B)exp(-n_et*z)
def calculate_phi_snz(z,day_argue,data): ###CURRENTLY NOT IN USE
    daily_data = read_dataline(day_argue,data)
    W_z = float(daily_data[gmVars.windVar])

    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita
    R= R_s *(1-0.08 * W_z)

    phi_s = float(daily_data[gmVars.sradVar]) * (1000/24) #Kj/m2/hr; in excel file says SRAD_MJ/m2day
    phi_sn = phi_s * (1-R)

    B = 0.5 #in L&P estimated to be between 0.4-0.5
    n = 1/(1.3**-5) #placeholder; I think this should be calculated with eqns in paper

    phi_snz = phi_sn * (1-R) * (1-B) * math.exp(-n*z)

    return phi_snz

#Atmospheric radiation, pp.174 eqn.3 (Gao & Merrick 1996)
#phi_at = (1-r)*e*sigma*((T_ak)**4)
def calculate_phi_at(day_argue,data):
    daily_data = read_dataline(day_argue,data)
    T_ak = float(daily_data[gmVars.airTempVar])
    e = (0.398 * (10 ** (-5)))*(T_ak ** (2.148))
    r = 0.03 # reflectance of the water surface to longwave radiation
    phi_at = (1-r)*e*gmVars.sigma*((T_ak)**4)

    return(phi_at)

#Water surface radiation, pp.174 eqn. 4 (Gao & Merrick 1996)
#phi_ws = 0.97*sigma*((T_wk)**4)
def calculate_phi_ws(T_wk, day_argue,data):
    phi_ws = 0.97 * gmVars.sigma * ((T_wk)**4)

    return(phi_ws)

#Evaporative heat loss, pp.174 eqn. 5-7 (Gao & Merrick 1996)
#phi_e = N*v*(e_s- e_a)
def calculate_phi_e(T_wk,day_argue,data):
    daily_data = read_dataline(day_argue,data)
    wind_speed = float(daily_data[gmVars.windVar])
    T_ak = float(daily_data[gmVars.airTempVar])
    RH = float(daily_data[gmVars.rhVar]) / 100
    W_2 = wind_speed * 3.6

    e_s = 25.374 * math.exp(17.62 - 5271/T_wk)
    e_a = RH * 25.374 * math.exp(17.62 - 5271/T_ak)

    phi_e = float(gmVars.N* W_2 * (e_s- e_a))
    return(phi_e)

#Sensible heat transfer, pp.175 eqn. 8-10 (Gao & Merrick 1996)
#phi_c = 1.5701*W*(T_wc-T_ac))
def calculate_phi_c(T_wk, day_argue,data):
    daily_data = read_dataline(day_argue,data)
    wind_speed = daily_data[gmVars.windVar]
    T_ak = float(daily_data[gmVars.airTempVar])

    W = float(wind_speed) #m/s per C&B paper

    T_wc = T_wk - 273.15 #convert to deg celcius
    T_ac = T_ak - 273.15

    phi_c = float(1.5701 * W * (T_wc-T_ac))

    return(phi_c)

#Heat transfer by turbulent diffusion, pp 203-205 eqn. 31 (Losordo&Piedrahita 1991)
#phi_d2 = p*C*E_z2(T_1 - T_2)/(z_1-z_3)
#For now we are just modelling two elements so depths are hard coded
def calculate_phi_d(T_1, T_2, day_argue, data):
    #if T_1 < T_2:
    #    print("top element is colder than bottom, numerical mixing")
    T_wK_v1 = T_1
    T_wK_v2 = T_2
    T_wC_v1 = T_1 - 273
    T_wC_v2 = T_2 - 273

    daily_data = read_dataline(day_argue,data)
    wind_speed = float(daily_data[gmVars.windVar])

    sigma = 0.05 #emperical coeff
    z = .1 #depth at z=2 in m
    T_av = (T_wK_v1 + T_wK_v2)/2 #average temperature of adjacent volume elements in K
    g = 9.8 #gravitational acceleration in m s-2
    C = 1*10**-3

    t = gmVars.air_density * C * wind_speed**2
    W = (t/gmVars.water_density)**.5
    u = 30 * W
    k = 6 * (wind_speed**-1.84)

    E = ((W**2)/u*k) * math.exp(-k*z)

    av = (1.5*10**-5) * (T_av - 277) - (2 * 10**-7) * (T_av - 277)**2
    Ri = av * g * z**2 / (W**2) * ((T_wK_v1 - T_wK_v2)/(.15)) #Temp in kelvin ; .15 = distance btwn the two centers in m; Ri is dimensionless

    E_z2 = (E) * ((1 + sigma * Ri)**-1)

    phi_d = gmVars.water_density * gmVars.water_heat_capacity * E_z2 * (T_wC_v1 - T_wC_v2)/(5-20) #mid depths of volume elements in cm

    return(phi_d)

#rain heat flux, adapted from eqn. 21 (pp 3706, Béchet et al 2011)
#phi_r = p*C*q_r(T_a - T_p)S
def calculate_phi_r(T_wk,day_argue,data):
    daily_data = read_dataline(day_argue,data)
    T_ak = float(daily_data[gmVars.airTempVar])
    precip = float(daily_data[gmVars.precipVar])

    phi_r = float(gmVars.water_density * gmVars.water_heat_capacity * precip * (T_ak-T_wk)) * 3600 #units need to be in kJm-2h-1

    return(phi_r)

# loop for energy flux equation
def main_simulation_loop(data,waterTemp,T_wk0,numberDays,saveFile):
    #global obsData
    global T_wk
    T_wk = T_wk0
    count = 0

    #create empty df for outputs
    T_wC_vec = []
    T_wK_vec = []
    phi_net_vec = []
    phi_at_vec = []
    phi_c_vec = []
    phi_ws_vec = []
    phi_e_vec = []
    phi_sn_vec = []
    phi_r_vec = []

    for day_argue in list(range(1, numberDays)): #731

        count = count + 1

        phi_sn = calculate_phi_sn(day_argue,data)
        phi_at = calculate_phi_at(day_argue,data)
        phi_ws = calculate_phi_ws(T_wk, day_argue,data)
        phi_e = calculate_phi_e(T_wk, day_argue,data)
        phi_c = calculate_phi_c(T_wk, day_argue,data)
        phi_r = calculate_phi_r(T_wk, day_argue,data)
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c - phi_r


        phi_at_vec.append(phi_at)
        phi_ws_vec.append(phi_ws)
        phi_e_vec.append(phi_e)
        phi_c_vec.append(phi_c)
        phi_net_vec.append(phi_net)
        phi_sn_vec.append(phi_sn)
        phi_r_vec.append(phi_r)

        T_wC = T_wk - 273.15 #change to degree celcius

        #We calculate the heat at t-1 and add the change in heat to get
        #heat at time t; then convert that to a temperature value
        H_t_1 = T_wC * gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density
        #check if K or C

        H_t = H_t_1 + (phi_net * gmVars.area * gmVars.t)
        T_w = H_t/ (gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density)

        #add T_w to a list
        T_wC_vec.append(T_w)

        T_wk = T_w + 273.15 #convert back to kelvin
        T_wK_vec.append(T_wk)

    T_wC = np.array(T_wC_vec)
    df1 = data.loc[0:(numberDays-2)].copy()
    df1['phi_at'] = phi_at_vec
    df1['phi_ws'] = phi_ws_vec
    df1['phi_e'] = phi_e_vec
    df1['phi_c'] = phi_c_vec
    df1['phi_sn'] = phi_sn_vec
    df1['phi_r'] = phi_r_vec
    df1['phi_net'] = phi_net_vec
    df1['simTemp_C'] = T_wC_vec
    df1['simTemp_K'] = T_wK_vec
    df1['observedWater_dailyAvg'] = waterTemp[gmVars.waterTempVar]

    print("Model run complete. Now returning plots.")
    print("    **If `saveFile`=='n' the process will run until user closes out of the plot(s).**")

    plt.plot(T_wC, label = 'Simulated Water temp')
    plt.plot(data[gmVars.airTempVarC], label = 'Air temp')
    plt.plot(waterTemp[gmVars.waterTempVar], label = 'Observed Water temp')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare model data to observed/measured temps")
    plt.legend()

    if saveFile == "y":
        plt.savefig(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}.png')
        df1.to_csv(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}.csv',index=True)
    elif saveFile=="n":
        plt.show()


def main_simulation_loop_stratified(data,waterTemp,T_wk0_v1,T_wk0_v2,numberDays,saveFile):
    #global obsData
    global T_wk_v1
    global T_wk_v2
    T_wk_v1 = T_wk0_v1
    T_wk_v2 = T_wk0_v2
    count = 0

    #create empty df for outputs
    T_wC_v1_vec = []
    T_wK_v1_vec = []
    T_wC_v2_vec = []
    T_wK_v2_vec = []
    phi_net_vec = []
    phi_at_vec = []
    phi_c_vec = []
    phi_ws_vec = []
    phi_e_vec = []
    phi_sn_vec = []
    phi_r_vec = []
    phi_d_vec = []

    for day_argue in list(range(1, numberDays)): #731

        count = count + 1
        print(f"*****iteration: {count}******")

        phi_sn = calculate_phi_sn(day_argue,data)
        print(f"phi_sn: {phi_sn}")
        phi_at = calculate_phi_at(day_argue,data)
        print(f"phi_at: {phi_at}")
        phi_ws = calculate_phi_ws(T_wk_v1, day_argue,data)
        print(f"phi_ws: {phi_ws}")
        phi_e = calculate_phi_e(T_wk_v1, day_argue,data)
        print(f"phi_e: {phi_e}")
        phi_c = calculate_phi_c(T_wk_v1, day_argue,data)
        print(f"phi_c: {phi_c}")
        phi_r = calculate_phi_r(T_wk_v1, day_argue,data)
        print(f"phi_r: {phi_r}")
        phi_d = calculate_phi_d(T_wk_v1,T_wk_v2,day_argue,data)
        print(f"phi_d: {phi_d}")
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c - phi_r
        print(f"phi_net: {phi_net}")


        phi_at_vec.append(phi_at)
        phi_ws_vec.append(phi_ws)
        phi_e_vec.append(phi_e)
        phi_c_vec.append(phi_c)
        phi_net_vec.append(phi_net)
        phi_sn_vec.append(phi_sn)
        phi_r_vec.append(phi_r)

        T_wC_v1 = T_wk_v1 - 273.15 #change to degree celcius
        T_wC_v2 = T_wk_v2 - 273.15 #change to degree celcius

        #We calculate the heat at t-1 and add the change in heat to get
        #heat at time t; then convert that to a temperature value
        H_t_1_v1 = T_wC_v1 * gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density
        H_t_1_v2 = T_wC_v2 * gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density
        #check if K or C

        H_t_v1 = H_t_1_v1 + ((phi_net-phi_d) * gmVars.area * gmVars.t)
        T_w_v1 = H_t_v1/ (gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density)
        print(f"temp at volume 1: {T_w_v1}")
        H_t_v2 = H_t_1_v2 + ((phi_sn + phi_d) * gmVars.area * gmVars.t)
        T_w_v2 = H_t_v2/ (gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density)
        print(f"temp at volume 2: {T_w_v2}")
        #add T_w to a list
        T_wC_v1_vec.append(T_w_v1)
        T_wC_v2_vec.append(T_w_v2)

        T_wk_v1 = T_w_v1 + 273.15 #convert back to kelvin
        T_wK_v1_vec.append(T_wk_v1)
        T_wk_v2 = T_w_v2 + 273.15 #convert back to kelvin
        T_wK_v2_vec.append(T_wk_v2)

    T_wC_v1 = np.array(T_wC_v1_vec)
    T_wC_v2 = np.array(T_wC_v2_vec)
    df1 = data.loc[0:(numberDays-2)].copy()
    df1['phi_at'] = phi_at_vec
    df1['phi_ws'] = phi_ws_vec
    df1['phi_e'] = phi_e_vec
    df1['phi_c'] = phi_c_vec
    df1['phi_sn'] = phi_sn_vec
    df1['phi_r'] = phi_r_vec
    df1['phi_net'] = phi_net_vec
    df1['simTemp_v1_C'] = T_wC_v1_vec
    df1['simTemp_v2_C'] = T_wC_v2_vec
    df1['simTemp_v1_K'] = T_wK_v1_vec
    df1['observedWater_dailyAvg'] = waterTemp[gmVars.waterTempVar]

    print("Model run complete. Now returning plots.")
    print("    **If `saveFile`=='n' the process will run until user closes out of the plot(s).**")

    plt.plot(T_wC_v1, label = 'Simulated Water temp, volume element 1')
    plt.plot(T_wC_v2, label = 'Simulated Water temp, volume element 2')
    plt.plot(data[gmVars.airTempVarC], label = 'Air temp')
    plt.plot(waterTemp[gmVars.waterTempVar], label = 'Observed Water temp')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare model data to observed/measured temps")
    plt.legend()

    if saveFile == "y":
        plt.savefig(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}.png')
        df1.to_csv(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}.csv',index=True)
    elif saveFile=="n":
        plt.show()

def climatology_simulation_loop(data,T_wk0,numberDays,saveFile):
    #global obsData
    global T_wk
    T_wk = T_wk0
    count = 0

    #create empty df for outputs
    T_wC_vec = []
    T_wK_vec = []
    phi_net_vec = []
    phi_at_vec = []
    phi_c_vec = []
    phi_ws_vec = []
    phi_e_vec = []
    phi_sn_vec = []
    phi_r_vec = []

    for day_argue in list(range(1, numberDays)):

        count = count + 1

        phi_sn = calculate_phi_sn(day_argue,data)
        phi_at = calculate_phi_at(day_argue,data)
        phi_ws = calculate_phi_ws(T_wk, day_argue,data)
        phi_e = calculate_phi_e(T_wk, day_argue,data)
        phi_c = calculate_phi_c(T_wk, day_argue,data)
        phi_c = calculate_phi_r(T_wk, day_argue,data)
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c + phi_r

        phi_at_vec.append(phi_at)
        phi_ws_vec.append(phi_ws)
        phi_e_vec.append(phi_e)
        phi_c_vec.append(phi_c)
        phi_net_vec.append(phi_net)
        phi_sn_vec.append(phi_sn)
        phi_r_vec.append(phi_r)

        T_wC = T_wk - 273.15 #change to degree celcius

        H_t_1 = T_wC * gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density

        H_t = H_t_1 + (phi_net * gmVars.area * gmVars.t)
        T_w = H_t/ (gmVars.volume * gmVars.water_heat_capacity * gmVars.water_density)

        #add T_w to a list
        T_wC_vec.append(T_w)

        T_wk = T_w + 273.15 #convert back to kelvin
        T_wK_vec.append(T_wk)

    df1 = data.loc[0:(numberDays-2)].copy()
    df1['simTemp_C'] = T_wC_vec
    df1['simTemp_K'] = T_wK_vec
    df1['phi_at'] = phi_at_vec
    df1['phi_ws'] = phi_ws_vec
    df1['phi_e'] = phi_e_vec
    df1['phi_c'] = phi_c_vec
    df1['phi_sn'] = phi_sn_vec
    df1['phi_r'] = phi_r_vec
    df1['phi_net'] = phi_net_vec

    print("Model run complete. Now returning plots.")
    print("    **If `saveFile`=='n' the process will run until user closes out of the plot(s).**")

    plt.plot(T_wC_vec, label = 'Simulated Water temp')
    plt.plot(data['T2M_C'], label = f'Air temp (climatology;{gmVars.spellDay} day spells)')
    plt.gca().legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.xlabel("Time (days)")
    plt.ylabel("Temperature (C)")
    plt.title("Compare climatology model data to measured temps")
    plt.legend()

    if saveFile =="y":
        df1.to_csv(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}.csv',index=True)
        plt.savefig(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}.png')
    elif saveFile == "n":
        plt.show()
