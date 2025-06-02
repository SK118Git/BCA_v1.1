# =============================================================================
# main.py - Entry point for the Business Case Analysis Tool
# =============================================================================
# External imports 
import tkinter as tk
# =============================================================================
# Internal imports 
from gui import BCA_App
# =============================================================================

def main():
    """
    Main entry point for the application.
    Inputs: None
    Outputs: GUI
    """
    root = tk.Tk()
    app = BCA_App(root)
    root.mainloop()

if __name__ == "__main__":
    main()