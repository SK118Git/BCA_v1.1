
# Table of Contents:
- [Table of Contents:](#table-of-contents)
- [I. Prep Work:](#i-prep-work)
  - [A. In the *Timeseries Sheet*](#a-in-the-timeseries-sheet)
    - [IMV Gamma Method:](#imv-gamma-method)
    - [Borselle V Method](#borselle-v-method)
    - [Parkwind Method:](#parkwind-method)
  - [B. In the *Parametric Analysis* sheet:](#b-in-the-parametric-analysis-sheet)
    - [Parameters:](#parameters)
    - [Output 1 (All other methods):](#output-1-all-other-methods)
    - [Output 2 (Borselle V Method):](#output-2-borselle-v-method)
- [II. Launching the app:](#ii-launching-the-app)
  - [A. Through Python](#a-through-python)
  - [B. Executable format](#b-executable-format)
    - [On Windows:](#on-windows)
    - [On Linux/Mac:](#on-linuxmac)
    - [On All Platforms:](#on-all-platforms)
- [III. Explaining the source code:](#iii-explaining-the-source-code)
  - [A. File Structure:](#a-file-structure)
  - [B. The Business Case Logic:](#b-the-business-case-logic)
- [IV. Modifying the code to suit the BC:](#iv-modifying-the-code-to-suit-the-bc)

# I. Prep Work:

Make sure that your excel sheets are correctly labeled (the code will crash if there are spelling mistakes)

Make sure that your Timeseries sheet and Parametric Analysis sheets have the same columns as the **IMV Gamma Case**, *or* **Borssele V** *or* **Parkwind Bus Case**. If not, modify the code accordingly. 

Below you will find a list of all columns that are needed/can be put (I will anotate with **OPT** the one that you should only put if you are doing a mixed solar/wind case). The column order is crucial for everything after duration (including duration itself). The method employed for the Borssele V BC has unique columns and the code is written to accomodate for that.

## A. In the *Timeseries Sheet*

### IMV Gamma Method:
+ Date	
+ Time	
+ Day-Ahead Prices [Euro/MWh]	
+ Imbalance Prices [Euro/MWh]	
+ Wind Speed [m/s]	
+ Capacity Constraint [MW]

### Borselle V Method
+ Date	
+ Time	
+ Wind Speed [m/s]	
+ Potential Generation [MW]	
+ Actual Generation [MW]	
+ Delta [MW]	
+ (Type A) PPA [MW]	
+ (Type B) Maintenance [MW]	
+ (Type B) Environmental [MW]	
+ (Type A) Utility [MW]	
+ (Type B) Owner Stops [MW]	
+ Capacity Constraint [MW]	
+ Generation Constraint [MW]	
+ Day-Ahead Prices [Euro/MWh]	
+ Imbalance Prices [Euro/MWh]


### Parkwind Method:
+ Starting Time	
+ Day-Ahead Prices [Euro/MWh]	
+ Imbalance Prices [Euro/MWh]	
+ Belwind (181MW)	
+ OOE Production (15MWp) [MW]	
+ Capacity Constraint [MW]

## B. In the *Parametric Analysis* sheet:
### Parameters:
+ Scenario
+ PPA Price 
+ Market Type 
+ Wind Power (MW)
+ Solar Installed (MWp) (**OPT**)
+ Balancing Market Participation 
+ Storage Power Rating 
+ Duration 
  
### Output 1 (All other methods):
+ Annual Energy Potential	
+ Annual Energy Generated	
+ Annual Energy Exported	
+ Annual Enery Curtailed	
+ Lost to Storage Inefficiency	
+ Still In Storage	
+ Storage CAPEX	
+ Storage OPEX	
+ Baseline Revenue	
+ Revenue Direct Production to Balancing Market [A]
+ Revenue Stored Energy to Balancing Market [B]
+ Revenue Extra Generation-Based Income [C]
+ Revenue with Storage Baseline = [A] + [B] + [C]
+ IRR	
+ NPV

### Output 2 (Borselle V Method):
+ Annual Yield Potential [A]
+ Type B Curtailment [B]	
+ Annual Generation Potential [C] = [A] - [B]	
+ Type A Curtailment [D]	
+ Annual Energy Generated [E] = [C] - [D]	
+ Lost to Storage Inefficiency [F]	
+ Still In Storage [G]	
+ Annual Energy Exported [H] = [E] - [F] - [G]
+ Storage CAPEX	
+ Storage OPEX	
+ Baseline Revenue	
+ Revenue Direct Production to Balancing Market [A]
+ Revenue Stored Energy to Balancing Market [B]
+ Revenue Extra Generation-Based Income [C]
+ Revenue with Storage Baseline = [A] + [B] + [C]
+ IRR	
+ NPV



# II. Launching the app:

## A. Through Python

Check the [requirements.txt](requirements.txt) file for information on the packages needed to run the code
This code was last tested for Python **v3.13.4** and requires a version above **v3.10**

To launch the app through python, simply run the [main.py](main.py) file.

Make sure to consult the **Options** menu if you want to enable plots, or have the file be directly saved to a formatted excel sheet of your chosing 


## B. Executable format


### On Windows:

Run the **build.bat** file 
The executable should appear in the **dist/** folder

### On Linux/Mac:

Run the following command in a terminal opened in this folder (or use **cd** to get to this folder):

```bash 
make build
```

The executable should appear in the **dist/** folder


### On All Platforms:

Warning! 
You must have **tomli** *or* **tomllib** *and* **pyinstaller** both installed.

Run the following command in a terminal opened in this folder (or use **cd** to get to this folder):

```python
python build.py
```

The executable should appear in the **dist/** folder

# III. Explaining the source code: 

## A. File Structure:

| File Name |  Purpose | 
| -------------- | ----------------------------------------------------- |
| [bca.py](bca.py) | The core functionality related to the BC, the code was refactored to conserve Daniel's methodology, no changes should be needed.|
| [excel.py](excel.py) | Contains all functionality which directly interacts and modifies the excel file. |
| [extra.py](extra.py)  | A collection of useful functions (Feel free to add functions here if needed).              | 
| [frontend.py](frontend.py)    |  The core functionality related to the user interface  (There shoud be no need to modify this). |
| [modifiable.py](modifiable.py) | This is the file that stores everything that can be (almost) freely modified to suit the BC. This entire code base is built around allowing BCs to be freely done by simply entering the relevant inputs in the GUI, or modifying this file if necessary. In particular, the core difference between the three prior BCs (and potentially all BCs) is the method of calculating **Available Power** (*ap*) and the **Available Transmission Capacity** (*atc*). |
| [plots.py](plots.py) | The functions defining the different plots offered to the user. Make sure for every plot defined in here, it is noted in **AVAILABLE_PLOTS** in the tomodify file with name and a reference to the function (see prior examples). | 
| [popup.py](popup.py) | A file which contains the code for the progress bar which appears as a popup. It was put into its own file because otherwise I ran into import loops.  | 
| [tests.py](tests.py) | This file allows for testing the functionality defined for the BCA without having to go through the GUI by simply modifying the relevant entries. | 

## B. The Business Case Logic:

See the [relevant file](BCA_EXPLANATION.md)

# IV. Modifying the code to suit the BC:

As was stated above, please try as much as possible to limit changes to the [modifiable.py](modifiable.py).  

You can freely:
+ Modify the GUI configuration settings
+ Add plots by adding the name of the plot to the list of **AVAILABLE PLOTS** and and a reference to its function
+ Modify the zoning and colors for the excel formatting 
+ Add input entries to the list. If any of the entries you added are string based entries, add it to the relevant list. 
+ Modify the method fo calculating the **AVAILABLE POWER** and **AVAILABLE TRANSMISSION CAPACITY** for a new BC. Then you must add the name of the new BC method to the relavant list, add relevant if statements to the BCA code so that your new BC logic is applied when **case_type** and **method** have the correct value. (HINT: case type ranges from 0 to 2 and depends on the order of the case types in the list defined in **tomodify\.py** and the method number corresponds to the order of definition of the different methods in the list starting at 0.) 


