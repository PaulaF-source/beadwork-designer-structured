# utils/helpers.py

# --- Imports needed for this module ---
from PyQt6.QtGui import QPixmap, QIcon, QColor, QPainter
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtSvg import QSvgRenderer # Needed for advanced color rendering

# --- SVG Icon Paths ---
# Good practice: Constants are in UPPER_SNAKE_CASE

ICON_SAVE = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-save" viewBox="0 0 16 16"><path d="M2 1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1H9.5a1 1 0 0 0-1 1v4.5h2a.5.5 0 0 1 .354.854l-2.5 2.5a.5.5 0 0 1-.708 0l-2.5-2.5A.5.5 0 0 1 5.5 6.5h2V2a2 2 0 0 1 2-2H14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V2a2 2 0 0 1 2-2h2.5a.5.5 0 0 1 0 1H2z M8 13.5a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3z"/></svg>"""
ICON_LOAD = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-folder2-open" viewBox="0 0 16 16"><path d="M1 3.5A1.5 1.5 0 0 1 2.5 2h2.764c.958 0 1.76.746 1.97.686C7.996 2.68 8.683 2.5 9.5 2.5h3A1.5 1.5 0 0 1 14 4V5.5H2V3.5zM2 6h12v-.5a.5.5 0 0 0-.5-.5H9.5a.5.5 0 0 1-.485-.356L8.854 3.146A.5.5 0 0 0 8.369 3H4.5a.5.5 0 0 0-.485.356L3.854 4.146A.5.5 0 0 1 3.369 4H2.5a.5.5 0 0 0-.5.5V6zm1.33 1A1.5 1.5 0 0 0 1.5 8.5v4a1.5 1.5 0 0 0 1.5 1.5h9a1.5 1.5 0 0 0 1.5-1.5v-4A1.5 1.5 0 0 0 12.17 7H1.83z M1.5 8a.5.5 0 0 1 .5.5V12a.5.5 0 0 1-.5.5H.79A1.5 1.5 0 0 1 0 11.21V8.5A1.5 1.5 0 0 1 1.5 7h.83z"/></svg>"""
ICON_EXPORT = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-image" viewBox="0 0 16 16"><path d="M6.002 5.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0z"/><path d="M2.002 1a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V3a2 2 0 0 0-2-2h-12zm12 1a1 1 0 0 1 1 1v6.5l-3.777-1.947a.5.5 0 0 0-.577.093l-3.71 3.71-2.66-1.772a.5.5 0 0 0-.63.062L1.002 12V3a1 1 0 0 1 1-1h12z"/></svg>"""
ICON_CLEAR = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash" viewBox="0 0 16 16"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/></svg>"""
ICON_PREVIEW = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-eye" viewBox="0 0 16 16"><path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 1 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 1 1.172 8z"/><path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/></svg>"""

# --- NUEVOS ICONOS AÑADIDOS ---

ICON_UNDO = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-counterclockwise" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M8 3a5 5 0 1 1-4.546 2.914.5.5 0 0 0-.908-.417A6 6 0 1 0 8 2v1z"/>
  <path d="M8 4.466V.534a.25.25 0 0 0-.41-.192L5.23 2.308a.25.25 0 0 0 0 .384l2.36 1.966A.25.25 0 0 0 8 4.466z"/>
</svg>
"""

ICON_REDO = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-clockwise" viewBox="0 0 16 16">
  <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
  <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
</svg>
"""

ICON_PENCIL = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil-fill" viewBox="0 0 16 16">
  <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708l-3-3zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207l6.5-6.5zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.499.499 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11l.178-.178z"/>
</svg>
"""

# Icono de simetría vertical más claro: Muestra una forma y su reflejo
ICON_SYMMETRY_VERTICAL_DESCRIPTIVE = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="currentColor" d="M4 4h2V3H4a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h2V6H4V4z M12 4h-2v3h2v1h-2a1 1 0 0 0-1 1v2a1 1 0 0 0 1 1h2v-1h-2v-3h2V4z"/>
  <path fill="currentColor" stroke-width="2" stroke="currentColor" stroke-dasharray="2,2" d="M8 1 v14"/>
</svg>
"""

# Icono de simetría horizontal más claro: Muestra una forma y su reflejo
ICON_SYMMETRY_HORIZONTAL_DESCRIPTIVE = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path fill="currentColor" d="M4 4v2H3V4a1 1 0 0 1 1-1h2v2H4z M4 12v-2H3v2a1 1 0 0 0 1 1h2v-2H4z M12 4v2h-2V3h2a1 1 0 0 1 1 1z"/>
  <path fill="currentColor" stroke-width="2" stroke="currentColor" stroke-dasharray="2,2" d="M1 8 h14"/>
</svg>
"""

# --- Helper Function ---

def svg_to_qicon(svg_string: str, color: str = "#f8f9fa") -> QIcon:
    """
    Converts an SVG string to a QIcon, applying a color.
    
    This function creates a QPixmap, renders the SVG onto it using
    a QPainter (which allows the SVG to be scaled and colored),
    and then returns a QIcon from that pixmap.
    
    Args:
        svg_string: The SVG content as a string.
        color: The color (hex or name) to replace 'currentColor' or use as default fill.
               (Note: For these icons, 'currentColor' is used explicitly).
    
    Returns:
        A QIcon generated from the modified SVG.
    """
    # Reemplazar 'currentColor' con el color deseado
    # Esta es la forma más robusta de colorear SVGs que usan 'currentColor'
    colored_svg_string = svg_string.replace('currentColor', color)

    # Convertir el string a bytes UTF-8
    svg_bytes = bytes(colored_svg_string, 'utf-8')

    # Usar QSvgRenderer para dibujar el SVG en un QPixmap
    # Esto maneja el escalado y el color mejor que loadFromData
    
    # Definir un tamaño estándar para los iconos de la barra de herramientas (ej. 24x24)
    icon_size = QSize(24, 24) 
    
    pixmap = QPixmap(icon_size)
    pixmap.fill(Qt.GlobalColor.transparent) # Empezar con un fondo transparente

    # Configurar el painter y el renderer
    painter = QPainter(pixmap)
    renderer = QSvgRenderer(svg_bytes)

    if renderer.isValid():
        # Dibujar el SVG renderizado en el pixmap
        renderer.render(painter)
    else:
        print(f"Warning: Failed to render SVG for icon.")
        # Opcional: dibujar una 'X' roja si falla la renderización
        painter.setPen(QColor("red"))
        painter.drawLine(0, 0, icon_size.width(), icon_size.height())
        painter.drawLine(0, icon_size.height(), icon_size.width(), 0)

    painter.end() # Finalizar el dibujo

    return QIcon(pixmap)