'''
Templates de la etiqueta de PRODUCTO WS ComBox70 (63 x 50 mm).

Alto ajustado a 50 mm para imprimir en el rollo continuo de 50 mm de la QL
(DK-22223). Ese rollo solo imprime de 1,6 a 48,4 mm: todo el contenido debe
quedar dentro de esa franja (si no, la app avisa y no imprime).

Un template por variante, independientes entre sí: un cambio en EU no toca
ROW. Cada template es una lista de elementos que dibuja
WS_product_label.py. Todas las medidas en mm desde la esquina superior
izquierda; los tamaños de letra en puntos (pt).

Campos variables (se sustituyen en los textos entre llaves):
    {imei}    IMEI (15 dígitos, se valida el dígito de control)
    {serial}  nº de serie (también va en el QR)
Campos fijos de cada variante ("fixed"): {product}, {model}, {article},
{anatel}. Si un texto usa un campo que no está en "fixed", la app avisa con
un error claro en lugar de fallar.

Tipos de elemento:
    asset      imagen encajada en 'box' (x, y, ancho, alto).
               Se le quita el margen blanco para que llene el hueco
               ("trim": False lo desactiva). "crop": (izq, arriba, der, abajo)
               en fracciones 0..1 para quedarse con una parte de la imagen,
               o "top_block" para quedarse con el dibujo de arriba y quitar
               el texto que venga debajo separado por un hueco en blanco.
    text       una línea; 'runs' = [(estilo, texto), ...] para mezclar
               negrita y normal; 'anchor' l/m/r; y = línea media del texto
    lines      varias líneas con el mismo estilo; 'lead' = interlineado mm
    paragraph  texto que se reparte en líneas dentro de 'box'; si no cabe,
               reduce el tamaño
    rbox       recuadro con esquinas redondeadas
    qr         código QR con 'data' en un cuadrado de lado 'size'
    dc_symbol  símbolo de corriente continua (IEC 60417-5031); con 'after'
               se coloca detrás de ese texto, a 'gap' mm

Cada template tiene además "offset": (dx, dy) en mm, que desplaza TODO su
contenido. Sirve para centrarlo en la franja imprimible o corregir una
impresora que imprime algo descentrada, sin tocar cada coordenada.

Las imágenes se buscan, por orden, en WS_PRODUCT_ASSETS_DIR (config.json),
images/ws/, images/leica/ e images/.
'''

LABEL_W_MM, LABEL_H_MM = 63, 50

PRODUCT_NAME = "ComBox70"

# --- Bloques comunes a las dos variantes -------------------------------------
# (se copian en cada template; si un día cambian para una sola variante,
#  basta con editar esa copia)

def _header():
    return [
        {"type": "asset", "name": "ws_logo_black", "box": (3.3, 2.8, 16.0, 10.2), "align": "l"},
        # Bloque de datos arriba a la derecha (alineado a la derecha)
        {"type": "text", "x": 58.1, "y": 6.2, "anchor": "r", "size": 4.7,
         "runs": [("bold", "Product"), ("regular", ": {product}")]},
        {"type": "text", "x": 58.1, "y": 8.15, "anchor": "r", "size": 4.7,
         "runs": [("bold", "Model"), ("regular", ": {model}")]},
        {"type": "text", "x": 58.1, "y": 10.1, "anchor": "r", "size": 4.7,
         "runs": [("bold", "Article No: "), ("regular", "{article}")]},
        {"type": "text", "x": 58.1, "y": 12.05, "anchor": "r", "size": 4.7,
         "runs": [("bold", "IMEI: "), ("regular", "{imei}")]},
        {"type": "text", "x": 58.1, "y": 14.0, "anchor": "r", "size": 4.7,
         "runs": [("bold", "Serial No"), ("regular", ": {serial}")]},
        # Fabricante
        {"type": "lines", "x": 3.3, "y": 16.3, "lead": 1.95, "size": 4.7, "style": "regular",
         "lines": ["Manufacturer: Worldsensing SL", "www.worldsensing.com", "Made in Spain"]},
    ]


def _power():
    return [
        # Conector y alimentación
        # Conector: la imagen trae debajo su propio texto ("Input Power...");
        # "top_block" se queda solo con el dibujo (corta por el hueco en blanco
        # más grande). Con una imagen que sea solo el conector, no hace nada.
        {"type": "asset", "name": "combox70_connector", "box": (26.8, 15.6, 12.0, 12.4),
         "align": "c", "crop": "top_block"},
        {"type": "text", "x": 26.6, "y": 29.2, "anchor": "l", "size": 4.7,
         "runs": [("regular", "Input Power, 10A")]},
        {"type": "text", "x": 26.6, "y": 31.4, "anchor": "l", "size": 4.7,
         "runs": [("regular", "13-26 VDC")]},
        # Símbolo de continua justo detrás de "13-26 VDC" (se calcula su posición)
        {"type": "dc_symbol", "after": ("regular", "13-26 VDC", 4.7), "x": 26.6,
         "gap": 0.8, "y": 31.4, "w": 3.2},
        # QR con el nº de serie
        {"type": "qr", "data": "{serial}", "x": 49.0, "y": 19.9, "size": 7.6},
    ]


def _ip_rating(x):
    return [
        {"type": "text", "x": x, "y": 42.9, "anchor": "l", "size": 9.8,
         "runs": [("bold", "IP66")]},
        {"type": "text", "x": x, "y": 45.9, "anchor": "l", "size": 9.8,
         "runs": [("bold", "IP67")]},
    ]


# --- EU: WS ComBox70 FX4-EU (Article 1030653) -----------------------------
TEMPLATE_EU = {
    "name": "EU",
    "description": "ComBox70 FX4-EU (1030653)",
    "offset": (0.0, -0.4),     # centrado en el rollo de 50 mm
    "fixed": {"product": PRODUCT_NAME, "model": "FX4-EU", "article": "1030653"},
    "elements": _header() + _power() + [
        {"type": "rbox", "box": (3.3, 40.5, 56.5, 7.4), "radius": 1.0, "line": 0.3},
        {"type": "asset", "name": "ce", "box": (4.3, 41.9, 6.2, 4.6), "align": "c"},
    ] + _ip_rating(12.0) + [
        {"type": "asset", "name": "ukca", "box": (21.6, 41.8, 4.9, 4.8), "align": "c"},
        {"type": "lines", "x": 27.0, "y": 42.85, "lead": 1.85, "size": 4.2, "style": "regular",
         "max_w": 23.4,
         "lines": ["Importer: Leica Geosystems Ltd.",
                   "Hexagon House, Michigan Drive,",
                   "Tongwell, Milton Keynes, MK15 8HT"]},
        {"type": "asset", "name": "weee", "box": (50.6, 40.8, 4.6, 6.9), "align": "c"},
        {"type": "asset", "name": "manual_info", "box": (55.4, 42.2, 4.2, 3.9), "align": "c"},
    ],
}


# --- ROW: WS ComBox70 FX4-ROW (Article 1030654) ---------------------------
TEMPLATE_ROW = {
    "name": "ROW",
    "description": "ComBox70 FX4-ROW (1030654)",
    "offset": (0.0, -0.4),     # centrado en el rollo de 50 mm
    # Nº de homologación ANATEL (Brasil). En el template aún es un marcador.
    "fixed": {"product": PRODUCT_NAME, "model": "FX4-ROW", "article": "1030654",
              "anatel": "AAAAA-BB-CCCCC"},
    "elements": _header() + _power() + [
        # Identificadores FCC / IC de los módulos de radio
        {"type": "lines", "x": 3.3, "y": 23.6, "lead": 1.52, "size": 3.6, "style": "regular",
         "max_w": 22.8,
         "lines": ["CONTAINS FCC ID XMR201903EG25G",
                   "CONTAINS IC ID: 10224A-201903EG25G",
                   "CONTAINS FCC ID 2AF6B-RAK5146",
                   "CONTAINS IC ID: 25908-RAK5146",
                   "CONTAINS FCC ID TLZ-CM358SM",
                   "CONTAINS IC ID: 6100A-CM358SM"]},
        # Declaración FCC parte 15
        {"type": "paragraph", "box": (3.7, 33.7, 55.4, 6.9), "size": 4.2, "style": "regular",
         "lead": 1.75,
         "text": ("This device complies with part 15 of the FCC Rules. Operation is subject "
                  "to the following two conditions: (1) This device may not cause harmful "
                  "interference, and (2) this device must accept any interference received, "
                  "including interference that may cause undesired operation.")},
        {"type": "rbox", "box": (3.3, 40.8, 56.5, 7.1), "radius": 1.0, "line": 0.3},
        {"type": "asset", "name": "fcc", "box": (3.8, 41.4, 6.6, 4.4), "align": "c"},
        {"type": "asset", "name": "anatel", "box": (10.8, 41.4, 6.6, 4.4), "align": "c"},
        {"type": "text", "x": 14.1, "y": 46.8, "anchor": "m", "size": 3.6,
         "runs": [("regular", "{anatel}")]},
        {"type": "asset", "name": "rcm", "box": (23.6, 41.5, 7.2, 5.9), "align": "c"},
    ] + _ip_rating(32.1) + [
        {"type": "asset", "name": "weee", "box": (40.1, 41.0, 4.6, 6.7), "align": "c"},
        {"type": "asset", "name": "manual_info", "box": (48.8, 42.2, 4.6, 3.9), "align": "c"},
    ],
}


TEMPLATES = {t["name"]: t for t in (TEMPLATE_EU, TEMPLATE_ROW)}

# Nombres de fichero aceptados para cada imagen.
# Sin extensión (.png/.svg/.jpg/.webp) y sin distinguir mayúsculas.
# Si guardas un fichero con otro nombre, basta con añadirlo a su lista.
ASSET_NAMES = {
    "ws_logo_black":      ["ws_logo_black", "ws_logo", "logo"],
    "ce":                 ["ce"],
    "ukca":               ["ukca"],
    "weee":               ["weee"],
    "manual_info":        ["manual_info", "manual", "info_manual"],
    "fcc":                ["fcc", "fcc_id"],
    "anatel":             ["anatel"],
    "rcm":                ["rcm", "regulatory_compliance_mark_aus"],
    "combox70_connector": ["combox70_connector", "connector",
                           "conector_thread_2", "conector_thread"],
}
