from configparser import ConfigParserconfig = ConfigParser()config.read('diagnostics_config.ini')#datasaveFile = config.get('data', 'saveFile')outputPath = config.get('data', 'outputPath')modelDataFile = config.get('data', 'modelDataFile')observedDataFile = config.get('data', 'observedDataFile')inputDataFile = config.get('data', 'inputDataFile')#runTimeoutputs = config.get('runTime','outputFluxes')saveFigs = config.get('runTime','saveFigs')units = config.get('runTime','units')year = config.getfloat('runTime','year')allMonth = config.get('runTime','allMonth')