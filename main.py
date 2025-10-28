# main.py

import sys
import os # Import the 'os' module to handle file paths

from PyQt6.QtWidgets import QApplication

# Import the main window class from its file
from main_window import MainWindow 

# --- Best Practice: Function to load stylesheet ---
def load_stylesheet(filename: str) -> str:
    """Loads a Qt stylesheet file (.qss) and returns its content."""
    try:
        # Construct the full path relative to this script file
        # __file__ is the path to the current script (main.py)
        # os.path.dirname gets the directory containing the script
        # os.path.join creates a cross-platform path
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, filename)

        with open(file_path, "r", encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: Stylesheet file not found at '{file_path}'. Using default styles.")
        return "" # Return empty string if file not found
    except Exception as e:
        print(f"Error loading stylesheet '{filename}': {e}")
        return "" # Return empty string on other errors

# --- Main execution block ---
if __name__ == "__main__":
    # 1. Create the QApplication instance
    #    This is the core object managing GUI application resources.
    app = QApplication(sys.argv) # sys.argv allows command line arguments if needed

    # 2. Load the stylesheet
    #    Separating styles makes the application easier to theme.
    stylesheet = load_stylesheet("styles/dark_theme.qss")
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # 3. Create the MainWindow instance
    #    This initializes your main application window using the class we defined.
    window = MainWindow()

    # 4. Show the main window
    #    Make it visible. showMaximized() is often good for design tools.
    window.showMaximized()
    # window.show() # Use this for a normal, non-maximized window

    # 5. Start the application's event loop
    #    This hands control over to Qt to handle user interactions (clicks, etc.)
    #    sys.exit() ensures a clean exit code is returned when the app closes.
    sys.exit(app.exec())