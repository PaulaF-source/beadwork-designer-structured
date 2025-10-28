# utils/helpers.py

from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize # QSize needed if svg_to_qicon uses it implicitly, but not directly needed for icons below

# --- SVG Icon Paths ---
# It's good practice to name constants in UPPER_SNAKE_CASE
ICON_SAVE = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-save" viewBox="0 0 16 16"><path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v4.5h2a.5.5 0 0 1 .354.854l-2.5 2.5a.5.5 0 0 1-.708 0l-2.5-2.5A.5.5 0 0 1 5.5 6.5h2V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z M8 13.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/></svg>"""
ICON_LOAD = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-folder2-open" viewBox="0 0 16 16"><path d="M1 3.5A1.5 1.5 0 0 1 2.5 2h2.764c.958 0 1.76.746 1.97.686C7.996 2.68 8.683 2.5 9.5 2.5h3A1.5 1.5 0 0 1 14 4V5.5H2V3.5zM2 6h12v-.5a.5.5 0 0 0-.5-.5H9.5a.5.5 0 0 1-.485-.356L8.854 3.146A.5.5 0 0 0 8.369 3H4.5a.5.5 0 0 0-.485.356L3.854 4.146A.5.5 0 0 1 3.369 4H2.5a.5.5 0 0 0-.5.5V6zm1.33 1A1.5 1.5 0 0 0 1.5 8.5v4a1.5 1.5 0 0 0 1.5 1.5h9a1.5 1.5 0 0 0 1.5-1.5v-4A1.5 1.5 0 0 0 12.17 7H1.83z M1.5 8a.5.5 0 0 1 .5.5V12a.5.5 0 0 1-.5.5H.79A1.5 1.5 0 0 1 0 11.21V8.5A1.5 1.5 0 0 1 1.5 7h.83z"/></svg>"""
ICON_EXPORT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-image" viewBox="0 0 16 16"><path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/><path d="M2.002 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2h-12zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12V3a1 1 0 0 1 1-1h12z"/></svg>"""
ICON_CLEAR = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/></svg>"""
ICON_APPLY = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-check-lg" viewBox="0 0 16 16"><path d="M12.736 3.97a.733.733 0 0 1 1.047 0c.286.289.29.756.01 1.05L7.88 12.01a.733.733 0 0 1-1.065.02L3.217 8.384a.757.757 0 0 1 0-1.06.733.733 0 0 1 1.047 0l3.052 3.093 5.4-6.425a.247.247 0 0 1 .02-.022z"/></svg>"""
ICON_PREVIEW = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"><path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/><path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/></svg>"""

def svg_to_qicon(svg_string: str, color: str = "#f8f9fa") -> QIcon:
    """
    Creates a QIcon from an SVG string, replacing 'currentColor' with the specified color.

    Args:
        svg_string: The SVG content as a string.
        color: The color (hex or name) to replace 'currentColor'.

    Returns:
        A QIcon generated from the modified SVG.
    """
    # Using type hints (str, -> QIcon) is good practice
    try:
        final_svg = svg_string.replace("currentColor", color).encode('utf-8')
        pixmap = QPixmap()
        # It's safer to check the return value of loadFromData
        if pixmap.loadFromData(final_svg, "SVG"):
            return QIcon(pixmap)
        else:
            print(f"Warning: Failed to load SVG data for icon.")
            return QIcon() # Return an empty icon on failure
    except Exception as e:
        print(f"Error creating icon from SVG: {e}")
        return QIcon() # Return an empty icon on error