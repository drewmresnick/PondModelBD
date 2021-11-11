# PondModelBD
Repository for building energy flux model for pond aquaculture in Bangladesh.

Reach out to Drew Resnick (drewr@iri.columbia.edu) for access to input data.

Not all the files in this folder are up-to-date. The two main working files are briefly
outlines below.

1. Bechet_model.py (file to run the model)

    Model elements:

    Qra,p: radiation from pond surface (W)
    Qra,s: total (direct and diffuse) solar radiation (W)
    Qra,a: radiation from air to pond (W)
    Qev: evaporative heat flux (W)
    Qconv: convective flux at pond surface (W)
    Qcond: conductive flux with ground at pond bottom (W) #not using
    Qi: heat flux associated with water inflow (W)
    Qr: heat flux induced by rain (W) #not using

    This file will ask for three inputs when run:
        1. number of days to run the model
        2. directory path to where files are held
        3. if you would like to save the outputs (enter (y) if you would like to run
                                                  accompanying diagnostics file
                                                  for the model)

2. Diagnostics_bechet.py (file to run diagnostics on outputs from Bechet_model.py)   

    This script will run diagnostics plots for outputs of the bechet_model.py python script.

    When you run this script, it will ask you a series of questions to determine which
    plots to generate.

    Check the outputs from the model to determine which year(s) and month(s) will be valid
    as inputs for diagnostics. This depends on number of days you ran the model for.

    Please note that there were issues with displaying plots without saving them when running
    on python directly in terminal. If your plots do not display, please try using a GUI such
    as spyder or jupyter notebook.

    Use this script to generate plots for:
        1) hourly fluxes for any month and year
        2) air temp (measured) vs water temp (Modeled) for any month and year
        3) hourly modeleld water temp for any month and year
        4) hourly changes in heat flux (annual avg) for any year

    Plots will be saved to current working directory if you return "y" as input for
    this option when running the script.                                   
