# ============================================================================================================================
# bca_entrypoint.py - File containing the intersection between the frontend, and the BC tool
# ============================================================================================================================
# External Imports 
import pandas as pd
from typing import Any
# ============================================================================================================================
# Internal Imports 
from modify.bca_class import Business_Case
from methods.general_method import general_method
from methods.bv_method import bv_method
from methods.imv_method import imv_method
from libs.extra import find_scenario_index
from libs.excel import force_excel_calc,save_to_excel
from libs.logger import log_print
from frontend.popup import Progress_Popup
# ============================================================================================================================

# This is the entry point into the BCA 
def run(file_name:str, output_sheet_name:str, debug_mode:bool, paste_to_excel:bool, case_type:int, method:int, input_values:dict[str, Any], chosen_plots:dict[str, Any],  progress_pp:Progress_Popup, gen_flag=False, recalc_flag=False):
    """
    Function purpose: this function serves as the entry point into the BC logic \n 
    Args: 
        file_name: the name of the excel file studied 
        output_sheet_name: the sheet the result should be saved to if paste_to_excel is True 
        debug_mode: enables additional print statements for debugging and backtracing 
        paste_to_excel: determines whether or not the final result needs to be saved directly to excel, if False will just copy to clipboard 
        case_type: the type of case being studied 
        method: the type of method being used to calculate the available pwoer and transmission capacity 
        input_values: a dictionnary where all the user inputed values (through the GUI) are, can also be defined manually like in tests.py: (key:string|float) 
        chosen_plots: a dictionnary where the information is stored about which polots the user chose to do:  (key:boolean) 
        progress_pp: the progress bar and the label that appears above the progress bar, set to optional for compatibility with tests 
        gen_flag: a boolean which enables or disables the use of the generalised BC method
    """
    if not(recalc_flag): force_excel_calc(file_name) # Force excel to recalculate the sheets of the file, this adds overhead but elimantes many bugs 
    business_case = Business_Case() 
    business_case.setup_globals(file_name, input_values, case_type, method, gen_flag)

    progress_counter:int = 0
    for scenario_name in business_case.scenario_list:
        scenario_index = find_scenario_index(business_case.param_df, scenario_name)
        launch_analysis_new(business_case, scenario_index, debug_mode, gen_flag)
        progress_counter +=1
        for key in chosen_plots:
            if chosen_plots[key][0]:
                chosen_plots[key][1](business_case, scenario_name, debug_mode)
        percent: float = (progress_counter/len(business_case.scenario_list)) * 100
        log_print(f"Progress: {percent}% done")
        
        progress_pp.update_vals("Computing Simulation", percent)
        
    log_print("Simulations Complete! \n ")

    selected_data: pd.DataFrame = business_case.param_df.iloc[:, 7:] # type: ignore

    # Copy to clipboard without the index
    selected_data.to_clipboard(index=False, header=False)

    log_print("Data copied to clipboard!\n")
    progress_pp.update_vals("Data Copied to Clipboard", 0)
   
    if paste_to_excel: 
        progress_pp.update_vals('Beginning save to excel', 0)
       
        save_to_excel(file_name, output_sheet_name, debug_mode, business_case.param_df, progress_pp)
    
    log_print("Program execution complete!")
    return 

#_______________________________________________________________________________________________________________________________________________________________________________

def launch_analysis_new(business_case:Business_Case, scenario_index:int, debug_mode:bool, gen_flag:bool):
    """
    Function purpose: This function links together all the BC methods
    Args:
        business_case: the class which contains all usefuk information about the business_case which needs to carry over 
        scenario_index: the index of the currently studeid scenario
        debug_mode: a boolean which when True adds more print statements/logs
        gen_flag: a boolean which enables or disables the use of the generalized BC function 
    """
    log_print(f"Current Value of method is {business_case.method}")
    if gen_flag:
        log_print("Using general method")
        try: 
            general_method(business_case, scenario_index, debug_mode)
            return 
        except Exception: pass

    if business_case.method == 0:
        log_print("Using Method 0")
        imv_method(business_case, scenario_index)
    elif business_case.method == 1:
        log_print("Using Method 1")
        bv_method(business_case, scenario_index)
    elif business_case.method == 2:
        #log_print("Using Method 2")
        #parkwind_method(business_case, scenario_index)
        general_method(business_case, scenario_index, debug_mode) #the parkwind only method is broken and idk why. but the general one works

    # Add your methods here following the same format
    # Note: Remember! the value of the method (0, 1, 2, ...) depends on the order of its definition in settings.py in the Choice Matrix, 
    # counting from left to right, top to bottom, starting at 0 
    # Read the instructions.pdf file for more details 
    return 

