import pandas as pdimport diagnosticsFuncsimport diagnosticsVarsoutputPath = diagnosticsVars.outputPathModeled = pd.read_csv(diagnosticsVars.modelDataFile)observed = pd.read_csv(diagnosticsVars.observedDataFile)inputData= pd.read_csv(diagnosticsVars.inputDataFile)Modeled['T_aC'] = inputData['T2M']observed["date"] = pd.to_datetime(observed["date"])outputs = diagnosticsVars.outputssaveFigs = diagnosticsVars.saveFigsunits = diagnosticsVars.unitsyear = diagnosticsVars.yearallMonth = diagnosticsVars.allMonthif outputs == "y":    if units == "W":        fluxes = ["Qrap", "Qras", "Qraa", "Qevap", "Qconv"]    elif units == "W/m2":        fluxes = ["Qrap_Wm-2", "Qras_Wm-2", "Qraa_Wm-2", "Qevap_Wm-2", "Qconv_Wm-2"]elif outputs == "n":    fluxes = ["T_wC"]if allMonth == "y":    month = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]    print("***generating plots for all months***")    diagnosticsFuncs.plotYearlyAvg(Modeled,year,units,saveFigs,outputPath)    for m in month:        month = float(m)        diagnosticsFuncs.plotMonthlyModeled(Modeled,month,year,units,fluxes,saveFigs,outputPath)        diagnosticsFuncs.plotMonthlyObserved(observed,Modeled,month,year,saveFigs,outputPath)elif allMonth == "n":    month = float(input("input month as integer: "))    print(f"***generating plots for month: {month}***")    diagnosticsFuncs.plotMonthlyModeled(Modeled,month,year,units,fluxes,saveFigs,outputPath)    diagnosticsFuncs.plotMonthlyObserved(observed,Modeled,month,year,saveFigs,outputPath)    diagnosticsFuncs.plotYearlyAvg(Modeled,year,units,saveFigs,outputPath)elif allMonth == "custom":    monthCustom = input("input months you want as integers (eg: 1 2 3): ")    month = monthCustom.split()    print(f"***generating plots for months: {monthCustom}***")    diagnosticsFuncs.plotYearlyAvg(Modeled,year,units,saveFigs,outputPath)    for m in month:        month = float(m)        diagnosticsFuncs.plotMonthlyModeled(Modeled,month,year,units,fluxes,saveFigs,outputPath)          diagnosticsFuncs.plotMonthlyObserved(observed,Modeled,month,year,saveFigs,outputPath)