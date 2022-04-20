import bechet_modelfrom configparser import ConfigParserimport pandas as pdimport datetime as dtconfig = ConfigParser()config.read('Bechet_config.ini')filesPath = config.get('data', 'filesPath')dataType = config.get('data', 'dataType')outputPath = config.get('data','outputFilesPath')numberDays = config.getint('data','numberDays')saveFile = config.get('data','saveFile')start_date = config.get('data','start_date')#how does this format?start_date = dt.datetime.strptime(start_date, "%d-%m-%Y")if dataType == 'H':    inputFileName = config.get('data', 'inputFile') #load input data    data = pd.read_csv(f'{filesPath}{inputFileName}') #df of input data    print(data)    obsFileName = config.get('data','observationData') #load observation data    observed = pd.read_csv(f'{filesPath}{obsFileName}') #observed data    observed['date'] = pd.to_datetime(observed['date'])    bechet_model.main_simulation_loop(data,observed,filesPath,numberDays,saveFile,outputPath) #run main sim loopelse: #if dataType == 'C':    inputFileName = config.get('data', 'inputFile')    data = pd.read_csv(f'{filesPath}{inputFileName}')    print(data)    bechet_model.climatology_simulation_loop(data, filesPath)