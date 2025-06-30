# =====================================================================================
# bca_class.py - This file defined the BC class which is used to contain all 
# information about the business case which needs to be carried over between functions
# =====================================================================================
# External imports 
from typing import Any
import numpy as np
from openpyxl import load_workbook
import pandas as pd
# =====================================================================================
# Internal imports
from libs.extra import coerce_byte
from libs.logger import log_print
# =====================================================================================


class Business_Case:
    def __init__(self):
    # Variables that don't change per scenario:
        ## Variables defined before BCA
        self.df: pd.DataFrame
        self.param_df: pd.DataFrame
        self.input_values:dict[str, Any]

        self.method:int 
        self.case_type:int

        self.plotting:bool

        ## Variables defined during BCA
        self.years_covered:float 
        self.scenario_list: pd.Series[Any] | list[str]

    # Variables which are defiend per scenario but are needed for the plots
        self.power_level:float
        
        
        return 
    
    
    def setup_globals(self, file_name:str, input_values:dict[str,Any], case_type:int, method:int, gen_flag:bool):
        """
        Function purpose: This function initializes all the variables which can be computed before starting the BC 
        Args:
            file_name: the name of the excel file to check 
            input_values: all the values the user inputted in the Frontend
            case_type: the type of case 
            method: the method being used to calculate the BC 
            gen_flag: a boolean which enables or disables the use of the generalized BC function 
        """
        self.input_values = input_values
        self.df = pd.read_excel(file_name, sheet_name=self.input_values['Timeseries Sheet Name'], header=0, engine="openpyxl")
        self.param_df = read_pdf(file_name, self.input_values["Param Analysis Sheet Name"])
        
        
        self.method = method 
        self.case_type = case_type

        self.plotting = True

        scenario:str= self.input_values["Scenario(s) (seperate with ',' or write 'All')"]
        if scenario.upper() == "ALL":
            self.scenario_list = self.param_df["Scenario"].dropna()
            self.plotting = False 
        else:
            self.scenario_list = [word.strip() for word in scenario.split(",")]

        if gen_flag: 
            self.gen_method_setup()
        return 
    



    def gen_method_setup(self):
            """
            Function Purpose: Setup the environment for the general purpose method to work
            """
            try:
               self.df['Intra-Day Prices [Euro/MWh]'] = self.df["Day-Ahead Prices [Euro/MWh]"] + (self.df["Imbalance Prices [Euro/MWh]"] - self.df["Day-Ahead Prices [Euro/MWh]"]) * 0.5
            except Exception:
                pass 
            try:
                self.df['Available Power [MW]'] = calculate_ap(self.df, self.method)
            except Exception:
                log_print("Didn't calculate ap")
                pass 

            self. df['Available Transmission Capacity [MW]'] = calculate_atc(self.df,self. method, self.input_values)


            self.df["Date"] = pd.to_datetime(self.df["Date"], format="%d/%m/%Y")

            # Compute total days covered
            days_covered = (self.df["Date"].max() - self.df["Date"].min()).days
            days_covered = coerce_byte(days_covered, [float])

            # Convert to years
            self.years_covered = days_covered / 365.25  # Using 365.25 to account for leap years
            return 
            

        

   



def read_pdf(file_name:str, pdf_sheetname:str) -> pd.DataFrame:
    """ 
    Function purpose:  Reads the excel sheet where the parameters by scenario are located \n
    Outputs: a pandas Dataframe of said excel sheet \n
    Note: The reason this function is different than the other is that in the original code  (probably to make the calculations doable for numpy) 
    the dataframe was manipulated in  a particular way. This code slightly modified the previous method to fix a few bugs that arose. \n 

    Args: 
        file_name: the name of the excel file 
        pdf_sheetname: the name of the excel sheet where the parameters are defiend for each scenario 
    """

    # Read Input Parameters from the param_df
    wb = load_workbook(file_name, data_only=True)
    sheet = wb[pdf_sheetname]

    # Convert sheet to DataFrame manually
    data = sheet.values
    cols = next(data)   
    param_df = pd.DataFrame(data, columns=cols)

    return param_df 





# ============================================================================================================================

def calculate_ap(df:pd.DataFrame, method:int) -> pd.Series:
    """
    Function purpose: Calculated the Available Power differently depending on the chosen method 

    Outputs: the column containing the values of Available Transmission Capacity that was computed 

    Args:
        df: a pandas Dataframe containing the timeseries sheet's values 
        method: the chosen method 
    """
    if method == 1: #BV
        df['Available Power [MW]'] = df['Potential Generation [MW]'] - df['Generation Constraint [MW]']
        df['Available Power [MW]'] = np.where(df['Available Power [MW]'] < 0, 0, df['Available Power [MW]'])
    elif method == 0: #IMV
        def siemens_gamesa_power_curve(wind_speed:float)-> float:
            """
            Approximate power curve for Siemens Gamesa SG 14-222 DD wind turbine.
            Input: Wind speed (m/s)
            Output: Power output (MW)
            """
            cut_in = 3       # Minimum wind speed for power generation (m/s)
            rated = 13       # Wind speed where full power is reached (m/s)
            cut_out = 32     # Wind speed where turbine shuts down (m/s)
            max_power = 14   # Rated power output (MW)

            if wind_speed < cut_in or wind_speed >= cut_out:
                return 0  # No power generation
            
            elif wind_speed >= rated:
                return max_power  # Full rated power

            else:
                # Use a logistic (sigmoid) function to approximate smooth ramp-up
                return max_power / (1 + np.exp(-0.5 * (wind_speed - (cut_in + rated) / 2)))

        num_turbines = 72 #1000MW / 14MW = 71.42

        # wake_loss = 0.1 #Wake loss fraction (typically 5-15% offshore)
        # blockage_loss = 0.02 #Blockage loss fraction (typically 1-3% offshore)

        #df['Available Power [MW]'] = (1-wake_loss)*(1-blockage_loss)*num_turbines*df['Wind Speed [m/s]'].apply(siemens_gamesa_power_curve)
        df['Available Power [MW]'] = num_turbines*df['Wind Speed [m/s]'].apply(siemens_gamesa_power_curve)
    return df['Available Power [MW]']

#__________________________________________________________________________________________________________________________________________
def calculate_atc(df:pd.DataFrame, method:int, input_values:dict[str, float|str]) -> pd.Series:
    log_print(f"Calcultating atc with method {method}")
    """
    Function purpose: Calculated the Available Power differently depending on the chosen method 

    Outputs: the column containing the values of Available Power that was computed 

    Args:
        df: a pandas Dataframe containing the timeseries sheet's values 
        method: the chosen method
        input_values: a dictionnary containing all the values inputted by the user
    """
    # Replace with your actual project name
    if method==0: #imv-like
        transformer_rating = 1000 #MW
        #maximum power
        df['Available Transmission Capacity [MW]'] = transformer_rating - df['Capacity Constraint [MW]'] #transmission power rating
    

    elif method == 1: #BV
        #%% Compute Transmisstion Capacity
        transformer_rating = 9.5*2 #MW

        #maximum power: "+ df['Available Power [MW]']" is included since the curtailment figures provided by the developer are relative to the Available Power not the transmission capacity: 
            #E.g. Transmission Capacity = 19MW: 
            #Available Power = 10WM
            #Curtailment = 2MW (realtive to Available Power)
            #Effective Transmission Capacity = 19 - ((19 - 10) + 2) = 8MW 
        df['Available Transmission Capacity [MW]'] = np.where(df['Capacity Constraint [MW]'] == 0,  transformer_rating,
                                                    df['Actual Generation [MW]']) #effective transmission power rating

        df['Available Transmission Capacity [MW]'] = np.where (df['Available Transmission Capacity [MW]'] < 0, 0, df['Available Transmission Capacity [MW]'])
    

    elif method == 2: #parkwind
        #%% Compute Transmisstion Capacity
        transformer_rating = input_values["Export Transmission Capacity"] #MW

        #maximum power
        df['Available Transmission Capacity [MW]'] = transformer_rating - df['Capacity Constraint [MW]'] #transmission power rating
        
    return df['Available Transmission Capacity [MW]'] 
