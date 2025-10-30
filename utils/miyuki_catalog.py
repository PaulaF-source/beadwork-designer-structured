# utils/miyuki_catalog.py
# Catálogo Extendido de Miyuki Delica 11/0 (DB)
# Incluye una gama más amplia de acabados (Finish) esenciales para el diseño de joyería.

MIYUKI_CATALOG = {
    # --- GRUPO 1: OPAQUE (Opaco - Sin Brillo) ---
    "DB0001": {"hex": "#FFFFFF", "name": "Opaque White", "finish": "Opaque"},
    "DB0002": {"hex": "#E8E8E8", "name": "Opaque Light Gray", "finish": "Opaque"},
    "DB0010": {"hex": "#1C1C1C", "name": "Opaque Black", "finish": "Opaque"},
    "DB0072": {"hex": "#080C8F", "name": "Opaque Cobalt", "finish": "Opaque"},
    "DB0723": {"hex": "#D7004F", "name": "Opaque Red", "finish": "Opaque"},
    
    # --- GRUPO 2: METALLIC / PLATED / GALVANIZED (Brillo Intenso) ---
    "DB0021": {"hex": "#505050", "name": "Metallic Dark Gunmetal", "finish": "Metallic"},
    "DB0034": {"hex": "#FFD700", "name": "24Kt Gold-Plated", "finish": "Plated"},
    "DB0035": {"hex": "#C0C0C0", "name": "Galvanized Silver", "finish": "Galvanized"},
    "DB1832": {"hex": "#E0B750", "name": "Duracoat Galvanized Gold", "finish": "Duracoat Galvanized"},
    "DB2273": {"hex": "#A0522D", "name": "Duracoat Galvanized Sepia", "finish": "Duracoat Galvanized"},
    
    # --- GRUPO 3: LUSTER / AB (Lustrado / Efecto Brillo Suave) ---
    "DB0050": {"hex": "#F0FFFF", "name": "Crystal Luster", "finish": "Luster"},
    "DB0160": {"hex": "#6C6C6C", "name": "Grey Luster", "finish": "Luster"},
    "DB0251": {"hex": "#4A4A4A", "name": "Smoke Gray Gold Luster AB", "finish": "Luster AB"},
    "DB0897": {"hex": "#D8BFD8", "name": "Opaque Rose Gold Luster", "finish": "Luster"},
    
    # --- GRUPO 4: SILVER LINED / DYE (Línea de Plata / Transparente Brillante) ---
    "DB0041": {"hex": "#FFFFFF", "name": "Silver Lined Crystal", "finish": "Silver Lined"},
    "DB0043": {"hex": "#CD5C5C", "name": "Silver Lined Red", "finish": "Silver Lined"},
    "DB0142": {"hex": "#98C6D4", "name": "Transparent Light Blue", "finish": "Transparent"},
    "DB0683": {"hex": "#846067", "name": "Dyed Plum", "finish": "Dyed"}, # Color teñido - baja durabilidad, pero distinto
    
    # --- GRUPO 5: MATTE / FROST (Mate / Sin Brillo) ---
    "DB0310": {"hex": "#696969", "name": "Matte Opaque Black", "finish": "Matte Opaque"},
    "DB0791": {"hex": "#F0E68C", "name": "Matte Transparent Yellow", "finish": "Matte Transparent"},
    "DB1845": {"hex": "#B0C4DE", "name": "Frosted Light Steel Blue", "finish": "Frosted"},
}

def get_miyuki_data(code: str) -> dict | None:
    """Busca y retorna los datos de color Miyuki por código (DBxxxx)."""
    normalized_code = code.upper().replace(" ", "").strip()
    return MIYUKI_CATALOG.get(normalized_code)