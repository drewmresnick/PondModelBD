#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script will run diagnostics plots for outputs of the bechet_model.py python script. 

When you run this script, it will ask you a series of questions to determine which 
plots to generate.

Check the outputs from the model to determine which year(s) and month(s) will be valid
as inputs for diagnostics. This depends on number of days you ran the model for.

Please note that there were issues with displaying plots without saving them when running
on python directly in terminal. If your plots do not display, please try using a GUI such
as spyder or jupyter notebook.

Use this script to generate plots for:
    1) hourly fluxes for any month and year
    2) air temp (measured) vs water temp (Modeled) for any month and year
    3) hourly modeleld water temp for any month and year
    4) hourly changes in heat flux (annual avg) for any year
    
Plots will be saved to current working directory if you return "y" as input for
this option when running the script.
"""
import pandas as pd
import matplotlib.pyplot as plt 

print("This code can run plots for hourly temperature and individual energy flux.")
outputs = input("Include fluxes? (y/n): ")

if outputs == "y":
    fluxes = ["T_wC", "Qrap", "Qras", "Qraa", "Qevap", "Qconv"]
elif outputs == "n":
    fluxes = ["T_wC"]

dataPath = input("input path to data folder: ")
Modeled = pd.read_csv(f"{dataPath}simulated_hourly.csv")
observed = pd.read_csv(f"{dataPath}observed_khulna.csv")
inputData= pd.read_csv(f"{dataPath}bechet_etal_input.csv")
Modeled['T_aC'] = inputData['T2M']
observed["date"] = pd.to_datetime(observed["date"])

#function that generates plots for model outputs
def plotMonthlyModeled(month):
    modelSel = Modeled[(Modeled["YEAR"]==year) & (Modeled["MO"]==month)]
    for i in fluxes:
        flux = modelSel[i]
        plt.plot(flux.index, flux)
        plt.title(label=f"hourly {i} for month: {month} year: {year}")
        plt.xlabel("hours since start")
        if i == "T_wC":
            plt.ylabel("temperature (C)")
        else:
            plt.ylabel("flux (W)")
        if saveFigs =="y":
            plt.savefig(f"{i}_plot{month}{year}.png")
            plt.show()
        elif saveFigs == "n":
            plt.show()

#function that generates plots observed temp data against modeled temp
def plotMonthlyObserved(month):
    measuredSel = observed[(pd.DatetimeIndex(observed["date"]).year ==year) & \
                           (pd.DatetimeIndex(observed["date"]).month ==month)]
    modelSel = Modeled[(Modeled["YEAR"]==year) & (Modeled["MO"]==month)]
    plt.plot(measuredSel["days_numbered"], measuredSel["avg_air_temp"])
    plt.title(label=f"daily average air temp for month: {month} year: {year}")
    plt.xlabel("days since start")
    plt.ylabel("temperature (C)")
    if saveFigs == "y":
        plt.savefig(f"airTemp_plot{month}{year}.png")
        plt.show()
    elif saveFigs == "n":
        plt.show()
    
    plt.plot(modelSel.index, modelSel["T_aC"], label="Air temp (C)")
    plt.plot(modelSel.index, modelSel["T_wC"], label="Water temp (C)")
    plt.legend()
    plt.title("Compare hourly water and air temp")
    plt.xlabel("hours since start")
    plt.ylabel("temperature (C)")
    if saveFigs == "y":
        plt.savefig(f"airVSwater_plot{month}{year}.png")
        plt.show()
    elif saveFigs == "n":
        plt.show()

#function that generates annual avergae change in heat flux        
def plotYearlyAvg(year):
    modelSel = Modeled[Modeled["YEAR"]==year]
    grouped = modelSel.groupby(['HR'])
    fluxes = ["Qrap", "Qras", "Qraa", "Qevap", "Qconv"]
    for flux in fluxes:
        meanFlux = grouped[flux].mean() / (4047 * 3600)
        resetIndex = meanFlux.reset_index()
        plt.plot(resetIndex.index, resetIndex[flux], label=f"{flux}")
        plt.legend()
        plt.title("hourly changes in heat flux (annual avg)")
        plt.xlabel("time (hrs)")
        plt.ylabel("heat flux (W/m2)")

saveFigs = input("save figures (y/n): ")

year = float(input("input year (2017/2018/2019): "))

allMonth = input("all months? (y/n/custom): ")

if allMonth == "y":
    month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    print("***generating plots for all months***")
    plotYearlyAvg(year)
    for m in month:
        month = float(m)
        plotMonthlyModeled(month)
        plotMonthlyObserved(month)
elif allMonth == "n":
    month = float(input("input month as integer: "))
    print(f"***generating plots for month: {month}***")
    plotMonthlyModeled(month)
    plotMonthlyObserved(month)
    plotYearlyAvg(year)
elif allMonth == "custom":
    monthCustom = input("input months you want as integers (eg: 1 2 3): ")
    month = monthCustom.split()
    print(f"***generating plots for months: {monthCustom}***")
    plotYearlyAvg(year)
    for m in month:
        month = float(m)
        plotMonthlyModeled(month)  
        plotMonthlyObserved(month)







