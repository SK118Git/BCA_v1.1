import pandas as pd
import numpy as np
import numpy_financial as npf

from libs.extra import coerce_byte, safe_irr
from modify.bca_class import Business_Case

def bv_method(business_case:Business_Case, scenario_index:int):
    #%% Generate Intra-Day Prices

    # Manipulate Imbalance prices to get an approxiamtion for Intraday prices (from ChatGPT):
    # Using imbalance prices as a proxy for intraday prices is possible, but it comes with significant limitations. 
    # But you can use imbalance prices as a proxy, but you must adjust for volatility, timing, and liquidity differences.
    # Here’s how you can approach it and improve accuracy:
    # Method 4 Incorporate Historical Day-Ahead Prices: If you have day-ahead prices, you can use them as an anchor to estimate intraday spreads.
    # This assumes intraday prices move toward the imbalance price but don’t fully reach it:

    business_case.df['Intra-Day Prices [Euro/MWh]'] = business_case.df["Day-Ahead Prices [Euro/MWh]"] + (business_case.df["Imbalance Prices [Euro/MWh]"] - business_case.df["Day-Ahead Prices [Euro/MWh]"]) * 0.5

    #%% Generate Available Power with storage in place
    # This corresponds to the "Potential Generation" - "Generation Constraint"

    business_case.df['Available Power [MW]'] = business_case.df['Potential Generation [MW]'] - business_case.df['Generation Constraint [MW]']
    business_case.df['Available Power [MW]'] = np.where(business_case.df['Available Power [MW]'] < 0, 0, business_case.df['Available Power [MW]'])

    #%% Compute Transmisstion Capacity
    transformer_rating = 9.5*2 #MW

    #maximum power: "+ df['Available Power [MW]']" is included since the curtailment figures provided by the developer are relative to the Available Power not the transmission capacity: 
    #E.g. Transmission Capacity = 19MW: 
    #Available Power = 10WM
    #Curtailment = 2MW (realtive to Available Power)
    #Effective Transmission Capacity = 19 - ((19 - 10) + 2) = 8MW 
    business_case.df['Available Transmission Capacity [MW]'] = np.where(business_case.df['Capacity Constraint [MW]'] == 0,  transformer_rating,
                                                business_case.df['Actual Generation [MW]']) #effective transmission power rating

    business_case.df['Available Transmission Capacity [MW]'] = np.where (business_case.df['Available Transmission Capacity [MW]'] < 0, 0, business_case.df['Available Transmission Capacity [MW]'])

    #%% Calculate number of years covered by the timeseries dataset (for annualising results where needed)

    # Convert "Date" column to datetime format
    business_case.df["Date"] = pd.to_datetime(business_case.df["Date"], format="%d/%m/%Y")

    # Compute total days covered
    days_covered = (business_case.df["Date"].max() - business_case.df["Date"].min()).days

    # Convert to years
    years_covered = days_covered / 365.25  # Using 365.25 to account for leap years

    #%% Run Parametric Analysis

    #Run only a specific analysis 
    # Function to find index of a specific scenario label
    #____
    # #Specify single Scenario
    # scenario_label = "B7"
    # index_result = find_scenario_index(param_df, scenario_label)
    # for i in range(index_result, index_result + 1):  # Ensures it runs only for index_result
    #____
    ##Run Full Analysis
    #____
    ppa_price = business_case.param_df.loc[scenario_index, 'PPA Price']
    bal_per = business_case.param_df.loc[scenario_index, 'Balancing Market Participation']
    price_type = business_case.param_df.loc[scenario_index, 'Market Type']
    power_level = business_case.param_df.loc[scenario_index, 'Storage Power Rating']
    business_case.power_level = coerce_byte(power_level, [int, float])
    storage_time_hr = business_case.param_df.loc[scenario_index, 'Duration']
            
    result = run_bus_case(business_case, ppa_price, bal_per, price_type, power_level, storage_time_hr, years_covered)

    business_case.param_df.iloc[scenario_index, 7:24] = result # type: ignore

    return 



def run_bus_case(business_case:Business_Case, ppa_price, bal_per, price_type, power_level, storage_time_hr, years_covered):
    global cash_flows
    df = business_case.df

    #% INPUT VALUES
    #settlement period as a fraction of an hour: 15 min = 0.25
    settlement_period = business_case.input_values['Settlement Period'] /60 

    # Determine which Energy Prices to Use (based on "Market Type Parameter")
    
    # Mapping logic
    if price_type == "IMB":
        business_case.df["Balancing Prices"] = business_case.df['Imbalance Prices [Euro/MWh]']
    elif price_type == "INTRA":
        business_case.df["Balancing Prices"] = business_case.df['Intra-Day Prices [Euro/MWh]']
    else:
        raise ValueError("Invalid price type. Use 'IMB' or 'INTRA'.")
    
    #efficiency charging and discharging: square root of the RTE
    efficiency = business_case.input_values['Storage RTE'] ** 0.5

    #power price
    # discount_on_wholesale = input_values['Discount on Day-Ahead'].iloc[-1]  #Wholesale_Price Calculation below
    green_certificate =business_case. input_values['Green-Certificate Price'] #€/MWh renewable energy producers receive these in proportion to their production, and offshore wind projects benefit by law from a guaranteed 4 June 2014 purchase of these "green certificates" by Elia, the Belgian grid operator, at a fixed price of 107 EUR/MWh for 20 years.
    
    # Storage capacity 
    capacity = power_level * storage_time_hr

    # #Adjust Solar Power based on Scenario (Default Data is for 15 MWp)
    # df['Available Power [MW]'] = df['Belwind (181MW)'] + ((solar_MWp/15) * df['OOE Production (15MWp) [MW]'])
        
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
    df['Wholesale_Price'] = ppa_price; #df['Day Ahead Price [Euro/MWh]']*(1-discount_on_wholesale) 

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
    Unit_CAPEX_kW  = business_case.input_values['Power Unit CAPEX'] # €/kW (Cost of Power)
    Unit_CAPEX_kWh = business_case.input_values['Capacity Unit CAPEX']  # €/kWh (Cost of Capacity)
    OPEX_rate = business_case.input_values['Annual OPEX Rate']      # % of CAPEX per year
    
    Storage_CAPEX = 1e3* (Unit_CAPEX_kW * power_level + Unit_CAPEX_kWh * (storage_time_hr * power_level))
    Storage_OPEX = Storage_CAPEX * OPEX_rate
    
    Project_Life = int(business_case.input_values['Project Life']) #years
    
    discount_rate = business_case.input_values['Discount Rate']  # 10% discount rate
    
    storage_total_income = (df['storage_income'].sum() + df['extra_generation_income'].sum())       #Wind + Storage total income
    storage_net_income_ANNUAL = (storage_total_income - df['baseline_income'].sum())/years_covered #Annualise Income only attrubuted to storgae: [A] + [B] + [C]
    
    cash_flows = [-1*Storage_CAPEX] + [(storage_net_income_ANNUAL - Storage_OPEX)] * Project_Life
    
    #IRR = npf.irr(cash_flows)
    # npf.npv(discount_rate, cash_flows) Python NPV calc starts discounting from Year 0 / Excel NPV discounts from Year 1 <- more accepted method
    
   

    irr = safe_irr(cash_flows)
    # Correct Excel-style NPV calculation (discounting starts from Year 1)
    #NPV = cash_flows[0] + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows[1:], start=1))
    npv = npf.npv(discount_rate, cash_flows[1:]) + cash_flows[0]
    result = [
        df['Potential Generation [MW]'].sum()*settlement_period/years_covered,       #[A]: Total Energy that could be generated assuming no generation constraint (Type B)
        df['Generation Constraint [MW]'].sum()*settlement_period/years_covered,      #[B]: Total Energy Lost to Type B Curtailment (cannot be mitigate by storage)
        df['Available Power [MW]'].sum()*settlement_period/years_covered,            #[C]: Total Energy that could be produced assuming no transmission constraint (Type A)
        df['Curtailed Power [MW]'].sum()*settlement_period/years_covered,                                       #[D]: Total Energy Lost to Type A Curtailment (mitigated by storage, when capacity is available)
        (df['Exported Power [MW]'].sum() + df['extra_generation'].sum())*settlement_period/years_covered,       #[E]: Total Energy Generated
        
        ((df['Exported Power [MW]'].sum() + df['extra_generation'].sum() - df['Net Exported Power_Storage [MW]'].sum())*settlement_period - df['end_soc_values'].iloc[-1])/years_covered, 
                                                                                    #[F]: Energy lost to conversion inefficiency accross the simulation period, annnualised. Calculated as the difference between what is generated and exported minus anything still in storage at the end of the simulation
        df['end_soc_values'].iloc[-1]/years_covered,                                #[G]: Energy Held in storage at the end of the simulation, annualised for year-fraction    
        
        df['Net Exported Power_Storage [MW]'].sum()*settlement_period/years_covered,#[H]: Total Energy Exported with Storage
        
        Storage_CAPEX,                                                          #Storage CAPEX
        Storage_OPEX,                                                           #Storage OPEX
        df['baseline_income'].sum()/years_covered,                              #Baseline Revenue
        (df['bal_income'].sum() - df['baseline_income'].sum())/years_covered,   #Revenue (A) - Direct Balancing Market 
        (df['storage_income'].sum() - df['bal_income'].sum())/years_covered,    #Revenue (B) - Stored Energy to Balancing Market
        df['extra_generation_income'].sum()/years_covered,                      #Revenue (C) - Extra Generation-Based Income
        storage_total_income/years_covered,                                     #New Wind Farm Revenue with Storage [Nominal + A+B+C]
        irr,                                                                    #Storage Project IRR
        npv                                                                     #Storage Project NPV
        ]     
        
    return result 