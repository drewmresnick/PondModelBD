import numpy as np
import pandas as pd
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

def read_dataline(day_argue,data,start_date):
    day, day_mon_year = find_day_month_year(day_argue,start_date)
    year = day_mon_year.year
    selected_data = data[(data[gmVars.dayVar]== day) & (data[gmVars.yearVar] == year)]
    return selected_data
 

#Solar radiation, pp.174 eqn.2 (Gao & Merrick 1996)
#phi_sn = phi_s * (1-R)
def calculate_phi_sn(day_argue,data,start_date):
    daily_data = read_dataline(day_argue,data,start_date)
    wind_speed = float(daily_data[gmVars.windVar])

    R_s = 0.035 #considering constant value for daily code #Losordo&Piedrahita

    W_z = wind_speed #wind velocity in m/s

    R= R_s *(1-0.08 * W_z)

    phi_s = float(daily_data[gmVars.sradVar]) * (1000/24) #Kj/m2/hr; in excel file says SRAD_MJ/m2day

    phi_sn = phi_s * (1-R)

    return phi_sn

#Atmospheric radiation, pp.174 eqn.3 (Gao & Merrick 1996)
#phi_at = (1-r)*e*sigma*((T_ak)**4)
def calculate_phi_at(day_argue,data,start_date):
    daily_data = read_dataline(day_argue,data,start_date)

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
def calculate_phi_e(T_wk,day_argue,data,start_date):
    daily_data = read_dataline(day_argue,data,start_date)
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
def calculate_phi_c(T_wk, day_argue,data,start_date):
    daily_data = read_dataline(day_argue,data,start_date)
    wind_speed = daily_data[gmVars.windVar]
    T_ak = float(daily_data[gmVars.airTempVar])

    W = float(wind_speed) #m/s per C&B paper

    T_wc = T_wk - 273.15 #convert to deg celcius
    T_ac = T_ak - 273.15

    phi_c = float(1.5701 * W * (T_wc-T_ac))

    return(phi_c)

#rain heat flux, adapted from eqn. 21 (pp 3706, Béchet et al 2011)
#phi_r = p*C*q_r(T_a - T_p)S
def calculate_phi_r(T_wk,day_argue,data,start_date):
    daily_data = read_dataline(day_argue,data,start_date)
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

        phi_sn = calculate_phi_sn(day_argue,data,gmVars.start_date)
        phi_at = calculate_phi_at(day_argue,data,gmVars.start_date)
        phi_ws = calculate_phi_ws(T_wk, day_argue,data)
        phi_e = calculate_phi_e(T_wk, day_argue,data,gmVars.start_date)
        phi_c = calculate_phi_c(T_wk, day_argue,data,gmVars.start_date)
        phi_r = calculate_phi_r(T_wk, day_argue,data,gmVars.start_date)
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

        phi_sn = calculate_phi_sn(day_argue,data,gmVars.start_date)
        phi_at = calculate_phi_at(day_argue,data,gmVars.start_date)
        phi_ws = calculate_phi_ws(T_wk, day_argue,data,gmVars)
        phi_e = calculate_phi_e(T_wk, day_argue,data,gmVars.start_date)
        phi_c = calculate_phi_c(T_wk, day_argue,data,gmVars.start_date)
        phi_c = calculate_phi_r(T_wk, day_argue,data,gmVars.start_date)
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


def simplified_simulation_loop(data,T_wk0,numberDays,start_date,season,year):
    #global obsData
    global T_wk
    T_wk = T_wk0
    DOY = 0

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
    doy_vec = []

    for day_argue in list(range(1, numberDays)):

        DOY = DOY + 1

        phi_sn = calculate_phi_sn(day_argue,data,start_date)
        phi_at = calculate_phi_at(day_argue,data,start_date)
        phi_ws = calculate_phi_ws(T_wk, day_argue,data)
        phi_e = calculate_phi_e(T_wk, day_argue,data,start_date)
        phi_c = calculate_phi_c(T_wk, day_argue,data,start_date)
        phi_r = calculate_phi_r(T_wk, day_argue,data,start_date)
        phi_net = phi_sn + phi_at - phi_ws - phi_e - phi_c - phi_r


        phi_at_vec.append(phi_at)
        phi_ws_vec.append(phi_ws)
        phi_e_vec.append(phi_e)
        phi_c_vec.append(phi_c)
        phi_net_vec.append(phi_net)
        phi_sn_vec.append(phi_sn)
        phi_r_vec.append(phi_r)
        doy_vec.append(DOY)

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
    df1 = pd.DataFrame()
    df1['DOY'] = doy_vec
    df1['phi_at'] = phi_at_vec
    df1['phi_ws'] = phi_ws_vec
    df1['phi_e'] = phi_e_vec
    df1['phi_c'] = phi_c_vec
    df1['phi_sn'] = phi_sn_vec
    df1['phi_r'] = phi_r_vec
    df1['phi_net'] = phi_net_vec
    df1['simTemp_C'] = T_wC_vec
    df1['simTemp_K'] = T_wK_vec

    #select only the months in the season from the full 6 months the model runs
    selected_season = df1[(df1[gmVars.dayVar] >= 90) & (df1[gmVars.dayVar] <= 180)]
    run_means = selected_season.mean()

    data = {
        'year':[year,],
        'season':[season,],
        'phi_at':[run_means['phi_at'],],
        'phi_ws':[run_means['phi_ws'],],
        'phi_e':[run_means['phi_e'],],
        'phi_c':[run_means['phi_c'],],
        'phi_sn':[run_means['phi_sn'],],
        'phi_r':[run_means['phi_r'],],
        'phi_net':[run_means['phi_net'],],
        'simTemp_C':[run_means['simTemp_C'],],
        'simTemp_K':[run_means['simTemp_K']],
    }

    means_dataframe = pd.DataFrame(data)

    return df1, means_dataframe

    return dataFrame_full


def seasonal_simulation_terciles(fullData,seasonalMeans,T_wk0,numberDays,saveFile):
    seasons = ["JFM","AMJ","JAS","OND"]
    dataFrame_full = pd.DataFrame()
    means_outputs = pd.DataFrame()
    means_full = pd.DataFrame()
    print("    Running model on all years of data...")
    for year in range(1990,(2020+1)):

        for season in [gmVars.season]: #currently just running for a single season at a time
            if season == "JFM": #we start the model run three months before target season so JFM needs data from previous year
                sampled_data = fullData[(fullData[gmVars.yearVar]>=(year-1)) & (fullData[gmVars.yearVar]<=year)]
                year_string = f"01/10/{(year-1)}" #day month year date that the model will start running on 
            else:
                sampled_data = fullData[fullData[gmVars.yearVar]==year]
                if season == "AMJ":
                    year_string = f"01/01/{year}" #day month year
                if season == "JAS":
                    year_string = f"01/04/{year}" #day month year
                if season == "OND":
                    year_string = f"01/07/{year}" #day month year

                    #now we run the model with the selected data
            daysCount = 181 #6 months of data will be run through the model for each model run

            modelRuns, runMeans = simplified_simulation_loop(sampled_data,gmVars.T_wk0,daysCount,year_string,season,year)
            dataFrame_full = dataFrame_full.append(modelRuns)
            means_outputs = means_outputs.append(runMeans) 
    print("    Getting and sorting yearly averages from model run...")
    yearly_averages_sorted_og = means_outputs.groupby('year').mean().sort_values(by=['simTemp_C'],ascending=False)
    yearly_averages_sorted = yearly_averages_sorted_og
    yearly_averages_sorted['rank'] = range(1,32)
    print("yearly avg sorted")
    print(yearly_averages_sorted)

    above_cutoff_temp = yearly_averages_sorted['simTemp_C'][yearly_averages_sorted['rank']==10].values[0]
    below_cutoff_temp = yearly_averages_sorted['simTemp_C'][yearly_averages_sorted['rank']==20].values[0]
    
    if saveFile == "y":
        yearly_averages_sorted.to_csv(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}_{gmVars.season}_means_sorted.csv',index=True)
    
    print("    Sampling from the model outputs...")
    #now we have the means for each season for each year so we can sample from that df
    sampled_df = pd.DataFrame()
    runs = []
    terciles = []
    for season in [gmVars.season]: #getting the number of samples for each tercile
        print(f"    Sampling for season {season}")
        below = gmVars.tercile_below
        average = gmVars.tercile_avg
        above = gmVars.tercile_above
        terciles_dict = {"below":below, "average":average, "above":above}

        szn_means = seasonalMeans[seasonalMeans["season"]==season] #selecting seasonal means

        for tercile in list(terciles_dict.keys()):
            print(f"    tercile: {tercile}")
            for run in range(1,(terciles_dict[tercile]+1)): #sampling for the number of times associated with each tercile

                if tercile == "above":
                    szn_means_sel = szn_means[(szn_means["rank"]>=1) & (szn_means["rank"]<=10)]
                if tercile == "average":
                    szn_means_sel = szn_means[(szn_means["rank"]>10) & (szn_means["rank"]<=20)]
                if tercile == "below":
                    szn_means_sel = szn_means[(szn_means["rank"]>20) & (szn_means["rank"]<=31)]  

                sampled_year = (szn_means_sel[gmVars.yearVar].sample()).values[0] #now we have the year that we will use to run with the model  
                sampled_year_data = means_outputs[(means_outputs['year']==sampled_year) & (means_outputs['season']==season)]
                copy_of_sampled = sampled_year_data

                print(f"    ***doing the copy stuff***")
                copy_of_sampled['run'] = run 
                copy_of_sampled['tercile_air'] = tercile
                print(f"cutoffs: upper={above_cutoff_temp} lower={below_cutoff_temp}")
                if copy_of_sampled['simTemp_C'].values[0] >= above_cutoff_temp:
                    copy_of_sampled['tercile_water'] = str("above")
                elif copy_of_sampled['simTemp_C'].values[0] <= below_cutoff_temp:
                    copy_of_sampled['tercile_water'] = str("below")
                else:
                    copy_of_sampled['tercile_water'] = str("average")

                #sampled_df = sampled_df.append(copy_of_sampled)
                sampled_df = pd.concat([sampled_df,copy_of_sampled])
    print(f"cutoff temps: upper {above_cutoff_temp} below {below_cutoff_temp}")
    if saveFile == "y":
        sampled_df.to_csv(f'{gmVars.outputFilesPath}{gmVars.outputFilesName}_{gmVars.season}_means_resampled.csv',index=True)
    
    for tercile in list(terciles_dict.keys()):
        occurance = sampled_df['tercile_water'].str.count(tercile).sum()
        print(f"tercile {tercile}: {occurance}%") 