from bca import run 

"""
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

#%% Values for testing IMV -- Test Passed 
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
    "Scenario (or 'All')":"All",
    "Timeseries Sheet Name":"Timeseries_Input_2022",
    "Param Analysis Sheet Name":"Parametric Analysis"
}

chosen_plots = {
    "State-Of-Charge": True,
    "Distribution-Of-Power": True, 
}

case_type = 0
filename = "/Users/sashakistnassamy/Desktop/IMV Gamma - Bus Case.xlsx"
method = 0 

run(filename, inputs_2, chosen_plots, case_type, method, True, "testing", True)

#%% Values to test BV --- test passed
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
    "Scenario (or 'All')":"B7",
    "Timeseries Sheet Name":"BorsseleV_15min_2024",
    "Param Analysis Sheet Name":"Parametric Analysis"
}

chosen_plots = {
    "State-Of-Charge": True,
    "Distribution-Of-Power": True, 
}

case_type = 0
filename = "/Users/sashakistnassamy/Desktop/Borssele V - Bus Case.xlsx"
method = 1 

run(filename,  inputs_2, chosen_plots, case_type, method, True, "testing", True)

#%% Values to test Parkwind -- test not quite passed (incorrect storge opex, npv and irr)

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
    "Scenario (or 'All')":"All",
    "Timeseries Sheet Name":"Timeseries_Input",
    "Param Analysis Sheet Name":"Parametric Analysis"
}

chosen_plots = {
    "State-Of-Charge": True,
    "Distribution-Of-Power": True, 
}

case_type = 1
filename = "/Users/sashakistnassamy/Desktop/Parkwind - Bus Case_2.xlsx"
method = 2 

run(filename, inputs_2, chosen_plots, case_type, method, True, "testing", False)


# %%
