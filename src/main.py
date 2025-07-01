# =============================================================================
# main.py - Entry point for the Business Case Analysis Tool
# =============================================================================
# External imports
import tkinter as tk

# =============================================================================
# Internal imports
from frontend.frontend import BCA_App

# =============================================================================


def main() -> None:
    """
    Main entry point for the application. \n
    """
    root = tk.Tk()
    app = BCA_App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
