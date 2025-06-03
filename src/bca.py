# ============================================================================================================================
# bca.py - File containg all functions that don't need to be modified, are not used for plotting, nor the GUI, not the BCA 
# ============================================================================================================================
# External Imports 
import pandas as pd
import numpy as np
import numpy_financial as npf

# ============================================================================================================================
# Internal Imports 
from extra import find_scenario_index, safe_irr, read_pdf, read_df, save_to_excel, force_excel_calc
from plots import plot_dop, plot_soc 
from tomodfiy import calculate_ap, calculate_atc
# ============================================================================================================================

# Notes: mofify parameter order to be homogenous, properly define parameters of run_bus_case() and replace all the try catch with if statements

# This is the entry point into the BCA 

def run(filename, input_values, chosen_plots, case_type, method, paste_to_excel, output_sheet_name, debug_mode):
    """
    Function purpose: this function serves as the entry point into the BC logic 
    Inputs:
        filename = the name of the excel file studied
        input_values = a dictionnary where all the user inputed values (through the GUI) are, can also be defined manually like in tests.py = (key:string|float) 
        chosen_plots = a dictionnary where the information is stored about which polots the user chose to do =  (key:boolean)
        case_type = the type of case being studied
        method = the type of method being used to calculate the available pwoer and transmission capacity 
        paste_to_excel = determines whether or not the final result needs to be saved directly to excel, if False will just copy to clipboard
        output_sheet_name = the sheet the result should be saved to if paste_to_excel is True
        debug_mode = enables additional print statements for debugging and backtracing 
    Outputs: None
    Note: The BCA logic was split into these subfunctions to allow for modularity and the multitude of methods/cases
    """
    force_excel_calc(filename)
    df_sheetname = input_values['Timeseries Sheet Name']
    pdf_sheetname = input_values["Param Analysis Sheet Name"]
    df = read_df(filename, df_sheetname)
    param_df = read_pdf(filename, pdf_sheetname)
    scenario = input_values["Scenario (or 'All')"]
    try:
        df['Intra-Day Prices [Euro/MWh]'] = df["Day-Ahead Prices [Euro/MWh]"] + (df["Imbalance Prices [Euro/MWh]"] - df["Day-Ahead Prices [Euro/MWh]"]) * 0.5
    except Exception:
        pass 
    try:
        df['Available Power [MW]'] = calculate_ap(df, method)
    except Exception:
        print("Didn't calculate ap")
        pass 

    df['Available Transmission Capacity [MW]'] = calculate_atc(df, method, input_values)


    df["Date"] = pd.to_datetime(df["Date"], format="%d/%m/%Y")

    # Compute total days covered
    days_covered = (df["Date"].max() - df["Date"].min()).days

    # Convert to years
    years_covered = days_covered / 365.25  # Using 365.25 to account for leap years

    if scenario.upper() == "ALL":
        launch_full_analysis(df, input_values, param_df, years_covered, case_type, method, filename, output_sheet_name, paste_to_excel, debug_mode)
    else:
        power_level = launch_single_analysis(df, input_values, param_df, years_covered, case_type, method, scenario, filename, output_sheet_name, paste_to_excel, debug_mode)
        if chosen_plots['State-Of-Charge']:
            plot_soc(df)
        if chosen_plots['Distribution-Of-Power']:
            plot_dop(df, power_level)

    return 

#_______________________________________________________________________________________________________________________________________________________________________________

def launch_single_analysis(df, input_values, param_df, years_covered, case_type, method, scenario, filename, output_sheet_name, paste_to_excel, debug_mode):
    """
    Function purpose: Launches a BC Analysis for a single scenario
    Inputs:
        df = the dataframe holding the timeseries values
        input_values = a dictionnary where all the user inputed values (through the GUI) are, can also be defined manually like in tests.py = (key:string|float) 
        param_df = the dataframe holding the values of the parameters for each scenario 
        years_covered = the amount of time the timeseries values oversee (defined in the run() function)
        case_type = the type of case being studied
        scenario = the name of the scenario 
        filename = the name of the excel file studied
        output_sheet_name = the sheet the result should be saved to if paste_to_excel is True
        paste_to_excel = determines whether or not the final result needs to be saved directly to excel, if False will just copy to clipboard
        debug_mode = enables additional print statements for debugging and backtracing 
    Outputs: the power level defined here (which is needed for the plots afterwards)
    Note:
    """
    i = find_scenario_index(param_df, scenario)
    PPA_price = param_df.loc[i, 'PPA Price']
    bal_per = param_df.loc[i, 'Balancing Market Participation']

    try: 
        price_type = param_df.loc[i, 'Market Type']
    except Exception:
        if debug_mode: print(f"An error has occured with price_type assignment: {Exception}")
        price_type = ""

    power_level = param_df.loc[i, 'Storage Power Rating']
    storage_time_hr = param_df.loc[i, 'Duration']

    if case_type == 1:
        solar_MWp = param_df.loc[i, 'Solar Installed (MWp)']
    else:
        solar_MWp = 0 
        
    result = run_bus_case(df=df, input_values=input_values, PPA_price=PPA_price, bal_per=bal_per, price_type=price_type, power_level=power_level, storage_time_hr=storage_time_hr, years_covered=years_covered, case_type=case_type, solar_MWp=solar_MWp)

    if case_type == 1: 
        param_df.iloc[i, 8:24] = result
    else:
        if method == 1:
            param_df.iloc[i, 8:24] = result
        else: 
            param_df.iloc[i, 7:22] = result 

    print("\nSimulations Complete! \n ")

    selected_data = param_df.iloc[:, 7:]

    # Copy to clipboard without the index
    selected_data.to_clipboard(index=False, header=False)

    print("Data copied to clipboard!\n")

    if paste_to_excel: 
        save_to_excel(filename, param_df, output_sheet_name)

    return power_level # we need to obtain the power_level later for one of the plots  



def launch_full_analysis(df, input_values, param_df, years_covered, case_type, method, filename, output_sheet_name, paste_to_excel, debug_mode):
    """
    Function purpose: Does the BCA for every scenario 
    Inputs:
        df = the dataframe holding the timeseries values
        input_values = a dictionnary where all the user inputed values (through the GUI) are, can also be defined manually like in tests.py = (key:string|float) 
        param_df = the dataframe holding the values of the parameters for each scenario 
        years_covered = the amount of time the timeseries values oversee (defined in the run() function)
        case_type = the type of case being studied
        filename = the name of the excel file studied
        output_sheet_name = the sheet the result should be saved to if paste_to_excel is True
        paste_to_excel = determines whether or not the final result needs to be saved directly to excel, if False will just copy to clipboard
        debug_mode = enables additional print statements for debugging and backtracing 
    Outputs: the power level defined here (which is needed for the plots afterwards)
    Outputs: None 
    Note: The code doesn't allow you to compute plots if you chose to do every scenario for obvious performance reasons, although this could be remedied if wanted 
    """

    print(f"Computing for all scenarios")
    for i in range(len(param_df)-1):  #range(86,87):  
        PPA_price = param_df.loc[i, 'PPA Price']
        bal_per = param_df.loc[i, 'Balancing Market Participation']
        try: 
            price_type = param_df.loc[i, 'Market Type']
        except Exception:
            print(f"Exception type: Exception")
            price_type = ""

        power_level = param_df.loc[i, 'Storage Power Rating']
        storage_time_hr = param_df.loc[i, 'Duration']

        if case_type == 1:
            solar_MWp = param_df.loc[i, 'Solar Installed (MWp)']
        else:
            solar_MWp = 0 
            
        result = run_bus_case(df=df, input_values=input_values, PPA_price=PPA_price, bal_per=bal_per, price_type=price_type, power_level=power_level, storage_time_hr=storage_time_hr, years_covered=years_covered, case_type=case_type, solar_MWp=solar_MWp)



        if case_type == 1: 
            param_df.iloc[i, 8:24] = result
        else:
            if method == 1:
                #print(f"i= {i}")
                #print("param df: ", param_df)
                #print("result", result)
                print("7:24")
                param_df.iloc[i, 7:24] = result
            else: 
                param_df.iloc[i, 7:22] = result 

        #if case_type == 1:
        #    param_df.iloc[i, 8:24] = result
        #else:
        #    param_df.iloc[i, 7:22] = result 

        print(f"{int((i/(len(param_df)-1)) * 100)} % done")

    print("\nSimulations Complete! \n ")

    selected_data = param_df.iloc[:, 7:]

    # Copy to clipboard without the index
    selected_data.to_clipboard(index=False, header=False)

    print("Data copied to clipboard!\n")


    if paste_to_excel: save_to_excel(filename, param_df, output_sheet_name)

    return   


#_______________________________________________________________________________________________________________________________________________________________________________

def run_bus_case(df, input_values, PPA_price, bal_per, price_type, power_level, storage_time_hr, years_covered, case_type, solar_MWp=0):
    """
    Function purpose: This function is the one that actually computes the BC given the user defined inputs and the scenario parameters
    Inputs:
        df = the timeseries dataframe
        input_values = the user defined inputs
        PPA_price = 
        bal_per = percentage of energy allocated to the balancing market 
        price_type = either IMB or INTRA 
        power_level 
        storage_time_hr 
        years_covered
        case_type = the type of case being studied
        solar_MWp = energy generated by solar panels? (only used if the case is based on either mixed or only solar panel usage)
    Outputs: a dataframe called results which contains the result of the BC
    Note:
    """
    global cash_flows

    #% INPUT VALUES
    #settlement period as a fraction of an hour: 15 min = 0.25
    settlement_period = input_values['Settlement Period'] /60 

    # Determine which Energy Prices to Use (based on "Market Type Parameter")
    
    # Mapping logic
    if price_type.upper() == "IMB":
        df["Balancing Prices"] = df['Imbalance Prices [Euro/MWh]']
    elif price_type.upper() == "INTRA":
        df["Balancing Prices"] = df['Intra-Day Prices [Euro/MWh]']
    elif price_type == "":
        df["Balancing Prices"] = df['Balancing Prices [Euro/MWh]']
    else:
        raise ValueError("Invalid price type. Use 'IMB' or 'INTRA'.")
    
    #efficiency charging and discharging: square root of the RTE
    efficiency = input_values['Storage RTE'] ** 0.5

    #power price
    # discount_on_wholesale = input_values['Discount on Day-Ahead'].iloc[-1]  #Wholesale_Price Calculation below
    green_certificate = input_values['Green-Certificate Price'] #€/MWh renewable energy producers receive these in proportion to their production, and offshore wind projects benefit by law from a guaranteed 4 June 2014 purchase of these "green certificates" by Elia, the Belgian grid operator, at a fixed price of 107 EUR/MWh for 20 years.
    
    # Storage capacity 
    capacity = power_level * storage_time_hr

    # #Adjust Solar Power based on Scenario (Default Data is for 15 MWp)
    if case_type == 1: 
        df['Available Power [MW]'] = df['Belwind (181MW)'] + ((solar_MWp/15) * df['OOE Production (15MWp) [MW]'])    
    #Limit Exported Power to the Transmission Capacity: This corresponds to the "No Storage" scenario and is used for calculating over-production available for charging
    

    df['Exported Power [MW]'] = np.where(df['Available Power [MW]'] > df['Available Transmission Capacity [MW]'], df['Available Transmission Capacity [MW]'], df['Available Power [MW]']) 
    
    #df['Exported Power [MW]'] = df['Actual Generation [MW]']
    
    #for hybrid projects: (Wind+Solar), Available Power [MW] should already account for combined energy sources

    #deltapower: delta between available power and transmission capacity, -ve values correspond to overproduction wrt to max power
    df['deltapower'] = df['Available Transmission Capacity [MW]'] - df['Available Power [MW]'] 
        #deltapower > 0: underproduction relative to Available Transmission Capacity
        #deltapower < 0: overproduction relative to Available Transmission Capacity

    #Balancing power [MW]
    #df['bal_power'] = bal_per / 100 * df['Available Power [MW]'] #amount of power to be allocated to balancing market as % of available power
    df['bal_power'] = bal_per * df['Exported Power [MW]']   #amount of power to be allocated to balancing market as % of power being exported

    # PPA_price = input_values['PPA Price'].iloc[-1]
    df['Wholesale_Price'] = PPA_price; #df['Day Ahead Price [Euro/MWh]']*(1-discount_on_wholesale) 

    #### Charging and Discharging Strategy

    #CHARGING
    # theor_charging: Power being pulled from the grid [MW]:
        # when there is overproduction relative to transmission (deltapower < 0): the maximum charging is the overproduced power
        # when there is underproduction (deltapower ≥ 0): 
            #if balancing prices are -ve: Charge at max power
            #if balancing prices are +ve: do nothing
    df['theor_charging'] = np.where (df['deltapower'] < 0 , - df['deltapower'] , 
                                     np.where ((df["Balancing Prices"] < 0 ) , power_level , 0 ))

    # efficiency charging: actual energy GOING INTO THE STORAGE SYSTEM after conversion losses
    df['eff_charging'] = df['theor_charging'] * efficiency
    
    # DISCHARGING
    #this is the maximum possible discharging rate: 
        #based on the rated power of the storage system and the maximum available transmission capacity (which ever is the smallest)
    df['max_discharging'] = np.where (df['deltapower'] < 0 , 0 , -1 * np.minimum(power_level, df['deltapower']/efficiency))  #corrected for effiency since this is the discharge from storage (before conversion)
    
    # theor_discharging: discharge at full rated output of the storage system
        # when there is overproduction relative to transmission constraint (deltapower < 0): do nothing
        # when there is underproduction (deltapower ≥ 0): 
            #if balancing prices are MORE than X * the day-ahead or fixed price (e.g. PPA): Discharge at the maximum possible discharging rate: df['max_discharging']
            #if balancing prices are LESS than X * the day-ahead or fixed price (e.g. PPA): do nothing
            
    df['theor_discharging'] = np.where (df['deltapower'] < 0 , 0 ,
                              np.where (df["Balancing Prices"] > (1.3 * df['Wholesale_Price']) , df['max_discharging'] , 0 ))          
                              #np.where (df["Balancing Prices"] > (1.3 * df['Wholesale_Price']) , - power_level , 0 )) #original command in AIS code did not respect transmission constraint
                                         
    # Maximum charging or discharging power
    # Add a column to the DF with the Max Charging/Discharging profile: where Charging is zero, put the theoretical discharge output, where it is not zero, leave as is
    # Used for calculating the end_soc_values
    df['maximum_charge_discharge'] = np.where (df['eff_charging'] == 0, df['theor_discharging'], df['eff_charging'])

    ## State of Charge Calculations

    # soc_values will eventually contain all the end_soc values. Foregoing initial_soc.
    soc_values = [0]

    # soc_diffs is a combination of actual_charge and actual_discharge, with charge values being positive and discharge values being negative
    max_charge_or_discharge_np = df['maximum_charge_discharge'].to_numpy()

    #define functions
    for i in range(len(df)):
      soc_val = np.clip(soc_values[-1] + max_charge_or_discharge_np[i]*(settlement_period), a_min = 0, a_max = capacity)
      soc_values.append(soc_val)

    #create the cumulitive state of charge dataframe
    df["end_soc_values"] = soc_values[1:]           #

    #create the charging/discharging parameter
    #'charge_discharge': energy in (>0) and out (<0) of the system
    df['charge_discharge'] = (df['end_soc_values'] - df['end_soc_values'].shift(+1))/settlement_period #Power = d(SOC)/dt

    #remove the nan from the first line
    df['charge_discharge'] = df['charge_discharge'].replace(np.nan, 0)

    #define discharge efficiency
    #'eff_charge_discharge': energy in (>0) and out (<0) out at storage-grid connection point (used for revenue calculation)
    df['eff_charge_discharge'] = np.where(df['charge_discharge'] >= 0, df['charge_discharge'] / efficiency , df['charge_discharge'] * efficiency )

    #create the percentage state of charge
    df['per_state_of_charge'] = (df["end_soc_values"] * 100) / capacity

    ## Revenue Calculations

    #Theoretical Windfarm revenue 
    #Standard wind farm income based on Exported Power (as imported from Excel)
    df['baseline_income'] = ((df['Wholesale_Price'] + green_certificate ) * df['Exported Power [MW]'] ) * settlement_period 

    #Total income when considering balancing market participation (no storage): directly exporting portion of energy to balancing market, e.g 85% wholesale + 15% Balancing Market
    df['bal_income'] = ((df['Wholesale_Price']+ green_certificate) * (df['Exported Power [MW]'] * (1-bal_per)* settlement_period)) + (bal_per * df['Exported Power [MW]'] * (df["Balancing Prices"] + green_certificate) * settlement_period)
    # Storage Revenue (only attributed directly to storage) SIGN OF BALANCING PRICES: (-ve Balance Price = PAID TO CHARGE)
        #[A]: IDLE (Not Charging or Discharging): assign balancing market income
        #[B]: DISCHARGING: assign balancing market income corrected for what is being delivered by storage system (if balancing prices are +ve then it will increase the income)
        #[C]: CHARGING: If there is Over Production (delta power < 0) (can't discharge): attribute the full balancing market income to storage (based on Exported Power -> so already corrected for transmission constraint)
        #[D]: CHARGING: If Storage Power Rating < Balancing Market Assigned Power (X% of Available Power): All Charging from Balancing Market: assign balancing market income corrected for what is being charged by storage system (if balancing prices are -ve then it will increase the income during charging)
        #[E]: CHARGING: If Storage Power Rating < Exported Power: attribute Charging from Balancing Market (charging here happens only when Balance Prices are -ve) 
        #[F]: CHARGING: Otherwise: Exported < Storage Power Rating: pull down output into negative (charging from grid) (charging here only happens only when Balance Prices are -ve) 
    try:
        df["Balancing Prices"] = df['Balancing Prices [Euro/MWh]']
    except Exception:
        pass 
    
    df['storage_income'] = np.where (df['eff_charge_discharge'] == 0, df['bal_income'],  #[A]
                           np.where (df['eff_charge_discharge'] < 0 , df['bal_income'] - df['eff_charge_discharge'] * df["Balancing Prices"]* settlement_period, #[B]
                           np.where (df['deltapower'] < 0           , df['bal_income'],  #[C]       
                           np.where (power_level <= df['bal_power'] , df['bal_income'] - df['eff_charge_discharge'] * df["Balancing Prices"] * settlement_period, #[D]
                           np.where (power_level <= df['Exported Power [MW]'] , df['bal_income'] - df['bal_power']*df["Balancing Prices"]*settlement_period - (df['eff_charge_discharge'] - df['bal_power']) * (df['Wholesale_Price'] + df["Balancing Prices"])*settlement_period, #[E]
                           (df['bal_power'] - power_level) * df["Balancing Prices"] * settlement_period #[F]
                            )))))                         
    
    #correct Exported Power for what is discharged and charged from the grid:
        #when charging: What is produced - what has been charged = what is exported / but clipped to the transmission capacity (n case SOC = 100% and cannot charge any more)
        #when discharging: what is produced + what has been discharged (should be automatically clipped to the transmission given discharing rate calc)
    df['Net Exported Power_Storage [MW]'] = df.apply(lambda row: min(row['Available Power [MW]'] - row['eff_charge_discharge'], 
                                                                     row['Available Transmission Capacity [MW]']), axis=1)
    
    #Extra income from Generation-Based Compenstation: since baseline_income and bal_income are both computed on the basis of EXPORTED output
    #Generation that was above transmission constraint AND stored:
    df['extra_generation'] = np.where (df['deltapower'] < 0, df['eff_charge_discharge'], 0)
    df['extra_generation_income'] = df['extra_generation'] * green_certificate * settlement_period #Extra income on green certificates awarded for generation of clean energy
    
    #%%
    #Calculate effective curtailment rate: when delta_power < 0 (over production):
        # if SOC < 100% |delta_power| = charging_rate (charge with over production) and there is no curtailment
        # if SOC = 100% (or No Storage): |delta_power| - charging_rate = curtailed energy
    #so to calculate effective curtailment, simply do: |delta_power| - charging_rate and sum all non-zero instances: 
    df['Curtailed Power [MW]'] = np.where(df['Available Power [MW]'] > df['Exported Power [MW]'],
                                 np.where(df['eff_charge_discharge'] > 0, df['Available Power [MW]'] - (df['Exported Power [MW]'] + df['eff_charge_discharge']), 
                                          df['Available Power [MW]'] - df['Exported Power [MW]']), 0)
    
    #%% NPV Calculation
    #Storage CAPEX & OPEX
    Unit_CAPEX_kW  = input_values['Power Unit CAPEX'] # €/kW (Cost of Power)
    Unit_CAPEX_kWh = input_values['Capacity Unit CAPEX'] # €/kWh (Cost of Capacity)
    OPEX_rate = input_values['Annual OPEX Rate']      # % of CAPEX per year
    
    Storage_CAPEX = 1e3* (Unit_CAPEX_kW * power_level + Unit_CAPEX_kWh * (storage_time_hr * power_level))
    Storage_OPEX = Storage_CAPEX * OPEX_rate
    
    Project_Life = int(input_values['Project Life']) #years
    
    discount_rate = input_values['Discount Rate']  # 10% discount rate
    
    storage_total_income = (df['storage_income'].sum() + df['extra_generation_income'].sum())       #Wind + Storage total income
    storage_net_income_ANNUAL = (storage_total_income - df['baseline_income'].sum())/years_covered  #Annualise Income only attrubuted to storgae: [A] + [B] + [C]
    
    cash_flows = [-1*Storage_CAPEX] + [(storage_net_income_ANNUAL - Storage_OPEX)] * Project_Life
    
    #IRR = npf.irr(cash_flows)
    # npf.npv(discount_rate, cash_flows) Python NPV calc starts discounting from Year 0 / Excel NPV discounts from Year 1 <- more accepted method

    IRR = safe_irr(cash_flows)
    # Correct Excel-style NPV calculation (discounting starts from Year 1)
    #NPV = cash_flows[0] + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows[1:], start=1))
    NPV = npf.npv(discount_rate, cash_flows[1:]) + cash_flows[0]
    try:
        result = [
                # --- Energy Potential and Curtailment Breakdown ---
                df['Potential Generation [MW]'].sum() * settlement_period / years_covered,       # [A]: Total potential generation (no generation or transmission constraint)
                df['Generation Constraint [MW]'].sum() * settlement_period / years_covered,      # [B]: Energy lost to generation constraint (Type B curtailment - non-storage mitigable)
                df['Available Power [MW]'].sum() * settlement_period / years_covered,            # [C]: Energy available assuming no transmission constraint (Type A only)
                df['Curtailed Power [MW]'].sum() * settlement_period / years_covered,            # [D]: Energy curtailed due to transmission constraint (Type A, storage-mitigable)
                
                # --- Generation and Export ---
                (df['Exported Power [MW]'].sum() + df['extra_generation'].sum()) * settlement_period / years_covered,  # [E]: Total actual generation (includes extra gen)

                # --- Storage Efficiency and Residual ---
                ((df['Exported Power [MW]'].sum() + df['extra_generation'].sum() - df['Net Exported Power_Storage [MW]'].sum()) * settlement_period - df['end_soc_values'].iloc[-1]) / years_covered, 
                # [G]: Energy lost to conversion inefficiencies over the simulation period, annualized

                df['end_soc_values'].iloc[-1] / years_covered,                                                       # [H]: Final energy in storage, annualized

                df['Net Exported Power_Storage [MW]'].sum() * settlement_period / years_covered,                      # [F]: Energy exported via storage
                # --- Financials ---
                Storage_CAPEX,                                                                                       # [I]: Storage CAPEX
                Storage_OPEX,                                                                                        # [J]: Storage OPEX
                df['baseline_income'].sum() / years_covered,                                                         # [K]: Baseline income (no storage)
                (df['bal_income'].sum() - df['baseline_income'].sum()) / years_covered,                              # [L]: Revenue A - direct balancing market
                (df['storage_income'].sum() - df['bal_income'].sum()) / years_covered,                               # [M]: Revenue B - storage dispatched to balancing
                df['extra_generation_income'].sum() / years_covered,                                                 # [N]: Revenue C - income from extra generation
                storage_total_income / years_covered,                                                                # [O]: Total revenue with storage (baseline + A + B + C)

                # --- Financial Returns ---
                IRR,                                                                                                 # [P]: Internal Rate of Return of storage project
                NPV                                                                                                  # [Q]  NPV of the storage project 
            ]    
    except Exception:
        result = [
                # --- Energy Potential and Curtailment Breakdown ---
                df['Available Power [MW]'].sum() * settlement_period / years_covered,            # [C]: Energy available assuming no transmission constraint (Type A only)
                
                # --- Generation and Export ---
                (df['Exported Power [MW]'].sum() + df['extra_generation'].sum()) * settlement_period / years_covered,  # [E]: Total actual generation (includes extra gen)
                df['Net Exported Power_Storage [MW]'].sum() * settlement_period / years_covered,                      # [F]: Energy exported via storage


                df['Curtailed Power [MW]'].sum() * settlement_period / years_covered,            # [D]: Energy curtailed due to transmission constraint (Type A, storage-mitigable)

                # --- Storage Efficiency and Residual ---
                ((df['Exported Power [MW]'].sum() + df['extra_generation'].sum() - df['Net Exported Power_Storage [MW]'].sum()) * settlement_period - df['end_soc_values'].iloc[-1]) / years_covered, 
                # [G]: Energy lost to conversion inefficiencies over the simulation period, annualized

                df['end_soc_values'].iloc[-1] / years_covered,                                                       # [H]: Final energy in storage, annualized

                # --- Financials ---
                Storage_CAPEX,                                                                                       # [I]: Storage CAPEX
                Storage_OPEX,                                                                                        # [J]: Storage OPEX
                df['baseline_income'].sum() / years_covered,                                                         # [K]: Baseline income (no storage)
                (df['bal_income'].sum() - df['baseline_income'].sum()) / years_covered,                              # [L]: Revenue A - direct balancing market
                (df['storage_income'].sum() - df['bal_income'].sum()) / years_covered,                               # [M]: Revenue B - storage dispatched to balancing
                df['extra_generation_income'].sum() / years_covered,                                                 # [N]: Revenue C - income from extra generation
                storage_total_income / years_covered,                                                                # [O]: Total revenue with storage (baseline + A + B + C)

                # --- Financial Returns ---
                IRR,                                                                                                 # [P]: Internal Rate of Return of storage project
                NPV                                                                                                  # [Q]  NPV of the storage project 
            ]    
    return result  






