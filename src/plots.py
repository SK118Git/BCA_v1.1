# ============================================================================================================================
# plots.py - File containg all functions that do the plotting  
# ============================================================================================================================
# External imports 
import matplotlib.pyplot as plt
import numpy as np 
# ============================================================================================================================

def plot_soc(df, debug_mode, *args):
    """
    Function Purpose: Plots the State-Of-Charge \n
    Inputs: \n
        df = timeseries dataframe \n
        debug_mode = if True adds some extra print statements in the code to help backtracing and debugging \n
        *args = dummy variable that allows the function to recieve extra parameters, enabling compatibility with all other plot functions \n
    Output: None
    """

    # Compute total throughput (sum of absolute energy changes)
    df["energy_change"] = df["end_soc_values"].diff().abs()
    total_throughput = df["energy_change"].sum()

    # Compute nominal battery capacity (max - min energy levels)
    battery_nominal_capacity = df["end_soc_values"].max() - df["end_soc_values"].min()

    # Compute equivalent full cycles
    equivalent_cycles = total_throughput / battery_nominal_capacity

    # Display results
    if debug_mode: print(f"Total Throughput: {total_throughput:.2f} MWh")
    if debug_mode: print(f"Equivalent Full Cycles: {equivalent_cycles:.2f}")

    # Define bin edges (0% to 100% in steps of 5%)
    bins = np.arange(0, 105, 5)

    # Compute histogram data
    hist_values, bin_edges = np.histogram(df["per_state_of_charge"], bins=bins)

    # Convert frequency to percentage of time
    total_points = sum(hist_values)  # Total number of occurrences
    hist_values = (hist_values / total_points) * 100  # Convert to percentage

    # Create labels for bin ranges
    bin_labels = [f"[{int(bin_edges[i])}-{int(bin_edges[i+1])}]" for i in range(len(bin_edges)-1)]

    # Plot horizontal bar chart
    plt.figure(figsize=(8, 6))
    plt.barh(bin_labels, hist_values, color="green", alpha=0.7, edgecolor="black")

    # Formatting with bold labels and Arial font (since Aptos may not be available in Matplotlib)
    plt.xlabel("% of time during the year at that State-of-Charge", fontsize=12, fontweight="bold", fontname="Avenir")
    plt.ylabel("Storage System State-of-Charge [%]", fontsize=12, fontweight="bold", fontname="Avenir")
    plt.title("State of Charge (SOC) Distribution", fontsize=14, fontweight="bold", fontname="Avenir")
    # Set x-axis limits to 0% - 100%
    plt.xlim(0, 100)

    # Format x-axis to show percentages
    plt.xticks(np.arange(0, 110, 10), [f"{int(x)}%" for x in np.arange(0, 110, 10)])

    plt.grid(axis="x", linestyle="--", alpha=0.7)

    # Show plot
    plt.show()
    return 





#_____________________________________________________________________________________________________________________________
def plot_dop(df, debug_mode, power_level, *args):
    """
    Function Purpose: Plots the Distribution of Power \n
    Inputs: \n
        df = timeseries dataframe \n
        debug_mode = if True adds some extra print statements in the code to help backtracing and debugging (although redundant here it allows for compatibility) \n
        power_level = Storage power rating for a given scenario \n 
        *args = dummy variable that allows the function to recieve extra parameters, enabling compatibility with all other plot functions \n
    Outputs: None
    """

    # Assume df['eff_charge_discharge'] exists and contains the power data

    # Drop NaNs

    power_series = df['eff_charge_discharge'].dropna()

    # Define bins (10 MW width from -100 to 100)
    bins = np.arange(-power_level, power_level+1, 1)

    # Histogram with manual normalization
    counts, bin_edges = np.histogram(power_series, bins=bins)
    percentages = counts / counts.sum() * 100

    # Plot
    plt.figure(figsize=(10, 6))
    bars = plt.bar(bin_edges[:-1], percentages, width=1, align='edge', edgecolor='black', alpha=0.7)

    # Add percentage labels on top of bars
    for bar, percentage in zip(bars, percentages):
        if percentage > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)

    # Vertical line at 0 MW
    plt.axvline(0, color='red', linestyle='--', linewidth=1)
    #plt.text(0, plt.ylim()[1]*0.95, '0 MW\n(Neutral)', color='red', ha='left', va='top', fontsize=9)

    # Axis settings

    plt.xlabel('Power level (MW)')
    plt.ylabel('Percentage of occurrences')
    plt.title('Distribution of Charging/Discharging Power')
    plt.grid(True, axis='y')

    plt.tight_layout()
    plt.show()
    return 

