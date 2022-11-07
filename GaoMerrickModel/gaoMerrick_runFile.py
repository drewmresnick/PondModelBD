# IRI aquaculture Bangladesh

"""
Simple Energy flux model for mixed pond  #######

This model runs at a daily time step.

 Assumptions:
     1. Single layer mixed pond
"""

import gaoMerrickFuncs
import pandas as pd
import gmVars

print("---MODEL RUN INFO---")
if gmVars.dataType == 'C':
    print(f"Climatology data run for {gmVars.numberDays} days")
elif gmVars.dataType == 'D':
    print(f"Daily data run for {gmVars.numberDays} days")
print("Running...")

if gmVars.dataType == 'D':
    data = pd.read_csv(f'{gmVars.filesPath}{gmVars.inputFileName}')
    watertemp = pd.read_csv(f'{gmVars.filesPath}{gmVars.obsFileName}') #observed data
    gaoMerrickFuncs.main_simulation_loop(data, watertemp, gmVars.T_wk0, gmVars.numberDays, gmVars.saveFile)
elif gmVars.dataType == 'C':
    data = pd.read_csv(f'{gmVars.filesPath}{gmVars.inputFileName}')
    gaoMerrickFuncs.climatology_simulation_loop(data, gmVars.T_wk0, gmVars.numberDays, gmVars.saveFile)

print("Run completed")
