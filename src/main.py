# =============================================================================
# main.py - Entry point for the Business Case Analysis Tool
# =============================================================================
# External imports 
import tkinter as tk
# =============================================================================
# Internal imports 
from frontend import BCA_App
from extra import setup_logging
# =============================================================================

def main() -> None:
    """
    Main entry point for the application. \n
    Inputs: None \n 
    Outputs: GUI
    """
    root = tk.Tk()
    app = BCA_App(root)
    root.mainloop()

if __name__ == "__main__":
    main()