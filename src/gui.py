# ============================================================================================================================
# gui.py - File containg all functions that don't need to be modified, are not used for plotting, nor the GUI, not the BCA 
# ============================================================================================================================
# External library imports 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import Any, cast
# =============================================================================
# Internal library imports 
from tomodfiy import AVAILABLE_PLOTS, INPUT_FIELDS, GUI_CONFIG, STRING_BASED, CHOICE_MATRIX
from extra import update_dict, find_index
from bca import run 
# =============================================================================

class BCA_App:
    def __init__(self, root:tk.Tk) -> None:
        """
        Function purpose: Initializer of the class \n
        Inputs: 
          self = this means that this function defines a method for the class
          root = the name of the root window for the GUI  
        \n
        Outputs: None 
        """
        self.initalize_vars(root)
        self.configure_window()
        self.entries: dict[str, list[ttk.Entry | float | str]] = self.create_entry_widgets()
        self.create_buttons()

    def initalize_vars(self, root:tk.Tk) -> None:
        """
        Function purpose: Initializes all the main variables of the class \n
        Inputs: 
          self = this means that this function defines a method for the class
          root = the name of the root window for the GUI  
        \n
        Outputs: None \n 
        Note: This method was created simply to clean-up the init 
        """
        self.root = root
        self.debug_mode = tk.BooleanVar(value=False) 
        self.paste_to_excel = tk.BooleanVar(value=False)
        self.amount_widgets:int = 0

        self.selected_plots: dict[str, tk.BooleanVar] = {}
        for plot in AVAILABLE_PLOTS:
            var = tk.BooleanVar(value=False)
            self.selected_plots[plot] = var
        
        self.case_type_choice = tk.StringVar()
        self.case_type:int = 0 

        self.method_choice = tk.StringVar()
        self.method:int = 0

        self.excel_output_sheet_name = tk.StringVar()

        self.isOkay = root.register(self.validate_input)
        self.correctInput= root.register(self.erase_input)


        return 

    def configure_window(self) -> None:
        """
        Function purpose: This function manages the settings for the GUI's window \n
        Inputs: 
          self = this means that this function defines a method for the class \n
        Outputs: None 
        """
        self.root.title(str(GUI_CONFIG['window_title']))
        self.root.geometry(str(GUI_CONFIG['window_size']))
        self.root.resizable(False, False)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=1)
        self.root.columnconfigure(3, weight=1)

    # Creating all the entry widgets 
    def create_entry_widgets(self) -> dict[str, list[ttk.Entry | float | str]]:  
        """
        Function purpose: Initializer of the class \n
        Inputs: 
          self = this means that this function defines a method for the class \n
        Outputs: Creates the entries dictionnary which maps to each entry (defined in tomodify.py) the actual ttk.Entry
        """
        entries: dict[str, list[ttk.Entry | float | str]] = {field:[] for field in INPUT_FIELDS}
        i:int=0

        for key in entries:
            entries[key].append(self.create_entry(key,i+1))
            i+=1
        if self.debug_mode.get():
            print(f"Currently in creation of entry dict the created dict is: {entries}")
        return entries  

    def create_entry(self, name:str, position:int) -> ttk.Entry:
        """
        Function purpose: This function manages the creation of each ttk.Entry \n
        Inputs: 
          self = this means that this function defines a method for the class
          name = the name of the entry aka what is written in the label of the entry 
          position = the row this entry should go on
        \n
        Outputs: An entry created using the prior info 
        Note: This function was created as all entries have the same settings so it allows for less repetition in the code
        """
        label = ttk.Label(self.root, text=name + ':')
        entry = ttk.Entry(self.root, validate="key", validatecommand=(self.isOkay, '%W', '%P'), invalidcommand=(self.correctInput, '%W'))

        label.grid(column=1, row=position, padx=10, pady=2, sticky='w')
        entry.grid(column=2, row=position, padx=10, pady=2)

        return entry


    def create_buttons(self) -> None:
        """
        Function purpose: This function creates all the buttons and their respective labels \n
        Inputs: 
          self = this means that this function defines a method for the class \n
        Outputs: None \n
        Note: Specificallty are created label and button for: \n
            - choose file \n
            - case choice \n
            - method choice \n
            - options \n
            - quit \n
            - launch \n
        """

        # File Selection button and show selected file 
        file_button = ttk.Button(self.root, text="Choose File", command=self.choose_file)
        file_button.grid(column=1, row=0,pady=20, padx=10, sticky='nsew')

        self.file_label = ttk.Label(self.root, text="No file selected")
        self.file_label.grid(column=2, row=0, pady=20, padx=10)

        self.amount_widgets +=1 

        # Taking into account the addition of the entries 
        self.amount_widgets += len(self.entries)

        # Case Type Select
        case_choice_label = ttk.Label(self.root, text="Select the type of Case")
        case_choice_label.grid(column=1, row=self.amount_widgets, pady=20, padx=10, sticky='nsew')
        case_type_combo = ttk.Combobox(self.root, textvariable=self.case_type_choice, state="readonly")
        case_type_combo['values'] = list(CHOICE_MATRIX.keys())
        case_type_combo.grid(column=2, row=self.amount_widgets, pady=20, padx=10, sticky='nsew')
        case_type_combo.bind("<<ComboboxSelected>>", self.update_method_combo)

        self.amount_widgets +=1 

        # Method Select 
        method_choice_label = ttk.Label(self.root, text="Choice of Method:")
        method_choice_label.grid(column=1, row=self.amount_widgets, pady=20, padx=10, sticky='nsew')
        self.method_combo = ttk.Combobox(self.root, textvariable=self.method_choice, state="readonly")
        self.method_combo.grid(column=2, row=self.amount_widgets, pady=20, padx=10, sticky='nsew')



        self.amount_widgets +=1 

        # Options Button and Quit button 
        options_button = tk.Button(self.root, text='Options', command=self.open_options_menu)
        options_button.grid(column=1, row=self.amount_widgets, pady=20, padx=10, sticky='nsew')

        quit_button = tk.Button(self.root, text='Quit', command=self.root.quit)
        quit_button.grid(column=2, row=self.amount_widgets, pady=20, padx=10, sticky='nsew')

        self.amount_widgets +=1 


        # Launch button 
        launch_button = tk.Button(self.root, text='Launch', command=self.launch_button)
        launch_button.grid(column=1, row=self.amount_widgets, pady=20, padx=10, columnspan=2, sticky='nsew')



    def update_method_combo(self, event) -> None:
        """
        Function purpose: This function is relevant for allowing the choice of case type to affect the choice of method\n
        Inputs: 
          self = this means that this function defines a method for the class
          event = ?
        \n
        Outputs: None 
        """

        # Get selected category
        selected_category = self.case_type_choice.get()
        
        # Update second combobox values based on first
        self.method_combo['values'] = CHOICE_MATRIX.get(selected_category, [])
        self.method_choice.set('')  # Clear current selection

    def launch_button(self) -> None:
        """
        Function purpose: This function corresponds to the code executed when the Launch button is pressed  \n
        Inputs: 
          self = this means that this function defines a method for the class \n
        Outputs: None 
        """

        debug_status: bool = self.debug_mode.get()
        if debug_status: 
            print("Currently in execution of launch_button function")
            for plot in AVAILABLE_PLOTS:
                try:
                    print(f"State of plot called: {plot}, {self.selected_plots[plot].get()}")
                except Exception:
                    print(f"An error occured for {plot}, program will keep executing but beware potential undefined behaviour ahead")
        try:
            self.update_widgets(self.entries)
        except Exception:
            messagebox.showwarning("Error", "An error has occured")
            return 

        if debug_status:
            print(f"Current values of entries: {self.entries}")

        clean_input_values: dict[str, Any] =  {key: value[1] for key, value in self.entries.items()} # Actual type of values[1] is str|float 
        clean_selected_plots: dict[str, bool] = {key: value.get() for key, value in self.selected_plots.items()}
        clean_paste_to_excel: bool = self.paste_to_excel.get()

        run(self.selected_file, clean_input_values,clean_selected_plots, self.case_type, self.method, clean_paste_to_excel,self.excel_output_sheet_name, debug_status)

        
        return

    
     
    def update_widgets(self, entries:dict[str, list[ttk.Entry | float | str]]) -> None:
        """
        Function purpose:   This function adds the value of each entry to the dictionnary mapping 
                            each entry name to its ttk.Entry and does the same for the dictionnary mapping each plot to the choice of the user \n
        Inputs: 
          self = this means that this function defines a method for the class
          entries = current dictionnary mapping each entry name to its actual ttk.Entry 
        \n
        Outputs: None 
        """
        i:int=0
        j:int=0
        for choice in CHOICE_MATRIX:
            if self.case_type_choice.get() == choice:
                self.case_type = i 
                for sub_choice in CHOICE_MATRIX[choice]:
                    if self.method_choice.get() == sub_choice:
                        self.method = j 
                        break 
                    else:
                        j +=1 
                break 
            else:
                i += 1
                for sub_choice in CHOICE_MATRIX[choice]:
                    j += 1

        for key in entries:
            if self.debug_mode.get():
                print(key, entries[key])
            if key in STRING_BASED:
                if key == "Scenario (or 'All')":
                    if isinstance(entries[key][0], ttk.Entry): 
                        entry_widget = cast(ttk.Entry, entries[key][0])
                        update_dict(entries, key, str(entry_widget.get()).upper())
                    else:
                        raise TypeError(f"Warning, Unexpected behavior occured: first value of self.entries isn't an Entry, it currently is {type(entries[key][0])}")
                else: 
                    if isinstance(entries[key][0], ttk.Entry): 
                        entry_widget = cast(ttk.Entry, entries[key][0])
                        update_dict(entries, key, str(entry_widget.get()))
                    else:
                        raise TypeError(f"Warning, Unexpected behavior occured: first value of self.entries isn't an Entry, it currently is {type(entries[key][0])}")
            else:
                if isinstance(entries[key][0], ttk.Entry): 
                    entry_widget = cast(ttk.Entry, entries[key][0])
                    update_dict(entries, key, float(entry_widget.get()))
                else:
                    raise TypeError(f"Warning, Unexpected behavior occured: first value of self.entries isn't an Entry, it currently is {type(entries[key][0])}")
        

        if self.debug_mode.get(): print(f"Case type is {self.case_type} and method is {self.method}")
        return 
    

    def choose_file(self) -> None:
        """
        Function purpose: This function corresponds to the code executed when the chose file button is pressed and concatenated the file name if too long to display on the GUI  \n
        Inputs: 
          self = this means that this function defines a method for the class \n
        Outputs: None 
        """
        file_path: str = filedialog.askopenfilename(title="Select a file")
        if file_path:
            # Truncate if filename is too long
            if len(file_path) > int(GUI_CONFIG['max_filename_display']):
                start = file_path[:int(GUI_CONFIG['filename_truncate_start'])]
                end = file_path[-int(GUI_CONFIG['filename_truncate_end']):]
                display_path = f"{start}...{end}"
            else:
                display_path = file_path

            self.file_label.config(text=display_path)
            self.selected_file: str = file_path  # Save full path if needed elsewhere 
    
    def validate_input(self, who:str, what:str) -> bool:
        """
        Function purpose: This function is what verifies that user input is valid or not  \n
        Inputs: 
          self = this means that this function defines a method for the class \n
          who = which entry called this function
          what = the text that the user has just inputted 
        Outputs: Whether or not the user input is valid (as a Boolean)
        """
        isValid:bool = True 
        if what == '':
            return True
        if who in ['.!entry' + str(find_index(self.entries, element)+1) for element in STRING_BASED]:
            try:
                input = str(what)
                if not(input[0].isdigit()) :
                    isValid = True
                else:
                    isValid = False 
            except:
                isValid = False 
        else:
            try:
                input=float(what)
                isValid = True 
            except:
                isValid = False 
        return isValid 

    def erase_input(self, who:str) -> None:
        """
        Function purpose: This function corresponds to the code executed when user input is considered invalid  \n
        Inputs: 
          self = this means that this function defines a method for the class \n
          who = the entry which called this function
        Outputs: None 
        """
        if who in ['.!entry' + str(find_index(self.entries, element)+1) for element in STRING_BASED]:
            if who == '.!entry' + str(find_index(self.entries, "Scenario (or 'All')")+1): 
                messagebox.showwarning("Invalid Entry", "Please enter a letter followed by a number")
            else:
                messagebox.showwarning("Invalid Entry", "Please enter an actual sheet name")
        else:
            messagebox.showwarning("Invalid Entry", "Please enter a number")
        return 

    def open_options_menu(self) -> None:
        """
        Function purpose: This function corresponds to the code executed when the Options button is pressed  \n
        Inputs: 
          self = this means that this function defines a method for the class \n
        Outputs: None 
        """
        # Create a new popup window
        popup = tk.Toplevel(self.root)
        popup.title("Options Menu")
        popup.grab_set()
        popup.columnconfigure(0, weight=1)
        popup.columnconfigure(1, weight=1)

        ttk.Label(popup, text="Select which plots").grid(column=0, row=0, padx=5, sticky='w')
        ttk.Label(popup, text="you want to compute").grid(column=0, row=1, padx=5, sticky='w')
        
        i:int=0
        for plot in AVAILABLE_PLOTS:
            ttk.Checkbutton(popup, text=plot, variable=self.selected_plots[plot]).grid(column=1, row=i, sticky='w')
            i+=1


        def toggle_entry() -> None:
            if self.paste_to_excel.get():
                excel_output_entry.configure(state="normal")
            else:
                excel_output_entry.configure(state="disabled")
            return 
      
        i+=2 # Adding some space

        # Excel Formatting

        ttk.Checkbutton(popup, text="Do you wish to automatically paste the result to excel?", variable=self.paste_to_excel,command=toggle_entry).grid(column=0, row=i, pady=10, sticky="sw")
        ttk.Label(popup, text="Enter output sheet name:").grid(column=0, row=i+1, padx=5, sticky='w')
        excel_output_entry = ttk.Entry(popup, state='disabled')
        excel_output_entry.grid(column =1, row=i+1, sticky='w')
        i+=2


        # Adding more space
        i+= 1
        # Debug_button
        ttk.Checkbutton(popup, text="Enable Debug mode?", variable=self.debug_mode).grid(column=0, row=i, pady=10, columnspan=2)


        def submit() -> None:
            selected = [plot for plot, var in self.selected_plots.items() if var.get()]
            self.excel_output_sheet_name = excel_output_entry.get()
            print(self.excel_output_sheet_name)
            messagebox.showinfo("Selected Plots", f"Selected plots: {', '.join(selected)}")
            popup.destroy()
            return 

        

        ttk.Button(popup, text="Confirm", command=submit).grid(column=0, row=i+1, columnspan=2) 


        return 