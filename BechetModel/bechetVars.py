from configparser import ConfigParser

config = ConfigParser()
config.read('Bechet_config.ini')

#directory info
filesPath = config.get('data', 'filesPath')
outputPath = config.get('data','outputFilesPath')

#data info
inputFileName = config.get('data', 'inputFile')
obsFileName = config.get('data','observationData')
outputFileNameHr = config.get('data', 'outputFileNameHr')
outputFileNameDy = config.get('data', 'outputFileNameDy')
start_date = config.get('data','start_date')
dataType = config.get('data', 'dataType')
spellDay = config.get('data','spellDay')
start_date = config.get('data','start_date')
end_date = config.get('data','end_date')

#data vars
hrVar =config.get('inputVarNames','hrVar')
yrVar = config.get('inputVarNames','yrVar')
dyVar = config.get('inputVarNames','dyVar')
dayCNTvar = config.get('inputVarNames','dayCNTvar')
windVar = config.get('inputVarNames','windVar')
sradVar = config.get('inputVarNames','sradVar')
t2mVar = config.get('inputVarNames','t2mVar')
rhVar = config.get('inputVarNames','rhVar')
waterTempVar = config.get('obsVarNames', 'waterTempVar')

#Pond constants
pond_depth =config.getfloat('modelConstants', 'pondDepth') #meters 
Volume =  config.getfloat('modelConstants', 'pondVolume') #m3
area = config.getfloat('modelConstants', 'pondArea') #m2

#model run info
numberDays = config.getint('data','numberDays') #number days model will run for
saveFile = config.get('data','saveFile')
T_wk = config.getfloat('modelConstants', 'initialTemp') #first day water temp at khulna 

#model constants
water_density = 998 #kg/m3
specific_heat = 4.18 * (10**3)