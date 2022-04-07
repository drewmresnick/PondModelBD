# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#             Single layer mixed pond
#             morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity

import pandas as pd
import GaoMerrick_model
import os
#import pyaconf

#CONFIG = pyaconf.load(os.environ["CONFIG"])
#reading in input csv file as array (question for drew: let me know if you want to work with dataframe instead)
# I separated the two districts into two files for ease for now, not sure if we want to keep them together
filesPath = input("Input file path to where data files are located: ")
dataType = input("Is the data daily data or climatology? (D/C): ")
#open csv file using pandas to create pandas dataframe 

if dataType == 'D':
    data = pd.read_csv(f"{filesPath}input_data_for_simulation_2018_2019_khulna.csv")
    watertemp = pd.read_csv(f'{filesPath}Realtime_watertemp.csv') #observed data
elif dataType == 'C':
    data = pd.read_csv(f"{filesPath}climatology_4daySpells.csv")
    
print(data)

#if __name__ == '__main__':
#    GaoMerrick_model.main_simulation_loop(data,watertemp)

if dataType == 'D':
    GaoMerrick_model.main_simulation_loop(data,watertemp,filesPath)
elif dataType == 'C':
    GaoMerrick_model.climatology_simulation_loop(data, filesPath)

