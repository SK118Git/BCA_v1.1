# ============================================================================================================================
# popup.py - File containg the class that manages the progression bar popup  
#
# Note: this class was put into its own file to avoid circular import loops 
# ============================================================================================================================
# External Imports 
from typing import Optional 
from tkinter import Label 
from tkinter.ttk import Progressbar
# ============================================================================================================================

class Progress_Popup:
    def __init__(self, progress_label: Optional[Label]=None, progress: Optional[Progressbar]=None):
        self.label = progress_label
        self.bar= progress
        return 

    def update_vals(self, message:str, current_progress:float):
        """
        Function purpose: Updates the progress bar with the inputed message and value 
        Args:
            message: the desired message to appear on the progress bar
            current_progress: the desired percentage of the progress bar 
        """
        if self.label and self.bar:
            self.bar['value'] = current_progress
            self.bar.update_idletasks()

            # Change label text
            self.label.config(text=message)
            self.label.update_idletasks()
        return 
   
