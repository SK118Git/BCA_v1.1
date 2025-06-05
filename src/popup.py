from typing import Optional 
from tkinter import Label 
from tkinter.ttk import Progressbar

class Progress_Popup:
    def __init__(self, progress_label: Optional[Label]=None, progress: Optional[Progressbar]=None):
        self.label = progress_label
        self.bar= progress
        return 

    def update_vals(self, message:str, current_progress:float):
        if self.label and self.bar:
            self.bar['value'] = current_progress
            self.bar.update_idletasks()

            # Change label text
            self.label.config(text=message)
            self.label.update_idletasks()
        return 
   
