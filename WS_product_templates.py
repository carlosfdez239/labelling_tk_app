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
Campos fijos de cada variante ("fixed"): {product}, {commercial},
{article}, {anatel}. Si un texto usa un campo que no está en "fixed", la app avisa con
un error claro en lugar de fallar.

Tipos de elemento:
    asset      imagen encajada en 'box' (x, y, ancho, alto).
               Se le quita el margen blanco para que llene el hueco
               ("trim": False lo desactiva; "trim": "ink" recorta por la tinta
               que se imprime, ignorando fondos o marcos gris claro). "crop": (izq, arriba, der, abajo)
               en fracciones 0..1 para quedarse con una parte de la imagen,
               o "top_block" para quedarse con el dibujo de arriba y quitar
               el texto que venga debajo separado por un hueco en blanco.
    text       una línea; 'runs' = [(estilo, texto), ...] para mezclar
               negrita y normal; 'anchor' l/m/r; y = línea media del texto
    lines      varias líneas con el mismo estilo; 'lead' = interlineado mm
    paragraph  texto que se reparte en líneas dentro de 'box'; si no cabe,
               reduce el tamaño
    rbox       recuadro con esquinas redondeadas
    hline      línea horizontal desde (x, y) de ancho 'w' y grosor 'line' (mm)
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

# Rev. 13/11/2026: maquetación según el documento de diseño WS
# "FusionX4 EU (FX4-EU & FX4-ROW)". Medidas tomadas del documento:
#   - cabecera: logo WS a la izquierda y 5 líneas de datos a la derecha
#     (sin la línea separadora del documento, eliminada a petición)
#   - conector centrado con "Input Power, 10A / 13-26 VDC" y QR (7,6 mm, como Leica)
#   - ROW: declaración FCC parte 15 (sin las líneas "CONTAINS FCC/IC ID")
#   - recuadro inferior con los logos de cumplimiento
# Cambios respecto al documento: IP67 eliminado (solo IP66), y en ROW se
# mantiene el logo FCC.

HEADER_X = 60.6          # borde derecho del bloque de datos
HEADER_PT = 4.9
HEADER_Y0, HEADER_LEAD = 2.85, 2.19


def _header():
    rows = [
        [("bold", "Product"), ("regular", ": {product}")],
        [("bold", "Commercial Part No"), ("regular", ": {commercial}")],
        [("bold", "Article No"), ("regular", ": {article}")],
        [("bold", "IMEI"), ("regular", ": {imei}")],
        [("bold", "Serial No"), ("regular", ": {serial}")],
    ]
    els = [{"type": "asset", "name": "ws_logo_black", "box": (1.7, 5.5, 24.7, 5.1), "align": "l"}]
    for i, runs in enumerate(rows):
        els.append({"type": "text", "x": HEADER_X, "y": HEADER_Y0 + i * HEADER_LEAD,
                    "anchor": "r", "size": HEADER_PT, "runs": runs})
    # Línea separadora bajo la cabecera: eliminada (13/11/2026). Para
    # recuperarla, descomentar:
    # els.append({"type": "hline", "x": 1.0, "y": 16.05, "w": 60.5, "line": 0.4})
    return els


def _power():
    return [
        # Conector: la imagen trae debajo su propio texto ("Input Power...");
        # "top_block" se queda solo con el dibujo.
        {"type": "asset", "name": "combox70_connector", "box": (28.0, 16.8, 10.7, 10.6),
         "align": "c", "crop": "top_block"},
        {"type": "text", "x": 33.15, "y": 28.95, "anchor": "m", "size": 4.7,
         "runs": [("regular", "Input Power, 10A")]},
        {"type": "text", "x": 27.1, "y": 31.35, "anchor": "l", "size": 4.7,
         "runs": [("regular", "13-26 VDC")]},
        {"type": "dc_symbol", "after": ("regular", "13-26 VDC", 4.7), "x": 27.1,
         "gap": 0.8, "y": 31.35, "w": 3.2},
        # QR con el nº de serie
        # Mismo tamaño que en Leica (7,6 mm), centrado donde estaba el del
        # documento WS (13/11/2026)
        {"type": "qr", "data": "{serial}", "x": 49.2, "y": 20.9, "size": 7.6},
    ]


def _ip66(x):
    # Solo IP66: IP67 anulado en todas las variantes (13/11/2026).
    return [{"type": "text", "x": x, "y": 45.0, "anchor": "l", "size": 9.8,
             "runs": [("bold", "IP66")]}]


def _bottom_box():
    return [{"type": "rbox", "box": (1.8, 41.2, 59.9, 7.6), "radius": 1.0, "line": 0.4}]


# --- EU: WS FX4-EU -----------------------------------------------------------
TEMPLATE_EU = {
    "name": "EU",
    "description": "FusionX4 FX4-EU",
    "offset": (0.0, 0.0),
    # Valores tal como aparecen en el documento de diseño
    "fixed": {"product": "FX4-EU", "commercial": "FX4-EU", "article": "FX4-EU"},
    "elements": _header() + _power() + _bottom_box() + [
        {"type": "asset", "name": "ce", "box": (2.2, 43.1, 6.5, 4.6), "align": "c"},
        {"type": "asset", "name": "ukca", "box": (9.9, 42.8, 4.7, 4.7), "align": "c"},
    ] + _ip66(16.6) + [
        {"type": "asset", "name": "weee", "box": (47.6, 42.1, 4.5, 6.2), "align": "c"},
        # Icono del manual: misma caja que en Leica (4,9 x 5,0 mm), centrado
        # en el recuadro inferior (13/11/2026)
        {"type": "asset", "name": "manual_info", "box": (55.1, 42.5, 4.9, 5.0), "align": "c", "trim": "ink"},
    ],
}


# --- ROW: WS FX4-ROW ---------------------------------------------------------
TEMPLATE_ROW = {
    "name": "ROW",
    "description": "FusionX4 FX4-ROW",
    "offset": (0.0, 0.0),
    # Nº de homologación ANATEL (Brasil). En el documento aún es un marcador.
    "fixed": {"product": "FX4-ROW", "commercial": "FX4-ROW", "article": "FX4-ROW",
              "anatel": "AAAAA-BB-CCCCC"},
    "elements": _header() + _power() + [
        # Declaración FCC parte 15
        {"type": "paragraph", "box": (3.0, 33.0, 57.6, 7.8), "size": 4.2, "style": "regular",
         "lead": 1.75,
         "text": ("This device complies with part 15 of the FCC Rules. Operation is subject "
                  "to the following two conditions: (1) This device may not cause harmful "
                  "interference, and (2) this device must accept any interference received, "
                  "including interference that may cause undesired operation.")},
    ] + _bottom_box() + [
        # Logo FCC: se mantiene porque ROW no lleva las líneas "CONTAINS FCC ID"
        {"type": "asset", "name": "fcc", "box": (2.8, 41.8, 6.3, 5.8), "align": "c"},
        {"type": "asset", "name": "anatel", "box": (10.6, 41.6, 6.0, 5.0), "align": "c"},
        {"type": "text", "x": 13.6, "y": 47.7, "anchor": "m", "size": 3.6,
         "runs": [("regular", "{anatel}")]},
        {"type": "asset", "name": "rcm", "box": (23.9, 42.4, 7.5, 5.6), "align": "c"},
    ] + _ip66(33.0) + [
        {"type": "asset", "name": "weee", "box": (41.7, 41.6, 4.4, 6.3), "align": "c"},
        # Icono del manual: misma caja que en Leica (4,9 x 5,0 mm) (13/11/2026)
        {"type": "asset", "name": "manual_info", "box": (51.6, 42.5, 4.9, 5.0), "align": "c", "trim": "ink"},
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
