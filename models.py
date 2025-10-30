# models.py

from PyQt6.QtGui import QColor

class BeadColorEntry:
    """
    Contenedor de datos para un color de cuenta, incluyendo su metadata 
    de acabado para efectos visuales y catalogación.
    """
    def __init__(self, color: QColor, finish: str = "Opaque", code: str | None = None, name: str | None = None):
        """
        Args:
            color (QColor): El color base (HEX/RGB).
            finish (str): Tipo de acabado (Opaque, Metallic, Luster, Transparent, Matte, etc.).
            code (str | None): Código oficial de la cuenta (ej. 'DB0034').
            name (str | None): Nombre descriptivo (ej. 'Galvanized Gold Duracoat').
        """
        if not color.isValid():
            raise ValueError("BeadColorEntry requires a valid QColor.")
            
        self.color: QColor = color
        self.finish: str = finish
        self.code: str | None = code
        self.name: str = name if name else color.name().upper() # Usar HEX si no hay nombre
        
    def __repr__(self):
        """Representación legible para depuración."""
        return f"BeadColorEntry(HEX={self.color.name()}, Finish='{self.finish}', Code='{self.code}')"

    def is_shiny(self) -> bool:
        """Determina si el acabado es brillante o metálico."""
        # Palabras clave comunes para el brillo en Miyuki Delica
        return any(f.lower() in self.finish.lower() for f in ["metallic", "luster", "galvanized", "plated", "rainbow", "ab"])

# --- End of BeadColorEntry class ---