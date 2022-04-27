# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#     Single layer mixed pond
#     morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity
import GaoMerrick_model
import pandas as pd
import gmVars

if gmVars.dataType == 'D':
    data = pd.read_csv(f'{gmVars.filesPath}{gmVars.inputFileName}')
    watertemp = pd.read_csv(f'{gmVars.filesPath}{gmVars.obsFileName}') #observed data
    GaoMerrick_model.main_simulation_loop(data, watertemp, gmVars.T_wk0, gmVars.numberDays, gmVars.filesPath,gmVars.saveFile)
elif gmVars.dataType == 'C':
    data = pd.read_csv(f'{gmVars.filesPath}{gmVars.inputFileName}')
    GaoMerrick_model.climatology_simulation_loop(data, gmVars.T_wk0, gmVars.numberDays, gmVars.filesPath,gmVars.saveFile)
    
print("---MODEL RUN INFO---")
if gmVars.dataType == 'C':
    print(f"Climatology data run for {gmVars.numberDays} days")
elif gmVars.dataType == 'H':
    print(f"Hourly data run for {gmVars.numberDays} days")
