#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use this to generate monthly plots for:
    1) all fluxes
    2) air temp (measured)
    3) modeleld water temp
    
Plots will be saved to current working directory
"""
import pandas as pd
import matplotlib.pyplot as plt 

print("This code can run plots for hourly temperature and individual energy flux.")
outputs = input("Include fluxes? (y/n): ")

if outputs == "y":
    fluxes = ["T_wC", "Qrap", "Qras", "Qraa", "Qevap", "Qconv"]
elif outputs == "n":
    fluxes = ["T_wC"]

dataPath1 = input("input full path to modelled data: ")
modelled = pd.read_csv(dataPath1)
dataPath2 = input("input full path to observed data: ")
observed = pd.read_csv(dataPath2)
observed["date"] = pd.to_datetime(observed["date"])

def plotMonthlyModelled(month):
    yearSel = modelled[modelled["YEAR"]==year]
    monthSel = yearSel[yearSel["MO"]==month]
    for i in fluxes:
        flux = monthSel[i]
        plt.plot(flux.index, flux)
        plt.title(label=f"hourly {i} for month: {month} year: {year}")
        #plt.savefig(f"{i}_plot.png")
        plt.show()
        
def plotMonthlyObserved(month):
    yearSel = observed[pd.DatetimeIndex(observed["date"]).year ==year]
    monthSel = yearSel[pd.DatetimeIndex(yearSel["date"]).month ==month]
    plt.plot(monthSel["days_numbered"], monthSel["avg_air_temp"])
    plt.title(label=f"daily average air temp for month: {month} year: {year}")
    #plt.savefig("airTemp_plot.png")
    plt.show()

year = float(input("input year (2017/2018/2019): "))

allMonth = input("all months? (y/n/custom): ")
if allMonth == "y":
    month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    print("***generating plots for all months***")
    for m in month:
        month = float(m)
        plotMonthlyModelled(month)
        plotMonthlyObserved(month)
elif allMonth == "n":
    month = float(input("input month as integer: "))
    print(f"***generating plots for month: {month}***")
    plotMonthlyModelled(month)
    plotMonthlyObserved(month)
elif allMonth == "custom":
    monthCustom = input("input months you want as integers (eg: 1 2 3): ")
    month = monthCustom.split()
    print(f"***generating plots for months: {monthCustom}***")
    for m in month:
        month = float(m)
        plotMonthlyModelled(month)  
        plotMonthlyObserved(month)
