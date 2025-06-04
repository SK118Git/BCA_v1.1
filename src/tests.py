# ==============================================================================================
# tests.py - File used for testing, serves as a firect entry point into the BA functions 
# ==============================================================================================
# Internal imports:
from bca import run 
# ==============================================================================================

"""
Externally defined parameters that you should know: 
(Update if necessary)
_____________________________________________
| case_type | wind    | wind+solar    | solar |
|_____________________________________________
| value     | 0       | 1             | 2     |
|_____________________________________________

_____________________________________________
| method    | IMV      | BV    | Parkwind    |
|_____________________________________________
| value     | 0       | 1      | 2           |
|_____________________________________________

"""
# ==============================================================================================
# Test for IMV Gamma:


#%% Values for testing IMV -- Test Passed 
from modifiable import AVAILABLE_PLOTS
from bca import run
inputs_2 = {
    "Settlement Period":15.0,
    "Storage RTE":0.7,
    "Green-Certificate Price":0.0,
    "Power Unit CAPEX":2158.3,
    "Capacity Unit CAPEX":442.86, 
    "Annual OPEX Rate":0.02,
    "Project Life":25,
    "Discount Rate":0.0812,
    "Export Transmission Capacity":0.0, 
    "Scenario(s) (seperate with ',' or write 'All')":"All",
    "Timeseries Sheet Name":"Timeseries_Input_2022",
    "Param Analysis Sheet Name":"Parametric Analysis"
}

chosen_plots = {
    "State-Of-Charge": True,
    "Distribution-Of-Power": True, 
}


clean_selected_plots = {
            key: [chosen_plots[key], AVAILABLE_PLOTS[key] ]
            for key in chosen_plots
            }

case_type = 0
file_name = "/Users/sashakistnassamy/Desktop/IMV Gamma - Bus Case.xlsx"
method = 0 

run(file_name, "testing2", True, True, case_type, method, inputs_2, clean_selected_plots)

# ==============================================================================================
# Test for BV 

#%% Values to test BV --- test passed
from modifiable import AVAILABLE_PLOTS
from bca import run 
inputs_2 = {
    "Settlement Period":15.0,
    "Storage RTE":0.7,
    "Green-Certificate Price":0.0,
    "Power Unit CAPEX":2158.3,
    "Capacity Unit CAPEX":442.86, 
    "Annual OPEX Rate":0.06,
    "Project Life":25,
    "Discount Rate":0.0812,
    "Export Transmission Capacity":0.0, 
    "Scenario(s) (seperate with ',' or write 'All')":"All",
    "Timeseries Sheet Name":"BorsseleV_15min_2024",
    "Param Analysis Sheet Name":"Parametric Analysis"
}

chosen_plots = {
    "State-Of-Charge": True,
    "Distribution-Of-Power": True, 
}


clean_selected_plots = {
            key: [chosen_plots[key], AVAILABLE_PLOTS[key] ]
            for key in chosen_plots
            }

case_type = 0
file_name = "/Users/sashakistnassamy/Desktop/Borssele V - Bus Case.xlsx"
method = 1 

run(file_name, "testing2", True, True, case_type, method, inputs_2, clean_selected_plots)

# ==============================================================================================
# Test for Parkwind

#%% Values to test Parkwind -- test passed
from modifiable import AVAILABLE_PLOTS
from bca import run 
inputs_2 = {
    "Settlement Period":15.0,
    "Storage RTE":0.7225,
    "Green-Certificate Price":107.0,
    "Power Unit CAPEX":2000.0,
    "Capacity Unit CAPEX":225.0, 
    "Annual OPEX Rate":0.06,
    "Project Life":30,
    "Discount Rate":0.0812,
    "Export Transmission Capacity":181.5, 
    "Scenario(s) (seperate with ',' or write 'All')":"All",
    "Timeseries Sheet Name":"Timeseries_Input",
    "Param Analysis Sheet Name":"Parametric Analysis"
}

chosen_plots = {
    "State-Of-Charge": True,
    "Distribution-Of-Power": True, 
}

clean_selected_plots = {
            key: [chosen_plots[key], AVAILABLE_PLOTS[key] ]
            for key in chosen_plots
            }

case_type = 1
file_name = "/Users/sashakistnassamy/Desktop/Parkwind - Bus Case_2.xlsx"
method = 2 
run(file_name, "testing", True, True, case_type, method, inputs_2, clean_selected_plots)

# %%
