# IRI aquaculture Bangladesh 

##### Simple Energy flux model for mixed pond  #######
# Assumptions:- 
#     Single layer mixed pond
#     morning minimum temperature (Tmin_air) as morning minimum dry-bulb temperature (line 816; cmd+F T_d) in place of Relative humidity
import GaoMerrick_model
from configparser import ConfigParser
import pandas as pd

config = ConfigParser()
config.read('GaoMerrick_config.ini')

filesPath = config.get('data', 'filesPath')
dataType = config.get('data', 'dataType')

if dataType == 'D':
    inputFileName = config.get('data', 'inputFile')
    data = pd.read_csv(f'{filesPath}{inputFileName}')
    obsFileName = config.get('data','observationData')
    watertemp = pd.read_csv(f'{filesPath}{obsFileName}') #observed data
    GaoMerrick_model.main_simulation_loop(data,watertemp,filesPath)
elif dataType == 'C':
    intputFileName = config.get('data', 'inputFile')
    data = pd.read_csv(f'{filesPath}{inputFileName}')
    print(data)
    GaoMerrick_model.climatology_simulation_loop(data, filesPath)
    

