# Instructions

## Prep Work:

Make sure that your excel sheets are correctly labeled (the code will crash if there are spelling mistakes)

Make sure that your Timeseries sheet and Parametric Analysis sheets have the same columns as the **IMV Gamma Case**, *or* **Borssele V** *or* **Parkwind Bus Case**. If not, modify the code accordingly. 

If any modifications are made, **tests\.py** file allows you to directly input saved values to the code base without using the GUI (allowing for tests to go much faster)


## Launching the app:

### 1. Through Python

Check the **requirements.txt** file for information on the packages needed to run the code
This code was only tested for Python **v3.13.3** 

To launch the app through python, simply run the **main\.py** file.

Make sure to consult the **Options** menu if you want to enable plots, or have the file be directly saved to a formatted excel sheet of your chosing 


### 2. Executable format


#### On Windows:

Run the **build.bat** file 
The executable should appear in the **dist/** folder

#### On Linux/Mac:

Run the following command in a terminal opened in this folder (or use **cd** to get to this folder):

```sh 
make build
```

The executable should appear in the **dist/** folder


#### On All Platforms:

Warning! 
You must have **tomli** *or* **tomllib** *and* **pyinstaller** both installed.

Run the following command in a terminal opened in this folder (or use **cd** to get to this folder):

```python
python build.py
```

The executable should appear in the **dist/** folder

## Explaining the source code: 

| File Name |  Purpose | 
| -------------- | ----------------------------------------------------- |
| gui\.py    |  The core functionality related to the user interface  (There shoud be no need to modify this) |
| extra\.py  | A collection of useful functions (Feel free to add functions here if needed)               | 
| bca\.py | The core functionality related to the BC, the code was refactored to conserve Daniel's methodology, no changes should be needed.|
| plots\.py | The functions defining the different plots offered to the user. Make sure for every plot defined in here, it is noted in **AVAILABLE_PLOTS** in the tomodify file. | 
| tests\.py | This file allows for testing the functionality defined for the BCA without having to go through the GUI by simply modifying the relevant entries. | 
| tomodify\.py| This is the file that stores everything that can be (almost) freely modified to suit the BC. This entire code base is built around allowing BCs to be freely done by simply entering the relevant inputs in the GUI, or modifying this file if necessary. In particular, the core difference between the three prior BCs (and potentially all BCs) is the method of calculating **Available Power** (*ap*) and the **Available Transmission Capacity** (*atc*) |

## Modifying the code to suit the BC:

As was stated above, please try as much as possible to limit changes to the **tomodify\.py**.  

You can freely:
+ Modify the GUI configuration settings
+ Add plots by adding the name of the plot to the list of **AVAILABLE PLOTS** and then adding the function execution to the run_analysis() functions conditioned by an if statement (you just need to follow the same method as was doen for the first two plots)
+ Modify the zoning and colors for the excel formatting 
+ Add input entries to the list. If any of the entries you added are string based entries, add it to the relevant list. 
+ Modify the method fo calculating the **AVAILABLE POWER** and **AVAILABLE TRANSMISSION CAPACITY** for a new BC. Then you must add the name of the new BC method to the relavant list, add relavant if statements to the BCA code so that your new BC logic is applied when **case_type** and **method** have the correct value. (HINT: case type ranges from 0 to 2 and depends on the order of the case types in the list defined in **tomodify\.py** and the method number corresponds to the order of definition of the different methods in the list starting at 0.) 


