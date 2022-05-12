# PondModelBD
**Repository for building energy flux model for pond aquaculture in Bangladesh.**

Reach out to Drew Resnick (drewr@iri.columbia.edu) for access to input data.

**There are two models under development in this repository, based off previously published research.**      
Please refer to the main runFiles in each model subdirectory for more model specific information regarding model assumptions.  
1. [**Béchet model**](https://pubs.acs.org/doi/abs/10.1021/es1040706?casa_token=ESVwMRuKWPcAAAAA:HW2Sep8goMov3i3losRrXzoIGboixMLpDiK4P8XxgKxK1asz4I_xuzJ0tKGTFrIVi4oJjamJCc3QAA)  
    - Fully mixed shallow algal pond model  
    - Required input hourly csv data of:  
        1. Temperature at 2m (C)  
        2. Temperature at 2m (K)  
        3. Relative humidity at 2m (%)  
        4. Wind Speed at 2m (m/s)  
        5. Total direct and diffuse solar irradiance (W/m2)  
        6. Year (yyyy)  
        7. Month (mm)  
        8. Day (day of year, 1-365)  
        9. Day count (total number of days of dataset, 1-n)  
    - Required realtime daily measured data of:  
        1. Day count (total number of days of dataset, 1-n)  
        2. Date (dd/mm/yyyy)  
        3. Morning/minimum, afternoon/maximum, average air temperature (C)  
        4. Morning/minimum, afternoon/maximum, average water temperature (C)  
        
    The Béchet model also has an associated diagnostics subdirectory which gives overview plots of individual heat fluxes for each model element.  
    The structure of this subdirectory follows the main model subdirectories shown below.  

2. [**Gao&Merrick model**](https://www.semanticscholar.org/paper/Simulation-of-temperature-and-salinity-in-a-fully-Gao-Merrick/e062ad4f52f4eed06c57285d871e8b8f2257b57d)  
    - Fully mixed pond model  
    - Required input daily csv data of:  
        1. Temperature at 2m (C)  
        2. Temperature at 2m (K)  
        3. Relative humidity at 2m (%)  
        4. Wind Speed at 2m (m/s)  
        5. Total direct and diffuse solar irradiance (W/m2)  
        6. Year (yyyy)  
        7. Month (mm)  
        8. Day (day of year, 1-365)  
    - Required realtime daily measured data of:  
        1. Date (dd/mm/yyyy)  
        2. Morning/minimum, afternoon/maximum, average water temperature (C)  


#### Repository structure  
The file structure for each model is as follows:  
    1. model_config.ini : Configuration file where you input runtime information to read into the model.  
        - make sure to read through the configuration file to understand how to change inputs to fit 
          your model run and data correctly.  
    2. model_runFile.py : Main runtime file that runs the model.  
    3. modelVars.py : Variables file which reads in variables from configuration file.  
    4. modelFuncs.py : Functions file which includes all the model and plotting functions.  


#### python packages needed for runtime  
> import numpy as np  
> import datetime as dt  
> import math  
> import matplotlib.pyplot as plt  
> import pandas as pd  


#### model citations:
1. Béchet et al (2011). Universal Temperature Model for Shallow Algal Ponds Provides Improved Accuracy. *Environ. Sci. Technol.* 45(8): pp 3702-3709.  
2. Gao, Merrick (1996). Simulation of temperature and salinity in a full mixed pond. *Environmental Software*. 11: pp 173-178.  