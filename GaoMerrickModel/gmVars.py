from configparser import ConfigParser
config = ConfigParser()config.read('GaoMerrick_config.ini')

#files information
filesPath = config.get('data', 'filesPath')
inputFileName = config.get('data', 'inputFile')
obsFileName = config.get('data','observationData')
outputFilesPath = config.get('data', 'outputFilesPath')
outputFilesName = config.get('data','outputFilesName')

#data information
dataType = config.get('data', 'dataType')

#data variable names
dayVar = config.get('inputVarNames','dayVar')
yearVar = config.get('inputVarNames','yearVar')
precipVar = config.get('inputVarNames','precipVar')
windVar = config.get('inputVarNames','windVar')
sradVar = config.get('inputVarNames','sradVar')
rhVar = config.get('inputVarNames','rhVar')
airTempVar = config.get('inputVarNames','airTempVar')
airTempVarC = config.get('inputVarNames','airTempVarC')
waterTempVar = config.get('obsVarNames','waterTempVar')
spellDay = config.get('data','spellDay')
start_date = config.get('data','start_date')

#pond constants
pond_depth =config.getfloat('modelConstants', 'pondDepth') #meters
volume = config.getfloat('modelConstants', 'pondVolume') #m3
area = config.getfloat('modelConstants', 'pondArea') #m2
t = config.getfloat('modelConstants', 'timeStep') #hrs

#model run info
T_wk0_v1 = config.getfloat('modelConstants', 'initialTemp_v1') #first day water temp at khulna
T_wk0_v2 = config.getfloat('modelConstants', 'initialTemp_v2') #first day water temp at khulna volume element 2
numberDays = config.getint('data','numberDays') #number days model will run for
saveFile = config.get('data','saveFile')#model constants
pi = 3.1415
sigma = 2.07e-7 ##stefan boltzman constant
N = 5.0593 ##empirical coefficient unit m^-2km^-1 mmHg^-1
water_heat_capacity = 4.184 #kJ/kgK
water_density = 997 #kg/m3
air_density = 1.225 #kg/m3
