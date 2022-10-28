import bechetFuncs
import pandas as pd
import bechetVars
"""
Created on Thu Aug 12 12:19:35 2021
@author: sanketa, Drew

Model elements:
Qra,p: radiation from pond surface (W)
    Qra,s: total (direct and diffuse) solar radiation (W)
    Qra,a: radiation from air to pond (W)
    Qev: evaporative heat flux (W)
    Qconv: convective flux at pond surface (W)
    Qcond: conductive flux with ground at pond bottom (W) #not using
    Qi: heat flux associated with water inflow (W)
    Qr: heat flux induced by rain (W) #not using
This model runs at an hourly time step.Assumptions:
    1. Fully mixed model.
    2. Average cloud cover.
    3. heat transfer due to rainfall and soil is negligible and thus neglected.
    4. algal absorbtion rate negligible and set to zero.
"""
print("---MODEL RUN INFO---")
if bechetVars.dataType == 'C':
    print(f"    Climatology data run for {bechetVars.numberDays} days")
    print("Model running...")
elif bechetVars.dataType == 'H':
    print(f"    Hourly data run for {bechetVars.numberDays} days")
    print("Model running...")

if bechetVars.dataType == 'H':
    data = pd.read_csv(f'{bechetVars.filesPath}{bechetVars.inputFileName}') #df of input data
    if bechetVars.obsFileName != 'NA':
        observed = pd.read_csv(f'{bechetVars.filesPath}{bechetVars.obsFileName}') #observed data
        observed['date'] = pd.to_datetime(observed['date'])
    elif bechetVars.obsFileName == 'NA':
        observed = 'NA'
    bechetFuncs.main_simulation_loop(data, observed, bechetVars.T_wk,bechetVars.filesPath, bechetVars.numberDays, bechetVars.saveFile, bechetVars.outputPath) #run main sim loop
    print("Model run completed")
else: #if dataType == 'C':
    data = pd.read_csv(f'{bechetVars.filesPath}{bechetVars.inputFileName}')
    bechetFuncs.climatology_simulation_loop(data, bechetVars.T_wk,bechetVars.filesPath, bechetVars.numberDays, bechetVars.saveFile, bechetVars.outputPath)
    print("Model run completed.")
