# =============================================================================
# main.py - Entry point for the Business Case Analysis Tool
# =============================================================================


import tkinter as tk
from gui import BCA_App

def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = BCA_App(root)
    root.mainloop()

if __name__ == "__main__":
    main()