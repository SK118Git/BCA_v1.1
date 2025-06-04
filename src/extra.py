# =================================================================================================================================
# extra.py - File containg all functions that don't need to be modified, are not used for plotting, nor the GUI, not the BCA 
# =================================================================================================================================
# External Imports 
#__________________________________________________________________________________________________________________________________
# Main imports 
import pandas as pd 
import numpy as np
import numpy_financial as npf
from typing import TypeVar, Any, Sequence, Callable 


# ==================================================================================================================================
# 
T = TypeVar('T')
def coerce_byte(input:Any, desired_types:Sequence[Callable[[str], T]]) -> T:
    """ 
    Function purpose: This function allows safe coercion from the Pandas Scalar type to any other type (the problem is that Scalar can 
                      be a bytes type and as such cant be directly coerced into a numeric type, needing to be first decoded into a string) \n
    Inputs: \n
        input: the variable you want to change the type of \n
        desired_types = a list containing the names of the types you want to potentially coerce it to \n
    Outputs: the inout variable but safely coerced to the minimal desired type \n
    Note: The user can put [int, float] in which case the function will coerce to int if possible, else will coerce to float 
    """
    if isinstance(input, bytes):
        input_str: str = input.decode()
        for dtype in desired_types:
            try:
                # Try coercing; check if float is actually an int
                coerced: T = dtype(input_str)
                # Optional: Avoid converting 15.0 to float if 15 is valid as int
                if type(coerced) == float:
                    if coerced.is_integer() and int in desired_types:
                        return int(coerced)
                return coerced
            except Exception:
                continue
        raise ValueError("Could not coerce input to any desired type")
    else:
        return input


# ============================================================================================================================
# Functions that define methods or utilities for dictionnaries 

def find_scenario_index(df:pd.DataFrame, scenario:str) -> int :
    """ 
    Function purpose: Finds the row number of a given scenario to then be able to index the other values by that number \n
    Inputs: \n
        df = the dataframe (or excel sheet) where all the scenarios are stored with their respective parameters \n
        scenario = the label of the scenario (ex: B7) \n
    Outputs: the row number - 1 where the given scenario label is located on the excel sheet \n
    """
    index_value = df.index[df["Scenario"] == scenario].tolist()
    if not index_value:
        raise ValueError(f"Scenario '{scenario}' not found in DataFrame") # raise Error if not found
    return index_value[0]  



Key = TypeVar("Key")
def update_dict(my_dict:dict[Key, list[Any]], key:Key, new_value:Any) -> None:
    """ 
    Function purpose: Takes a python dictionnary and add a value to a key \n
    Inputs: \n
        my_dict = any python dictionnary where each key is associated to a LIST \n
        key = the key in the dictionnary where the entry needs to be added \n
        new_value = the new value to add \n
    Outputs: None
    """
    if key not in my_dict: 
    # if the key doesn't exist yet then create it and directly assign the value
        my_dict[key] = [new_value]
    elif len(my_dict[key]) > 1:
    # if the key has at least 2 values in its associated list, replace the second value
        my_dict[key][1] = new_value
    else:
    # else add the new value to the list associated to the key 
         my_dict[key].append(new_value)
    return 




def find_index(container:dict[Key, Any], search_for:Key) -> int:
    """ 
    Function purpose: Finds the index of a given key in a dictionnary  \n
    Inputs: \n
        container = a python dictionnary \n
        search_for = the key to find \n
    Outputs: the index of the key, or -1 if an error has occurred
    """
    try:
        return list(container.keys()).index(search_for)
    except ValueError:
        raise ValueError(f"Key '{search_for}' not found in dictionnary")
    

# ============================================================================================================================
# All tht follows are functions useful for the BCA 
def safe_irr(cash_flows) -> float:
    """ 
    Function purpose:  Ensures the calculated irr value isn't a completely unrealistic value \n
    Inputs: the cash flows \n
    Outputs: a cleaned irr 
    """
    irr = npf.irr(cash_flows)
    
    if np.isnan(irr):
        # Case where IRR is not computable
        return -0.20
    elif irr > 1.0:
        # Case where IRR is unrealistically high (>100%)
        return np.nan
    else:
        return irr

