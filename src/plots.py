# ============================================================================================================================
# plots.py - File containg all functions that do the plotting  
# ============================================================================================================================
# External imports 
import os
import numpy as np 
import matplotlib.pyplot as plt
import tkinter as tk
import plotly.graph_objects as go
import plotly.io as pio
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
from datetime import datetime

# ============================================================================================================================
# Internal imports
from extra import log_print




def plot_soc(df:DataFrame, scenario_name:str, debug_mode:bool, *args) -> None:
    """
    Function Purpose: Show the SOC plot in a new popup window.
    Inputs:
        df = timeseries dataframe
        scenario_name = the name of the current scenario
        debug_mode = if True adds debug log statements
    Outputs: None
    """
    log_print("Entered plot for soc for scenario {scenario_name}.")

    # Compute metrics
    df["energy_change"] = df["end_soc_values"].diff().abs()
    total_throughput = df["energy_change"].sum()
    battery_nominal_capacity = df["end_soc_values"].max() - df["end_soc_values"].min()
    equivalent_cycles = total_throughput / battery_nominal_capacity

    if debug_mode: log_print(f"Total Throughput: {total_throughput:.2f} MWh.")
    if debug_mode: log_print(f"Equivalent Full Cycles: {equivalent_cycles:.2f}.")

    # Histogram setup
    bins = np.arange(0, 105, 5)
    hist_values, bin_edges = np.histogram(df["per_state_of_charge"], bins=bins)
    total_points = sum(hist_values)
    hist_values = (hist_values / total_points) * 100
    bin_labels = [f"[{int(bin_edges[i])}-{int(bin_edges[i+1])}]" for i in range(len(bin_edges)-1)]

    # Create popup window
    popup = tk.Toplevel()
    popup.title(f"Scenario {scenario_name}: State of Charge (SOC) Distribution")
    popup.geometry("1400x900")

    # Create Figure and Axes
    fig = Figure(figsize=(8, 6))
    ax = fig.add_subplot(111)
    ax.barh(bin_labels, hist_values, color="green", alpha=0.7, edgecolor="black")
    ax.set_xlabel("% of time during the year at that State-of-Charge", fontsize=10, fontweight="bold", fontname="Arial")
    ax.set_ylabel("Storage System State-of-Charge [%]", fontsize=10, fontweight="bold", fontname="Arial")
    ax.set_title("State of Charge (SOC) Distribution", fontsize=12, fontweight="bold", fontname="Arial")
    ax.set_xlim(0, 100)
    ax.set_xticks(np.arange(0, 110, 10))
    ax.set_xticklabels([f"{int(x)}%" for x in np.arange(0, 110, 10)])
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Embed in popup
    canvas = FigureCanvasTkAgg(fig, master=popup)
    canvas.draw()
    canvas.get_tk_widget().pack(fill='both', expand=True)

    log_print(f"SOC plot displayed in popup for scenario {scenario_name}.")
    save_figure(fig, "soc", scenario_name)
    log_print(f"SOC plot saved for scenario {scenario_name}.")
    return


#_____________________________________________________________________________________________________________________________
def plot_dop(df:DataFrame, scenario_name:str, debug_mode:bool, power_level:int|float, *args):
    """
    Function Purpose: Show the SOC plot in a new popup window.
    Inputs:
        df = timeseries dataframe
        scenario_name = the name of the current scenario
        debug_mode = if True adds debug log statements
    Outputs: None
    """

    log_print(f"Entered plot of dop for scenario {scenario_name}")

    # Drop NaNs
    power_series = df['eff_charge_discharge'].dropna()

    # Define bins (1 MW width from -power_level to +power_level)
    bins = np.arange(-power_level, power_level + 1, 1)

    # Histogram with manual normalization
    counts, bin_edges = np.histogram(power_series, bins=bins)
    percentages = counts / counts.sum() * 100

    # Create a new popup Tkinter window
    popup = tk.Toplevel()
    popup.title(f"Scenario {scenario_name}: Distribution of Charging/Discharging Power")
    popup.geometry("1400x900")

    # Create a Figure object
    fig = Figure(figsize=(10, 6), dpi=100)
    ax = fig.add_subplot(111)

    # Plot on the Figure
    bars = ax.bar(bin_edges[:-1], percentages, width=1, align='edge', edgecolor='black', alpha=0.7)

    for bar, percentage in zip(bars, percentages):
        if percentage > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)

    ax.axvline(0, color='red', linestyle='--', linewidth=1)
    ax.set_xlabel('Power level (MW)', fontsize=10, fontweight="bold", fontname="Arial")
    ax.set_ylabel('Percentage of occurrences', fontsize=10, fontweight="bold", fontname="Arial")
    ax.set_title('Distribution of Charging/Discharging Power', fontsize=12, fontweight="bold", fontname="Arial")
    ax.grid(True, axis='y')

    fig.tight_layout()

    # Embed the figure in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=popup)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    log_print(f"DOP plot displayed in popup for scenario {scenario_name}.")
    save_figure(fig, "dop", scenario_name)
    log_print(f"DOP plot saved for scenario {scenario_name}.")

    return


def save_figure(fig:Figure, plot_type:str, scenario_name:str) -> None:
    # Create a directory in the user's Documents folder
    documents_dir = os.path.join(os.path.expanduser("~"), "Documents")
    output_dir = os.path.join(documents_dir, "BCA_Plots")  # Change name as needed
    os.makedirs(output_dir, exist_ok=True)


    # Format timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Construct full path
    filename = f"{plot_type}_{scenario_name}_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    # Save figure
    fig.savefig(filepath, dpi=300, bbox_inches="tight") 
    return 



def plot_sankee(
        wind_to_total_aep:int|float,
        solar_to_total_aep:int|float,
        total_aep_to_curtailed:int|float,
        total_aep_to_generated:int|float,
        generated_to_exported:int|float,
        generated_to_lost:int|float,
        generated_to_stored:int|float
        ): 
    # Ensure the figure opens in the browser in Spyder
    pio.renderers.default = "browser"

    # Define labels for each stage in the energy flow
    base_labels = [
        "Annual Energy Potential - WIND", 
        "Annual Energy Potential - SOLAR", 
        "Annual Energy Potential - Total", 
        "Curtailed Energy", 
        "Annual Energy Generated", 
        "Annual Energy Exported", 
        "Lost to Storage Inefficiency", 
        "Still In Storage at End of Year"
    ]


    # Define source and target indices based on the flow
    # Define the source and target node indices
    sources = [
        0,  # AEP-Wind -> AEP - Total
        1,  # AEP-Solar -> AEP - Total
        2,  # AEP - Total -> Energy Curtailed
        2,  # AEP - Total -> Energy Generated
        4,  # Energy Generated -> Energy Exported
        4,  # Energy Generated -> Energy Lost
        4   # Energy Generated -> Energy Stored
    ]

    targets = [
        2,  # AEP-Wind -> AEP - Total
        2,  # AEP-Solar -> AEP - Total
        3,  # AEP - Total -> Energy Curtailed
        4,  # AEP - Total -> Energy Generated
        5,  # Energy Generated -> Energy Exported
        6,  # Energy Generated -> Energy Lost
        7   # Energy Generated -> Energy Stored
    ]

    values = [
        wind_to_total_aep,
        solar_to_total_aep,
        total_aep_to_curtailed,
        total_aep_to_generated,
        generated_to_exported,
        generated_to_lost,
        generated_to_stored 
    ]

    # Define link colors (light blue)
    # Define distinct link colors
    node_colors = ["lightblue", "orange", "pink", "red", "lightgreen", "green", "purple"]
    link_colors = ["lightblue", "orange", "red", "pink", "lightgreen", "purple"]

    # Calculate the divisor (sum of the first two values)
    divisor = values[0] + values[1]

    # Calculate the percentages
    #percentages = [(value / divisor) * 100 for value in values]

    percentages = [values[0]/divisor*100, 
                values[1]/divisor*100,
                divisor/divisor*100,
                values[2]/divisor*100,
                values[3]/divisor*100,
                values[4]/divisor*100,
                values[5]/divisor*100,
                values[6]/divisor*100]

    # Generate labels dynamically with values
    labels = [f"{label}: {value:.2f}%" for label, value in zip(base_labels, percentages)]


    # Define node positions
    x_positions = [0.0, 0.0,  0.3, 0.35, 0.6,  1.0, 1.0]  # Adjust x-coordinates
    y_positions = [0.5, 0.4, 0.5, 0.95, 0.45, 0.4, 1.0]  # Adjust y-coordinates (Curtailed Energy lower)

    # Create the Sankey diagram
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            #label = base_labels,
            label=labels,
            color = node_colors,  # Change node color to light blue
            x=x_positions,
            y=y_positions
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color = link_colors  # Apply distinct colors to links
        )
    ))

    # Update layout and show the figure
    fig.update_layout(
        title_text="Energy Flow Sankey Diagram: Belwind [181.5MW] + OOE [15MWp] + FLASC [10MW / 4hr]", 
        #title_text="Energy Flow Sankey Diagram: IMV-G NO STORAGE", 
        font=dict(size=14, color="black"),  # Make fonts bigger and text black
    )

    fig.show()
    return 