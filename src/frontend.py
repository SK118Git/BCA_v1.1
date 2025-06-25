# ============================================================================================================================
# gui.py - File containg all functions that don't need to be modified, are not used for plotting, nor the GUI, not the BCA 
# ============================================================================================================================
# External library imports 
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import Any, cast
from threading import Thread 
import pandas as pd

# =============================================================================
# Internal library imports 
from modifiable import AVAILABLE_PLOTS, INPUT_FIELDS, GUI_CONFIG, STRING_BASED, CHOICE_MATRIX
from extra import update_dict, find_index, log_print
from bca import run 
from popup import Progress_Popup
# =============================================================================



class BCA_App:
    def __init__(self, root:tk.Tk) -> None:
        """
        Function purpose: Initializer of the class \n
        Args: 
          root: the name of the root window for the GUI  
        """
        self.initalize_vars(root)
        self.configure_window()
        self.entries: dict[str, list[ttk.Entry | float | str]] = self.create_entry_widgets()
        self.create_buttons()

    def initalize_vars(self, root:tk.Tk) -> None:
        """
        Function purpose: 
            Initializes all the main variables of the class 
        Note: 
            This method was created simply to clean-up the init 
        Args: 
          root: the name of the root window for the GUI  
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


        self.excel_param_input_sheet_name = tk.StringVar()

        self.isOkay = root.register(self.validate_input)
        self.correctInput= root.register(self.erase_input)


        return 

    def configure_window(self) -> None:
        """
        Function purpose: This function manages the settings for the GUI's window \n
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
        Function purpose: 
            Initializer of the class 
        Outputs: 
            Creates the entries dictionnary which maps to each entry (defined in tomodify.py) the actual ttk.Entry
        """
        entries: dict[str, list[ttk.Entry | float | str]] = {field:[] for field in INPUT_FIELDS}
        i:int=1

        for key in entries:
            entries[key].append(self.create_entry(key,i+1))
            i+=1
        if self.debug_mode.get():
            log_print(f"Currently in creation of entry dict the created dict is: {entries}")
        return entries  

    def create_entry(self, name:str, position:int) -> ttk.Entry:
        """ 
        Function purpose: 
            This function manages the creation of each ttk.Entry 
        Output: 
            An entry created using the provided info
        Note: 
            This function was created as all entries have the same settings so it allows for less repetition in the code
        
        Args: 
          name: the name of the entry aka what is written in the label of the entry 
          position: the row this entry should go on 
        
        """
        label = ttk.Label(self.root, text=name + ':')
        entry = ttk.Entry(self.root, validate="key", validatecommand=(self.isOkay, '%W', '%P'), invalidcommand=(self.correctInput, '%W'))

        label.grid(column=1, row=position, padx=10, pady=2, sticky='w')
        entry.grid(column=2, row=position, padx=10, pady=2)

        return entry


    def create_buttons(self) -> None:
        """
        Function purpose: 
            This function creates all the buttons and their respective labels 
        Note: Are created label and button for: 
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

        self.load_vals_button = ttk.Button(self.root, text="Do you want to load the values from the sheet?", command=self.load_vals)
        self.load_vals_button.grid(column=1, row=self.amount_widgets, padx=10, pady=20, sticky='nsew')

        self.load_vals_label = ttk.Entry(self.root, validate="key", validatecommand=(self.isOkay, '%W', '%P'), invalidcommand=(self.correctInput, '%W'))
        self.load_vals_label.grid(column=2, row=self.amount_widgets, padx=10, pady=20, sticky='nsew')

        self.amount_widgets += 1
        

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
        """

        # Get selected category
        selected_category = self.case_type_choice.get()
        
        # Update second combobox values based on first
        self.method_combo['values'] = CHOICE_MATRIX.get(selected_category, [])
        self.method_choice.set('')  # Clear current selection

    def launch_button(self) -> None:
        """ 
        Function purpose: This function corresponds to the code executed when the Launch button is pressed 
        """

        log_print("Currently in execution of launch_button function")

        debug_status: bool = self.debug_mode.get()
        if debug_status: 
            for plot in AVAILABLE_PLOTS:
                try:
                    log_print(f"State of plot called: {plot}, {self.selected_plots[plot].get()}")
                except Exception:
                    log_print(f"An error occured for {plot}, program will keep executing but beware potential undefined behaviour ahead")
        try:
            self.update_widgets(self.entries)
        except ValueError:
            messagebox.showwarning("Warning!", "Some of the inputs are empty or invalid")
            return 
        except Exception as e:
            messagebox.showerror("Unexpected error", f"{type(e).__name__}: {e}")
            return 

        if not(hasattr(self, "selected_file")):
            messagebox.showwarning("Warning!", "No file selected")
            return 

        if debug_status:
            log_print(f"Current values of entries: {self.entries}")

        clean_input_values: dict[str, Any] =  {key: value[1] for key, value in self.entries.items()} # Actual type of values[1] is str|float 
      

        clean_selected_plots: dict[str, list[Any]] = {
            key: [value.get(), AVAILABLE_PLOTS[key] ]
            for key, value in self.selected_plots.items()
            }

        clean_paste_to_excel: bool = self.paste_to_excel.get()


        popup = tk.Toplevel(self.root)
        popup.title("Progress")
        popup.geometry("350x100")
        popup.resizable(True, True)

        # Label (optional)
        progress_pp = Progress_Popup(tk.Label(popup, text="Running simulation..."), ttk.Progressbar(popup, orient='horizontal', length=300, mode='determinate'))

        assert(progress_pp.bar != None and progress_pp.label != None)
        progress_pp.label.pack(pady=(10,5))
        progress_pp.bar.pack(pady=(0,10))
        
        
        thread = Thread(target=self.no_error_run, args=(
            self.selected_file,
            self.excel_output_sheet_name, 
            debug_status,
            clean_paste_to_excel,
            self.case_type,
            self.method,
            clean_input_values,
            clean_selected_plots,
            progress_pp
        ))
        thread.start()
        
        return

    def no_error_run(self, selected_file:str,  excel_output_sheet_name:str, debug_status:bool, paste_to_excel:bool, case_type:int, method:int, input_values:dict[str, Any], selected_plots:dict[str, Any], progress_pp:Progress_Popup):
        """
        Function purpose: Function which catches final errors when trying to run
        """
        assert(progress_pp.bar != None and progress_pp.label != None)

        try:
           run(selected_file, excel_output_sheet_name, debug_status, paste_to_excel, case_type, method, input_values, selected_plots, progress_pp)
        except AttributeError:
            progress_pp.bar.stop() 
            progress_pp.label.config(text="Error: You didn't select a file") 
        except ValueError as e:
            progress_pp.bar.stop()
            progress_pp.label.config(text="Error (ValueError): " + str(e) + "\n Make sure you selected the right method and named the columns correctly.")
            log_print(f"Warning (ValueError Raised): {str(e)} \n Make sure you selected the right method and named the columns correctly.")
        except Exception as e:
            progress_pp.bar.stop()
            progress_pp.label.config(text="Error: " + str(e) + "\n Make sure you selected the right method and named the columns correctly.")
            log_print(f"Warning: {str(e)} \n Make sure you selected the right method and named the columns correctly.")
        return 
    
     
    def update_widgets(self, entries:dict[str, list[ttk.Entry | float | str]]) -> None:
        """ 
        This function adds the value of each entry to the dictionnary mapping each entry name to its ttk.Entry 
        and does the same for the dictionnary mapping each plot to the choice of the user 

        Outputs: None 
        
        Args: 
          entries: current dictionnary mapping each entry name to its actual ttk.Entry 
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
                log_print(f"Value of {key} entry before update: {entries[key]}")
            if key in STRING_BASED:
                if key == "Scenario(s) (seperate with ',' or write 'All')":
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
        

        if self.debug_mode.get(): log_print(f"Case type is {self.case_type} and method is {self.method}")
        return 
    

    def choose_file(self) -> None:
        """
        Function purpose: This function corresponds to the code executed when the chose file button is pressed and concatenated the file name if too long to display on the GUI  \n
        """
        file_path: str = filedialog.askopenfilename(title="Select a file")
        if file_path:
            # Truncate if filename is too long
            if len(file_path) > int(GUI_CONFIG['max_file_name_display']):
                start = file_path[:int(GUI_CONFIG['file_name_truncate_start'])]
                end = file_path[-int(GUI_CONFIG['file_name_truncate_end']):]
                display_path = f"{start}...{end}"
            else:
                display_path = file_path

            self.file_label.config(text=display_path)
            self.selected_file: str = file_path  # Save full path if needed elsewhere 
    
    def validate_input(self, who:str, what:str) -> bool:
        """
        Function purpose: This function is what verifies that user input is valid or not  \n
        Outputs: Whether or not the user input is valid (as a Boolean)

        Args: 
          who: which entry called this function
          what: the text that the user has just inputted \n 
        """
        log_print(f"Currently entry named: {who} is being validated")
        isValid:bool = True 
        if what == '':
            return True
        if who in ['.!entry' + str(find_index(self.entries, element)+1) for element in STRING_BASED] or (who == ".!entry" + str(len(self.entries)+1)):
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
        Args: 
          who: the entry which called this function \n
        """
        if who in ['.!entry' + str(find_index(self.entries, element)+1) for element in STRING_BASED]:
            if who == '.!entry' + str(find_index(self.entries, "Scenario(s) (seperate with ',' or write 'All')")+1): 
                messagebox.showwarning("Invalid Entry", "Please enter a letter followed by a number")
            else:
                messagebox.showwarning("Invalid Entry", "Please enter an actual sheet name")
        else:
            messagebox.showwarning("Invalid Entry", "Please enter a number")
        return 

    def open_options_menu(self) -> None:
        """
        Function purpose: This function corresponds to the code executed when the Options button is pressed  \n
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
            messagebox.showinfo("Selected Plots", f"Selected plots: {', '.join(selected)}")
            popup.destroy()
            return 

        

        ttk.Button(popup, text="Confirm", command=submit).grid(column=0, row=i+1, columnspan=2) 


        return 

    def load_vals(self) -> None: 
        if self.load_vals_label.get() != "":
            try:
                vals = pd.read_excel(self.selected_file, sheet_name=self.load_vals_label.get(), index_col=0, header=None)
                log_print(f"Values found in sheet names {self.load_vals_label.get()}: \n {vals}" )
                for key in self.entries:
                    if key not in STRING_BASED:
                        log_print(f"Currently modifying value of {key} and replacing with {vals.loc[key].dropna().iloc[0]}")
                        self.entries[key][0].delete(0, 'end')
                        self.entries[key][0].insert(0, vals.loc[key].dropna().iloc[0])
            except ValueError:
                log_print("Error, no worksheet with that name found")
                messagebox.showwarning("Error", "No worksheet with that name was found")
            except KeyError as e:
                log_print(f"Error, Row name mismatch, first error occured at row named: {e}")
                messagebox.showwarning("Error", f"Row name mismatch, first error occured at row named: {e}")
            except Exception as e:
                log_print(f"Unknown error has occured: {e}")
                messagebox.showwarning("Error", f"Unknown error has occured: {e}")
        return 


    