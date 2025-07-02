import pandas as pd
import numpy as np
import numpy_financial as npf

from libs.extra import coerce_byte, safe_irr
from libs.logger import log_print


def parkwind_method(business_case, scenario_index, debug_mode:bool):
    ppa_price = business_case.param_df.loc[scenario_index, "PPA Price"]
    solar_MWp = business_case.param_df.loc[scenario_index, "Solar Installed (MWp)"]
    bal_per = business_case.param_df.loc[
        scenario_index, "Balancing Market Participation"
    ]
    power_level = business_case.param_df.loc[scenario_index, "Storage Power Rating"]
    business_case.power_level = coerce_byte(power_level, [int, float])
    storage_time_hr = business_case.param_df.loc[scenario_index, "Duration"]

    try:
        price_type = business_case.param_df.loc[scenario_index, "Market Type"]
        price_type = coerce_byte(price_type, [str])
    except Exception:
        log_print(f"An error has occured with price_type assignment: {Exception}")
        price_type = ""

    result = run_bus_case(
        business_case,
        ppa_price,
        solar_MWp,
        bal_per,
        power_level,
        storage_time_hr,
        price_type,
    )

    business_case.param_df.iloc[scenario_index, 7:18] = result
    return


def run_bus_case(
    business_case,
    ppa_price,
    solar_MWp,
    bal_per,
    power_level,
    storage_time_hr,
    price_type,
):
    global cash_flows
    df = business_case.df

    df["Balancing Prices [Euro/MWh]"] = (
        df["Day-Ahead Prices [Euro/MWh]"]
        + (df["Imbalance Prices [Euro/MWh]"] - df["Day-Ahead Prices [Euro/MWh]"]) * 0.5
    )

    # Parkwind + Solar (OOE)
    # Offhore wind + solar exporting to a fixed transmission contraint
    # Balancing market participation as per defined percentage
    # Can charge from the grid

    # 16 02 2025 version assumes fixed wholesale price
    # 24 02 2025 version takes day-ahead price from Excel
    # Also imports and exports values directly from/to Excel
    # Read and import the data from excel file including headers

    # % INPUT VALUES
    # settlement period as a fraction of an hour: 15 min = 0.25
    settlement_period = business_case.input_values["Settlement Period"] / 60

    # Power level storage system [MW]
    # power_level = input_values['Storage Power Rating'].iloc[-1]

    # storage time
    # storage_time = input_values['Storage Duration'].iloc[-1] #hrs

    # Balancing power level [percentage]
    # bal_per = input_values['Balancing Market Participation'].iloc[-1]

    # efficiency charging and discharging: square root of the RTE
    efficiency = business_case.input_values["Storage RTE"] ** 0.5

    # power price
    # discount_on_wholesale = business_case.input_values['Discount on Day-Ahead'].iloc[-1]  #Wholesale_Price Calculation below
    green_certificate = business_case.input_values[
        "Green-Certificate Price"
    ]  # €/MWh renewable energy producers receive these in proportion to their production, and offshore wind projects benefit by law from a guaranteed 4 June 2014 purchase of these "green certificates" by Elia, the Belgian grid operator, at a fixed price of 107 EUR/MWh for 20 years.

    # maximum power
    maxpower = business_case.input_values[
        "Export Transmission Capacity"
    ]  # transmission power rating

    # %

    # Storage capacity (corrected for settlement period)
    storage_time = (
        1 / settlement_period
    ) * storage_time_hr  # (corrected for settlment period)
    capacity = power_level * storage_time

    # Adjust Solar Power based on Scenario (Default Data is for 15 MWp)
    df["Available Power [MW]"] = df["Belwind (181MW)"] + (
        (solar_MWp / 15) * df["OOE Production (15MWp) [MW]"]
    )

    # Limit Exported Power to the Tranmission Capacity:
    df["Exported Power [MW]"] = np.where(
        df["Available Power [MW]"] > maxpower, maxpower, df["Available Power [MW]"]
    )
    # for hybrid projects: (Wind+Solar), available Power [MW] already accounts for combined energy sources

    # deltapower: delta between available power and transmission capacity, -ve values correspond to overproduction wrt to max power
    df["deltapower"] = maxpower - df["Available Power [MW]"]
    # deltapower > 0: underproduction relative to max power constraint
    # deltapower < 0: overproduction relative to max power constraint

    # Balancing power [MW]
    df["bal_power"] = (
        bal_per / 100 * df["Available Power [MW]"]
    )  # amount of power to be allocated to balancing market as % of available power

    # From Jochem: the sale of electricity on the wholesale market, which is done through the long term power purchase agreement with Electrabel.
    # The power is sold at prevailing market prices (using a widely traded index), minus a discount paid to Electrabel to remunerate the services the company provides
    # (grid compliance, administrative services, and the guarantee that the whole production will be sold at all times)

    # Updated description from Jochem: sold at a fixed price
    # PPA_price = input_values['PPA Price'].iloc[-1]
    df["Wholesale_Price"] = ppa_price
    # df['Day Ahead Price [Euro/MWh]']*(1-discount_on_wholesale)

    # %

    ## Charging and Discharging Strategy

    # CHARGING
    # theor_charging: Power being pulled from the grid [MW]:
    # when there is overproduction relative to transmission (deltapower < 0): the maximum charging is the overproduced power
    # when there is underproduction (deltapower ≥ 0):
    # if balancing prices are -ve: Charage at max power
    # if balancing prices are +ve: do nothing
    df["theor_charging"] = np.where(
        df["deltapower"] < 0,
        -df["deltapower"],
        np.where((df["Balancing Prices"] < 0), power_level, 0),
    )

    # df['charging'] = np.where (df['theor_charging'] >= power_level , power_level , df['theor_charging'])

    # efficiency charging: actual energy going into the system after conversion losses
    df["eff_charging"] = df["theor_charging"] * efficiency

    # DISCHARGING
    # theor_discharging: discharge at full rated output of the storage system
    # when there is overproduction relative to transmission constraint (deltapower < 0): do nothing
    # when there is underproduction (deltapower ≥ 0):
    # if balancing prices are MORE than 30% the day-ahead or fixed price (e.g. PPA): Discharge at max power
    # if balancing prices are LESS than 30% the day-ahead or fixed price (e.g. PPA): do nothing
    df["theor_discharging"] = np.where(
        df["deltapower"] < 0,
        0,
        np.where(
            df["Balancing Prices [Euro/MWh]"] > (1.3 * df["Wholesale_Price"]),
            -power_level,
            0,
        ),
    )

    # Maximum charging or discharging power
    # Add a column to the DF with the Max Charging/Discharging profile: where Charging is zero, put the theoretical discharge output, where it is not zero, leave as is
    # Used for calculating the end_soc_values
    df["maximum_charge_discharge"] = np.where(
        df["eff_charging"] == 0, df["theor_discharging"], df["eff_charging"]
    )

    ## State of Charge Calculations

    # soc_values will eventually contain all the end_soc values. Foregoing initial_soc.
    soc_values = [0]

    # soc_diffs is a combination of actual_charge and actual_discharge, with charge values being positive and discharge values being negative
    soc_diffs = []
    max_charge_or_discharge_np = df["maximum_charge_discharge"].to_numpy()

    # define functions
    for i in range(len(df)):
        last_soc_val = soc_values[-1]
        soc_val = np.clip(
            last_soc_val + max_charge_or_discharge_np[i], a_min=0, a_max=capacity
        )

        soc_diffs.append(soc_val - last_soc_val)
        soc_values.append(soc_val)

    # create the cumulitive state of charge dataframe
    df["end_soc_values"] = soc_values[1:]

    # create the charging/discharging parameter
    #'charge_discharge': energy in (>0) and out (<0) of the system
    df["charge_discharge"] = df["end_soc_values"] - df["end_soc_values"].shift(+1)

    # remove the nan from the first line
    df["charge_discharge"] = df["charge_discharge"].replace(np.nan, 0)

    # define discharge efficiency
    #'eff_charge_discharge': energy in (>0) and out (<0) out at storage-grid connection point (used for revenue calculation)
    df["eff_charge_discharge"] = np.where(
        df["charge_discharge"] >= 0,
        df["charge_discharge"] / efficiency,
        df["charge_discharge"] * efficiency,
    )

    # create the percentage state of charge
    df["per_state_of_charge"] = (df["end_soc_values"] * 100) / capacity

    ## Revenue Calculations

    # Theoretical Windfarm revenue
    # Standard wind farm income based on Exported Power (as imported from Excel)
    df["baseline_income"] = (
        (df["Wholesale_Price"] + green_certificate) * df["Exported Power [MW]"]
    ) * settlement_period

    # Total income when considering balancing market participation (no storage): directly exporting portion of energy to balancing market, e.g 85% wholesale + 15% Balancing Market
    df["bal_income"] = (
        (df["Wholesale_Price"] + green_certificate)
        * (df["Exported Power [MW]"] * (100 - bal_per) / 100)
        * settlement_period
    ) + (
        bal_per
        / 100
        * df["Exported Power [MW]"]
        * (df["Balancing Prices [Euro/MWh]"] + green_certificate)
        * settlement_period
    )

    # Storage Revenue (only attributed directly to storage) SIGN OF BALANCING PRICES: (-ve Balance Price = PAID TO CHARGE)
    # [A]: IDLE (Not Charging or Discharging): assign balancing market income
    # [B]: DISCHARGING: assign balancing market income corrected for what is being delivered by storage system (if balancing prices are +ve then it will increase the income)
    # [C]: CHARGING: If there is Over Production (delta power < 0) (can't discharge): attribute the full balancing market income to storage (based on Exported Power -> so already corrected for transmission constraint)
    # [D]: CHARGING: If Storage Power Rating < Balancing Market Assigned Power (X% of Available Power): All Charging from Balancing Market: assign balancing market income corrected for what is being charged by storage system (if balancing prices are -ve then it will increase the income during charging)
    # [E]: CHARGING: If Storage Power Rating < Exported Power: attribute Charging from Balancing Market (charging here only happens only when Balance Prices are -ve)
    # [F]: CHARGING: Otherwise: Exported < Storage Power Rating: pull down output into negative (charging from grid) (charging here only happens only when Balance Prices are -ve)

    df["storage_income"] = np.where(
        df["eff_charge_discharge"] == 0,
        df["bal_income"],  # [A]
        np.where(
            df["eff_charge_discharge"] < 0,
            df["bal_income"]
            - df["eff_charge_discharge"]
            * df["Balancing Prices [Euro/MWh]"]
            * settlement_period,  # [B]
            np.where(
                df["deltapower"] < 0,
                df["bal_income"],  # [C]
                np.where(
                    power_level <= df["bal_power"],
                    df["bal_income"]
                    - df["eff_charge_discharge"]
                    * df["Balancing Prices [Euro/MWh]"]
                    * settlement_period,  # [D]
                    np.where(
                        power_level <= df["Exported Power [MW]"],
                        df["bal_income"]
                        - df["bal_power"]
                        * df["Balancing Prices [Euro/MWh]"]
                        * settlement_period
                        - (df["eff_charge_discharge"] - df["bal_power"])
                        * (df["Wholesale_Price"] + df["Balancing Prices [Euro/MWh]"])
                        * settlement_period,  # [E]
                        (df["bal_power"] - power_level)
                        * df["Balancing Prices [Euro/MWh]"]
                        * settlement_period,  # [F]
                    ),
                ),
            ),
        ),
    )

    # Extra income from Generation-Based Compenstation: since baseline_income and bal_income are both computed on the basis of EXPORTED output
    # Generation that was above transmission constraint AND stored:
    df["extra_generation"] = np.where(
        df["deltapower"] < 0, df["eff_charge_discharge"], 0
    )
    df["extra_generation_income"] = (
        df["extra_generation"] * green_certificate * settlement_period
    )  # Extra income on green certificates awarded for generation of clean energy

    # %% NPV Calculation
    # Storage CAPEX & OPEX
    Unit_CAPEX_kW = business_case.input_values[
        "Power Unit CAPEX"
    ]  # €/kW (Cost of Power)
    Unit_CAPEX_kWh = business_case.input_values[
        "Capacity Unit CAPEX"
    ]  # €/kWh (Cost of Capacity)
    OPEX_rate = business_case.input_values["Annual OPEX Rate"]  # % of CAPEX per year

    Storage_CAPEX = 1e3 * (
        Unit_CAPEX_kW * power_level + Unit_CAPEX_kWh * (storage_time_hr * power_level)
    )
    Storage_OPEX = Storage_CAPEX * OPEX_rate

    Project_Life = int(business_case.input_values["Project Life"])  # years

    discount_rate = business_case.input_values["Discount Rate"]  # 10% discount rate

    storage_total_income = (
        df["storage_income"].sum() + df["extra_generation_income"].sum()
    )  # Wind + PV + Storage total income
    storage_net_income = (
        storage_total_income - df["baseline_income"].sum()
    )  # Income only attrubuted to storgae: [A] + [B] + [C]

    cash_flows = [-1 * Storage_CAPEX] + [
        storage_net_income - Storage_OPEX
    ] * Project_Life

    irr = safe_irr(cash_flows)
    # npf.npv(discount_rate, cash_flows) Python NPV calc starts discounting from Year 0 / Excel NPV discounts from Year 1 <- more accepted method

    # Correct Excel-style NPV calculation (discounting starts from Year 1)
    # NPV = cash_flows[0] + sum(cf / (1 + discount_rate) ** i for i, cf in enumerate(cash_flows[1:], start=1))
    npv = npf.npv(discount_rate, cash_flows[1:]) + cash_flows[0]
    result = [
        (
            df["extra_generation"].sum() + df["Exported Power [MW]"].sum()
        ),  # G: Annual Energy Generated
        df["Exported Power [MW]"].sum(),  # H: Annual Energy Exported
        Storage_CAPEX,  # I: Storage CAPEX
        Storage_OPEX,  # J: Storage OPEX
        df["baseline_income"].sum(),  # K: Baseline Revenue
        (
            df["bal_income"].sum() - df["baseline_income"].sum()
        ),  # L: Revenue (A) - Direct Balancing Market
        (
            df["storage_income"].sum() - df["bal_income"].sum()
        ),  # M: Revenue (B) - Stored Energy to Balancing Market
        df[
            "extra_generation_income"
        ].sum(),  # N: Revenue (C) - Extra Generation-Based Income
        storage_total_income,  # O: New Wind Farm Revenue with Storage [Nominal + A+B+C]
        irr,  # P: Storage Project IRR
        npv,  # Q: Storage Project NPV
    ]

    return result

