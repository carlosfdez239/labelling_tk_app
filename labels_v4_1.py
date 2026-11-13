'''
C. Fdez
Rev 3.0 --> 16/03/2026
- Nueva funcionalidad: Generación manual de etiquetas para Dispositivos y Accesorios.
- Integración de campo 'BRAND'.
- Uso de Logo PNG en cabecera y optimización de fuentes Rubik.
- Ajuste de DataMatrix dinámico según modo.

Rev 3.1 --> 20/06/2026
- Corrección de errores en la generación de etiquetas para Accesorios. Al seleccionar un número de serie en cualquier modo,
se generaba una etiqueta y se mostraba en todos los modos.
- Se incorpora un nuevo modo --> "etiqueta Chile", las dimensiones serán 62mm x 62mm ubicando únicamente la imagen images/chile.png
  centrada en la etiqueta. En este modo, el operario podrá indicar el número de copias a imprimir. Se mostrará igualmente la
  previsualización de la etiqueta y tras pulsar sobre el botón "IMPRIMIR", se enviará a la impresora el número de copias indicado
  y se generará el png correspondiente en la carpeta de salida.

Rev 3.1.1 --> 24/07/2026
- Refactor completo: panel de logs en tiempo real en la parte inferior de la ventana.
- Manejo de errores centralizado (sin popups crípticos tipo "stack overflow").
- Fix: bug de tamaño de DataMatrix (libdmtx) fijando size='36x36' en ambas funciones de etiqueta.
- Fix: en modo 1 (Archivo) se intercambiaban los campos MODEL y PN al llamar a Impr_Node_packaging_label.
- Fix: validación de datos antes de generar el DataMatrix (evita datos vacíos o placeholder "N/A").
- Fix: eliminado el UnboundLocalError que podía producirse en modo 1 si fallaba la generación de imagen.

Rev 3.1.2 --> 22/09/2026
- Incluido Modo Baterias (Product / LOT / Expiration Date) con su propia etiqueta.
- Fix: SyntaxError en switch_view (elif mode == 5 mal colocado tras logger.debug).
- Fix: SyntaxError/IndentationError en display_label (elif mode == 5 con sangrado incorrecto).
- Fix: declarada la variable manual_expire que faltaba.
- Fix: construcción de datam y llamada a la función correcta en el modo Baterías.

Rev 4.0 --> 02/10/2026
- Nuevo modo LEICA (6): etiqueta de packaging 75x50 mm según DOC-0003950 Rev D
  (generador en leica_label.py, que debe estar en la misma carpeta).
- IMPRIMIR regenera siempre la etiqueta con los datos actuales del formulario
  (antes se imprimía el último PNG guardado, que podía ser de otro modo).
- Impresión con subprocess: se detectan los errores de lp y las copias se
  envían con '-n' en un único trabajo.
- config.json se busca junto al script, no en el directorio de trabajo.
- El modo 4 (Chile) ya no es el 'else' por defecto de display_label.
- OUTPUT_DIR ya no está fijo en ~/Documentos: por defecto es la carpeta del
  script (configurable con "OUTPUT_DIR" en config.json) y se crea si no existe.
- Nuevo modo LEICA PRODUCTO (7): etiqueta de producto ComBox70 63x50 mm
  (rollo de 50 mm), con
  un template por variante (EU / ROW) en leica_product_templates.py y el
  dibujo en leica_product_label.py. QR con el nº de serie (pip install qrcode)
  y validación del IMEI (dígito de control).
- Calibración de posición en la QL: LEICA_QL_SHIFT_MM / LEICA_PRODUCT_QL_SHIFT_MM
  ([derecha, arriba] en mm). Conector de producto ampliado y recortable
  (LEICA_CONNECTOR_CROP).
- Leica en Brother QL-820NWB: la etiqueta se gira, se pasa a 1 bit y se envía
  a 300 dpi sin reescalar. Impresión directa con brother_ql (LEICA_QL_PRINTER)
  o por CUPS con ppi=300. Rollo por defecto: 50 mm (DK-22223), recortando
  solo el margen blanco hasta el ancho imprimible (46,9 mm), sin reescalar.

Rev 4.1 --> 10/10/2026
- Fix: en la etiqueta de producto, el símbolo de corriente continua (DC) se
  colocaba detrás del texto "DC" en lugar de delante.
- Se crea nuevas templates de producto para las variantes ROW y EU, con el logo de WorldSensing en la cabecera
- Nuevo modo WS PRODUCTO (8): usa WS_product_label.py / WS_product_templates.py
  (antes llamaba por error al generador de Leica). Imágenes buscadas en
  WS_PRODUCT_ASSETS_DIR, images/ws, images/leica e images.
- Fix: el template WS usaba el campo {product} sin definirlo (KeyError).
- Fix: impresión directa con LEICA_QL_PRINTER = "http://IP" fallaba con
  "No such file or directory". Ahora se acepta IP, http://, tcp:// o /dev/usb/lpX
  y se convierte a lo que espera brother_ql (tcp://IP:9100, backend network).
- Brillo y contraste de la QL en config.json: LEICA_QL_BRIGHTNESS y
  LEICA_QL_CONTRAST (1.0 = sin cambio). Se releen en cada impresión, no hace
  falta reiniciar la app. El bitmap enviado se guarda en output_ql_bitmap.png.
- Los modos 6, 7 y 8 imprimen con WS_label.print_brother_ql.
- Etiquetas de producto (7 y 8) en Zebra ZD621 300 dpi: si ZEBRA_PRINTER está
  definido se envían en ZPL raw (cola CUPS, IP o /dev/usb/lpX) a 12 p/mm, a
  tamaño exacto. Ajustes en config.json: ZEBRA_DARKNESS (^MD), ZEBRA_SPEED
  (^PR), ZEBRA_BRIGHTNESS, ZEBRA_CONTRAST, ZEBRA_ROTATE, ZEBRA_SHIFT_MM.
  El ZPL enviado se guarda en output_zebra.zpl y su bitmap en output_zebra_bitmap.png.
- LEICA_QL_PRINTER con un nombre de cola CUPS da un error claro.

Rev 4.1.1 --> 13/11/2026
- Resolución de la Zebra configurable en config.json con ZEBRA_DPI
  (203, 300 o 600). Se convierte a la densidad ZPL (8, 12 o 24 p/mm) y se
  relee en cada impresión, igual que darkness o velocidad.
- ZEBRA_DPMM sigue funcionando como antes si ZEBRA_DPI no está definido.
  Si están los dos, manda ZEBRA_DPI.
- La resolución usada se muestra en el registro al arrancar y en cada impresión.
- Elementos ocultables en las etiquetas de producto (Leica y WS, EU y ROW)
  con PRODUCT_HIDE_ELEMENTS en config.json, p. ej. ["ip67"]. Se quita todo
  elemento del template cuyo nombre, texto o imagen contenga ese término
  (sin distinguir mayúsculas). Los elementos quitados se listan en el registro
  al arrancar; si un término no coincide con nada, se avisa.
- Fix: PRODUCT_HIDE_ELEMENTS no encontraba los textos de tipo 'text' (están
  dentro de 'runs', en tuplas). Ahora busca en toda la estructura del elemento.
- IP67 eliminado de todas las etiquetas de producto (Leica y WS, EU y ROW)
  directamente en los templates; IP66 queda centrado en el recuadro.
- Etiquetas de producto en Zebra: se dibujan directamente a la resolución de
  la impresora (ZEBRA_DPI) en vez de a 300 dpi y reescalar. A 203 dpi el texto
  pequeño, el QR y los logos salen nítidos. La vista previa muestra
  exactamente el bitmap que se imprime.

'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import openpyxl
import logging
import os
import subprocess
import json
import datetime
from screeninfo import get_monitors
from pylibdmtx.pylibdmtx import encode
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk as IMG
import leica_label
import leica_product_label as leica_product
import WS_product_label as ws_product
import WS_label

# =========================================================================
# CONFIGURACIÓN
# =========================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
# Avisos de configuración: se vuelcan al registro cuando ya existe el logger
CONFIG_WARNINGS = []
# Mensajes informativos de configuración (se vuelcan al registro al arrancar)
CONFIG_INFO = []

def load_config(file_path=CONFIG_PATH):
    if not os.path.exists(file_path):
        CONFIG_WARNINGS.append(f"No existe {file_path}: se usan valores por defecto.")
        return {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        CONFIG_WARNINGS.append(f"config.json tiene un error de formato (línea {e.lineno}, "
                               f"columna {e.colno}): {e.msg}. SE IGNORA TODA LA CONFIGURACIÓN.")
        return {}
    except Exception as e:
        CONFIG_WARNINGS.append(f"No se pudo leer config.json: {e}")
        return {}


def save_config_key(key, value, file_path=CONFIG_PATH):
    """Guarda una clave en config.json conservando el resto del fichero."""
    data = {}
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)            # si tiene errores, mejor fallar que machacarlo
    data[key] = value
    tmp = file_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, file_path)

config = load_config()
IMPRESORA = config.get("IMPRESORA", "")
DIRECTORIO_LOGO = config.get("DIRECTORIO_LOGO", "")
BATCH_N = config.get("batch", "")
LEICA_PRINTER = config.get("LEICA_PRINTER", IMPRESORA)
# Impresión Leica en la Brother QL-820NWB.
# Si LEICA_QL_PRINTER está definido se imprime directo (brother_ql, sin CUPS):
#   "tcp://192.168.1.50" (red) o "file:///dev/usb/lp0" (USB)
# Si no, se usa CUPS con la imagen ya girada y en 1 bit.
LEICA_QL_PRINTER = config.get("LEICA_QL_PRINTER", "")
LEICA_QL_MODEL = config.get("LEICA_QL_MODEL", "QL-820NWB")
LEICA_QL_TAPE = config.get("LEICA_QL_TAPE", "50")          # "50" (DK-22223), "62" o "62red"
LEICA_QL_ROTATE = int(config.get("LEICA_QL_ROTATE", 90))  # 90 o 270 según cómo la quieras salir
LEICA_QL_THRESHOLD = int(config.get("LEICA_QL_THRESHOLD", 128))
# Blanco a quitar en cada extremo del largo. Sin definir = automático en
# impresión directa (compensa el avance de la impresora: 75 mm exactos).
_trim = config.get("LEICA_QL_TRIM_MM")
LEICA_QL_TRIM_MM = None if _trim in (None, "", "auto") else float(_trim)
LEICA_LP_OPTIONS = config.get("LEICA_LP_OPTIONS", ["-o", "PageSize=50X1", "-o", "ppi=300"])
LEICA_FONT_BOLD = config.get("LEICA_FONT_BOLD")
LEICA_FONT_ITALIC = config.get("LEICA_FONT_ITALIC")
# Etiqueta de producto (63x50 mm): en el mismo rollo de 50 mm que la de
# packaging; los 50 mm de alto van a lo ancho del rollo.
LEICA_PRODUCT_QL_TAPE = config.get("LEICA_PRODUCT_QL_TAPE", "50")
LEICA_PRODUCT_LP_OPTIONS = config.get("LEICA_PRODUCT_LP_OPTIONS", ["-o", "PageSize=50X1", "-o", "ppi=300"])
LEICA_PRODUCT_FONT_REGULAR = config.get("LEICA_PRODUCT_FONT_REGULAR")
LEICA_PRODUCT_FONT_BOLD = config.get("LEICA_PRODUCT_FONT_BOLD")


# Brillo y contraste de la QL (1.0 = sin cambio). La QL imprime en 1 bit:
# brillo < 1 o contraste > 1 = trazo más grueso/oscuro; brillo > 1 o
# contraste < 1 = más fino/claro. Rango útil 0.6 a 1.4.
# Se releen de config.json en cada impresión para poder ajustar sin reiniciar.
def ql_tone(prefix="LEICA_QL"):
    """Devuelve (brillo, contraste) actuales de config.json.
    prefix: "LEICA_QL" (Brother) o "ZEBRA"."""
    cfg = load_config() if os.path.exists(CONFIG_PATH) else {}
    out = []
    for key in (f"{prefix}_BRIGHTNESS", f"{prefix}_CONTRAST"):
        v = cfg.get(key, 1.0)
        try:
            out.append(WS_label._check_tone(key, 1.0 if v in (None, "") else v))
        except ValueError as e:
            raise LabelError(f"config.json: {e}") from None
    return tuple(out)


# Zebra ZD621 300 dpi para las etiquetas de producto (modos 7 y 8).
# Si ZEBRA_PRINTER está vacío, el producto se sigue imprimiendo en la QL.
#   "ZEBRA_PRINTER": "Zebra_Thread_Selcimat"   (cola CUPS, IP o /dev/usb/lp0)
ZEBRA_PRINTER = config.get("ZEBRA_PRINTER", "")
# Resolución: "ZEBRA_DPI": 203, 300 o 600 (ZD621 = 300). Por compatibilidad
# se acepta también "ZEBRA_DPMM" (8, 12 o 24) si ZEBRA_DPI no está definido.
ZEBRA_DPI_TO_DPMM = {203: 8, 300: 12, 600: 24}
ZEBRA_DEFAULT_DPI = 300


def zebra_resolution(cfg=None):
    """Devuelve (dpi, dpmm) de la Zebra según config.json.
    Lanza LabelError si el valor no es una resolución válida."""
    if cfg is None:
        cfg = load_config() if os.path.exists(CONFIG_PATH) else {}
    dpi_raw = cfg.get("ZEBRA_DPI")
    dpmm_raw = cfg.get("ZEBRA_DPMM")
    if dpi_raw not in (None, ""):
        try:
            dpi = int(float(dpi_raw))
        except (TypeError, ValueError):
            dpi = None
        if dpi not in ZEBRA_DPI_TO_DPMM:
            raise LabelError(f"config.json: ZEBRA_DPI no válido ({dpi_raw!r}). "
                             f"Valores admitidos: {sorted(ZEBRA_DPI_TO_DPMM)}")
        return dpi, ZEBRA_DPI_TO_DPMM[dpi]
    if dpmm_raw not in (None, ""):
        dpmm_to_dpi = {v: k for k, v in ZEBRA_DPI_TO_DPMM.items()}
        try:
            dpmm = int(float(dpmm_raw))
        except (TypeError, ValueError):
            dpmm = None
        if dpmm not in dpmm_to_dpi:
            raise LabelError(f"config.json: ZEBRA_DPMM no válido ({dpmm_raw!r}). "
                             f"Valores admitidos: {sorted(dpmm_to_dpi)}")
        return dpmm_to_dpi[dpmm], dpmm
    return ZEBRA_DEFAULT_DPI, ZEBRA_DPI_TO_DPMM[ZEBRA_DEFAULT_DPI]


ZEBRA_ROTATE = int(config.get("ZEBRA_ROTATE", 0))          # 0, 90, 180 o 270
ZEBRA_THRESHOLD = int(config.get("ZEBRA_THRESHOLD", 128))


def zebra_settings():
    """Ajustes de la Zebra que se releen en cada impresión."""
    cfg = load_config() if os.path.exists(CONFIG_PATH) else {}
    brillo, contraste = ql_tone("ZEBRA")
    return {"brightness": brillo, "contrast": contraste,
            "darkness": cfg.get("ZEBRA_DARKNESS"), "speed": cfg.get("ZEBRA_SPEED")}


# Modos que se imprimen en la Brother QL y su tipo de etiqueta
QL_MODES = (6, 7, 8)            # 6 Leica packaging, 7 Leica producto, 8 WS producto
QL_PRODUCT_MODES = (7, 8)       # 63 x 50 mm

# Calibración de posición en la QL (solo impresión directa), en mm medidos
# sobre la etiqueta impresa: [derecha, arriba]. Positivo = mover a la derecha /
# hacia arriba. La de producto, si no se define, usa la de packaging.
def _shift(key, default=(0.0, 0.0)):
    v = config.get(key)
    try:
        return (float(v[0]), float(v[1])) if v else tuple(default)
    except (TypeError, ValueError, IndexError):
        CONFIG_WARNINGS.append(f"{key} no válido ({v!r}); se usa {list(default)}")
        return tuple(default)
LEICA_QL_SHIFT_MM = _shift("LEICA_QL_SHIFT_MM")
LEICA_PRODUCT_QL_SHIFT_MM = _shift("LEICA_PRODUCT_QL_SHIFT_MM", LEICA_QL_SHIFT_MM)
ZEBRA_SHIFT_MM = _shift("ZEBRA_SHIFT_MM")

# Recorte de la imagen del conector. Por defecto es automático ("top_block":
# quita el texto que la imagen trae debajo). En config.json se puede forzar
# [izq, arriba, der, abajo] en fracciones, o "none" para no recortar.
_crop = config.get("LEICA_CONNECTOR_CROP")
if _crop not in (None, ""):
    try:
        if isinstance(_crop, str):
            _crop = None if _crop.lower() == "none" else _crop
        else:
            _crop = tuple(float(x) for x in _crop)
        for _tpl in list(leica_product.TEMPLATES.values()) + list(ws_product.TEMPLATES.values()):
            for _el in _tpl["elements"]:
                if _el.get("name") == "combox70_connector":
                    _el["crop"] = _crop
    except (TypeError, ValueError):
        CONFIG_WARNINGS.append(f"LEICA_CONNECTOR_CROP no válido ({_crop!r}); se usa el recorte automático")

# Elementos a ocultar en TODAS las etiquetas de producto (Leica y WS, EU y
# ROW). En config.json: "PRODUCT_HIDE_ELEMENTS": ["ip67"]. Se quita cada
# elemento cuyo nombre o cualquier valor de texto (texto, ruta de imagen...)
# contenga el término, sin distinguir mayúsculas. Lista vacía = no se oculta nada.
def _element_matches(el, term):
    """True si el término aparece en cualquier texto del elemento, a cualquier
    profundidad (nombre, 'runs' [(estilo, texto)], 'lines', rutas...)."""
    if isinstance(el, str):
        return term in el.lower()
    if isinstance(el, dict):
        return any(_element_matches(v, term) for v in el.values())
    if isinstance(el, (list, tuple)):
        return any(_element_matches(v, term) for v in el)
    return False


def _hide_product_elements(terms):
    if isinstance(terms, str):
        terms = [terms]
    if not isinstance(terms, (list, tuple)):
        CONFIG_WARNINGS.append(f"PRODUCT_HIDE_ELEMENTS no válido ({terms!r}); debe ser una lista de textos")
        return
    terms = [str(t).strip().lower() for t in terms if str(t).strip()]
    if not terms:
        return
    found = {t: 0 for t in terms}
    for marca, templates in (("Leica", leica_product.TEMPLATES), ("WS", ws_product.TEMPLATES)):
        for variante, tpl in templates.items():
            kept, removed = [], []
            for el in tpl["elements"]:
                hit = next((t for t in terms if _element_matches(el, t)), None)
                if hit:
                    found[hit] += 1
                    removed.append(el.get("name", "<sin nombre>"))
                else:
                    kept.append(el)
            tpl["elements"][:] = kept
            if removed:
                CONFIG_INFO.append(f"Producto {marca} {variante}: ocultos {removed} (PRODUCT_HIDE_ELEMENTS)")
    for t, n in found.items():
        if n == 0:
            CONFIG_WARNINGS.append(f"PRODUCT_HIDE_ELEMENTS: '{t}' no coincide con ningún elemento de los templates")


_hide_product_elements(config.get("PRODUCT_HIDE_ELEMENTS", []))
# Tamaños del texto pequeño de la etiqueta Leica (pt). Si no se definen, se
# usan los del plano (5 / 4 / 5). Si no caben, se reducen solos y se avisa.
for _key, _attr in (("LEICA_ADDRESS_PT", "ADDRESS_PT"),
                    ("LEICA_IMPORTER_PT", "IMPORTER_PT"),
                    ("LEICA_MADE_IN_PT", "MADE_IN_PT")):
    if config.get(_key) not in (None, ""):
        setattr(leica_label, _attr, float(config[_key]))

# Rutas candidatas para la fuente Rubik, en orden de preferencia:
# 1) lo indicado en config.json, 2) instalación de sistema típica en Ubuntu,
# 3) copia local del usuario (entornos de desarrollo antiguos).
_FONT_CANDIDATES = [
    config.get("font_path"),
    config.get("Rubik_font_path"),
    "/usr/share/fonts/truetype/Rubik/Rubik-Light.ttf",
    os.path.expanduser("~/.local/share/fonts/Rubik-Light.ttf"),
    os.path.join(BASE_DIR, "Rubik-Light.ttf"),
    os.path.join(BASE_DIR, "fonts", "Rubik-Light.ttf"),
]
RUBIK_FONT_PATH = next((p for p in _FONT_CANDIDATES if p and os.path.isfile(p)), None)

DATAMATRIX_SIZE = "36x36"  # Tamaño fijo para evitar el bug de auto-sizing de libdmtx
# Carpeta de trabajo (salida de PNG e imágenes). Por defecto, la del propio
# script; se puede fijar otra con "OUTPUT_DIR" en config.json.
OUTPUT_DIR = os.path.expanduser(config.get("OUTPUT_DIR") or BASE_DIR)
os.makedirs(OUTPUT_DIR, exist_ok=True)
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")
LEICA_ASSETS_DIR = config.get("LEICA_ASSETS_DIR", os.path.join(IMAGES_DIR, "leica"))
# Etiqueta de producto WS: cada imagen se toma de la primera carpeta en la que
# esté (así se reutilizan las marcas CE/UKCA/WEEE... de la carpeta de Leica).
WS_PRODUCT_ASSETS_DIR = [d for d in (config.get("WS_PRODUCT_ASSETS_DIR"),
                                     os.path.join(IMAGES_DIR, "ws"),
                                     LEICA_ASSETS_DIR, IMAGES_DIR) if d]

# Tamaño máximo del área de previsualización en pantalla (no afecta al archivo
# real generado, que siempre se guarda a resolución completa para imprimir).
PREVIEW_MAX_WIDTH = 640
PREVIEW_MAX_HEIGHT = 440


# =========================================================================
# LOGGING — consola + panel visual en la ventana principal
# =========================================================================

class TkTextHandler(logging.Handler):
    """Vuelca los logs a un widget Text de Tkinter, coloreado por nivel."""

    TAG_COLORS = {
        "DEBUG": "#8a8a8a",
        "INFO": "#1e824c",
        "WARNING": "#b8860b",
        "ERROR": "#c0392b",
        "CRITICAL": "#c0392b",
    }

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        for level, color in self.TAG_COLORS.items():
            self.text_widget.tag_configure(level, foreground=color)

    def emit(self, record):
        msg = self.format(record)
        try:
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", msg + "\n", record.levelname)
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        except tk.TclError:
            # La ventana puede haberse cerrado ya
            pass


logger = logging.getLogger("WSLabelling")
logger.setLevel(logging.DEBUG)

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(_console_handler)


class LabelError(Exception):
    """Excepción propia para fallos de generación de etiqueta, con mensaje ya listo para el usuario."""
    pass


# =========================================================================
# LÓGICA DE GENERACIÓN DE ETIQUETA
# =========================================================================

def Crear_Batch():
    fecha = datetime.datetime.today().strftime("%Y%m%d")
    return fecha + BATCH_N


def _validar_datam(datam, contexto=""):
    """Evita codificar datos vacíos o placeholder, que pueden disparar
    el bug de auto-sizing de libdmtx (stack overflow interno)."""
    limpio = datam.replace(";", "").strip().upper()
    valores_invalidos = {"", "N/A", "N/AN/A", "N/AN/AN/A"}
    if limpio in valores_invalidos:
        raise LabelError(
            f"Faltan datos para generar el DataMatrix{(' en ' + contexto) if contexto else ''}. "
            f"Verifica que los campos estén rellenos (o pulsa 'Buscar' primero)."
        )


def _encode_datamatrix(datam, contexto=""):
    _validar_datam(datam, contexto)
    logger.debug(f"Codificando DataMatrix ({contexto}): {datam!r}")
    try:
        return encode(datam.encode("utf8"), size=DATAMATRIX_SIZE)
    except Exception as e:
        logger.error(f"Fallo al generar DataMatrix ({contexto}) con datam={datam!r}: {e}")
        raise LabelError(f"No se pudo generar el DataMatrix: {e}") from e


def _validar_datam_bateria(datam, contexto="Batería"):
    """Validación específica de baterías. Independiente de _validar_datam:
    aquí el DataMatrix solo lleva Product y LOT, así que se comprueba que
    ninguno de esos campos esté vacío o sea placeholder."""
    partes = [p.strip().upper() for p in datam.split(";")]
    if not partes or any(p in ("", "N/A") for p in partes):
        raise LabelError(
            f"Faltan datos para generar el DataMatrix en {contexto}. "
            f"Verifica que 'Product' y 'LOT' estén rellenos."
        )


def _encode_datamatrix_bateria(datam, contexto="Batería"):
    """Codificador de DataMatrix INDEPENDIENTE para baterías.
    No toca _encode_datamatrix ni la validación del resto de modos.
    Nota: 'datam' debe contener solo Product;LOT (sin fecha de caducidad)."""
    _validar_datam_bateria(datam, contexto)
    logger.debug(f"Codificando DataMatrix ({contexto}): {datam!r}")
    try:
        return encode(datam.encode("utf8"), size=DATAMATRIX_SIZE)
    except Exception as e:
        logger.error(f"Fallo al generar DataMatrix ({contexto}) con datam={datam!r}: {e}")
        raise LabelError(f"No se pudo generar el DataMatrix: {e}") from e


def _cargar_fuentes():
    if not RUBIK_FONT_PATH:
        logger.warning("No hay ninguna fuente Rubik disponible, usando fuente por defecto")
        return ImageFont.load_default(), ImageFont.load_default()
    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
        return font_main, font_small
    except Exception as e:
        logger.warning(f"No se pudo cargar la fuente Rubik en '{RUBIK_FONT_PATH}' ({e}), usando fuente por defecto")
        return ImageFont.load_default(), ImageFont.load_default()

def _pegar_logo(label, draw, mm_to_px, font_main):
    logo_path = os.path.join(IMAGES_DIR, "W_Label_Devices_new.png")
    try:
        logo = Image.open(logo_path).resize((int(42 * mm_to_px), int(8 * mm_to_px)))
        label.paste(logo, (0, 0))
    except Exception as e:
        logger.warning(f"No se pudo cargar el logo ({logo_path}): {e}. Usando texto de respaldo.")
        draw.text((2 * mm_to_px, 2 * mm_to_px), "WORLDSENSING", font=font_main, fill="black")

def Impr_Node_packaging_label(datam, Model, Brand, ERP_Code, Serial_N, Batch):
    mm_to_px = 11.81  # 300 DPI
    width = int(50 * mm_to_px)
    height = int(45 * mm_to_px)

    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    font_main, font_small = _cargar_fuentes()

    _pegar_logo(label, draw, mm_to_px, font_main)
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    y_pos = 14 * mm_to_px
    spacing = 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 3), f"SERIAL NUMBER:  {Serial_N}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 4), f"BATCH NUMBER:  {Batch}", font=font_main, fill="black")

    encoded = _encode_datamatrix(datam, contexto="Dispositivo")
    dmtx = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    dmtx = dmtx.resize((int(13 * mm_to_px), int(13 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))

    icon_path = os.path.join(DIRECTORIO_LOGO, "iconos.png")
    try:
        icons = Image.open(icon_path)
        label.paste(icons, (int(34 * mm_to_px), int(24 * mm_to_px)))
    except Exception as e:
        logger.warning(f"No se pudieron cargar los iconos regulatorios ({icon_path}): {e}")

    output_path = os.path.join(OUTPUT_DIR, "output_test2.png")
    label.save(output_path)
    logger.info(f"Etiqueta de dispositivo generada correctamente -> {output_path}")
    return output_path

def Impr_Node_packaging_label_Peru(datam, Model, ERP_Code, Serial_N, Batch):
    mm_to_px = 11.81  # 300 DPI
    width = int(50 * mm_to_px)
    height = int(45 * mm_to_px)

    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    font_main, font_small = _cargar_fuentes()

    _pegar_logo(label, draw, mm_to_px, font_main)
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    y_pos = 14 * mm_to_px
    spacing = 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    #draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing ), f"PN:  {ERP_Code}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"SERIAL NUMBER:  {Serial_N}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 3), f"BATCH NUMBER:  {Batch}", font=font_main, fill="black")

    encoded = _encode_datamatrix(datam, contexto="Dispositivo")
    dmtx = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    dmtx = dmtx.resize((int(13 * mm_to_px), int(13 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))

    icon_path = os.path.join(DIRECTORIO_LOGO, "iconos.png")
    try:
        icons = Image.open(icon_path)
        label.paste(icons, (int(34 * mm_to_px), int(24 * mm_to_px)))
    except Exception as e:
        logger.warning(f"No se pudieron cargar los iconos regulatorios ({icon_path}): {e}")

    output_path = os.path.join(OUTPUT_DIR, "output_test2.png")
    label.save(output_path)
    logger.info(f"Etiqueta de dispositivo generada correctamente -> {output_path}")
    return output_path

def Impr_Acc_packaging_label(datam, Model, ERP_Code):
    mm_to_px = 11.81
    width = int(50 * mm_to_px)
    height = int(45 * mm_to_px)

    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    font_main, font_small = _cargar_fuentes()

    _pegar_logo(label, draw, mm_to_px, font_main)
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    y_pos = 14 * mm_to_px
    spacing = 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")

    encoded = _encode_datamatrix(datam, contexto="Accesorio")
    dmtx = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    dmtx = dmtx.resize((int(13 * mm_to_px), int(13 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))

    icon_path = os.path.join(DIRECTORIO_LOGO, "iconos.png")
    try:
        icons = Image.open(icon_path)
        label.paste(icons, (int(34 * mm_to_px), int(24 * mm_to_px)))
    except Exception as e:
        logger.warning(f"No se pudieron cargar los iconos regulatorios ({icon_path}): {e}")

    output_path = os.path.join(OUTPUT_DIR, "output_test2.png")
    label.save(output_path)
    logger.info(f"Etiqueta de accesorio generada correctamente -> {output_path}")
    return output_path


def Impr_Bateria_label(datam, Product, LOT, Expiration_Date):
    """Etiqueta de baterías: Product / LOT / Expiration Date + DataMatrix.
    Mismo lienzo y estilo que las demás (50x45 mm @ 300 DPI)."""
    mm_to_px = 11.81
    width = int(50 * mm_to_px)
    height = int(45 * mm_to_px)

    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    font_main, font_small = _cargar_fuentes()

    _pegar_logo(label, draw, mm_to_px, font_main)
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    y_pos = 14 * mm_to_px
    spacing = 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"PRODUCT:  {Product}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"LOT:  {LOT}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"EXP. DATE:  {Expiration_Date}", font=font_main, fill="black")

    # El DataMatrix de baterías NO incluye la fecha de caducidad: solo Product;LOT.
    encoded = _encode_datamatrix_bateria(datam, contexto="Batería")
    dmtx = Image.frombytes("RGB", (encoded.width, encoded.height), encoded.pixels)
    dmtx = dmtx.resize((int(13 * mm_to_px), int(13 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))

    icon_path = os.path.join(DIRECTORIO_LOGO, "iconos.png")
    try:
        icons = Image.open(icon_path)
        label.paste(icons, (int(34 * mm_to_px), int(24 * mm_to_px)))
    except Exception as e:
        logger.warning(f"No se pudieron cargar los iconos regulatorios ({icon_path}): {e}")

    output_path = os.path.join(OUTPUT_DIR, "output_test2.png")
    label.save(output_path)
    logger.info(f"Etiqueta de batería generada correctamente -> {output_path}")
    return output_path


def Impr_Chile_label():
    mm_to_px = 11.81
    size = int(62 * mm_to_px)

    label = Image.new("RGB", (size, size), "white")
    img_path = os.path.join(IMAGES_DIR, "chile.png")
    try:
        img = Image.open(img_path)
        img.thumbnail((size, size), Image.Resampling.LANCZOS)
        x = (size - img.width) // 2
        y = (size - img.height) // 2
        label.paste(img, (x, y))
    except Exception as e:
        logger.error(f"No se pudo cargar la imagen de Chile ({img_path}): {e}")
        raise LabelError(f"No se pudo cargar la imagen de la etiqueta Chile: {e}") from e

    output_path = os.path.join(OUTPUT_DIR, "output_chile.png")
    label.save(output_path)
    logger.info(f"Etiqueta Chile generada correctamente -> {output_path}")
    return output_path


def Impr_Leica_label(PN, Product_Name, Pcs, Made_In, Serial, EAN):
    """Etiqueta de packaging Leica 75x50 mm (DOC-0003950 Rev D).
    Devuelve (ruta, avisos). Los avisos se vuelcan al panel de logs."""
    if ";" in Serial:
        Serial = Serial.split(";")[1]
    output_path = os.path.join(OUTPUT_DIR, "output_leica.png")
    try:
        path, warnings = leica_label.render_leica_label(
            PN, Product_Name, Pcs, Made_In, serial=Serial, ean=EAN,
            assets_dir=LEICA_ASSETS_DIR, out_path=output_path,
            font_bold=LEICA_FONT_BOLD, font_italic=LEICA_FONT_ITALIC)
    except ValueError as e:
        raise LabelError(str(e)) from e
    for w in warnings:
        logger.warning(f"Leica: {w}")
    logger.info(f"Etiqueta Leica generada correctamente -> {path}")
    return path, warnings


def _product_dpmm():
    """Resolución de render de las etiquetas de producto: la de la Zebra si
    se imprimen en ella; None (300 dpi de la QL) si van a la Brother."""
    return zebra_resolution()[1] if ZEBRA_PRINTER else None


def Impr_Leica_product_label(Variant, IMEI, Serial, dpmm=None):
    """Etiqueta de producto Leica ComBox70 63x50 mm (template EU o ROW).
    dpmm: resolución del render (None = 300 dpi). Devuelve (ruta, avisos)."""
    output_path = os.path.join(OUTPUT_DIR, "output_leica_producto.png")
    try:
        path, warnings = leica_product.render_product_label(
            Variant, IMEI, Serial, assets_dir=LEICA_ASSETS_DIR, out_path=output_path,
            font_regular=LEICA_PRODUCT_FONT_REGULAR, font_bold=LEICA_PRODUCT_FONT_BOLD,
            dpmm=dpmm)
    except ValueError as e:
        raise LabelError(str(e)) from e
    for w in warnings:
        logger.warning(f"Leica producto: {w}")
    logger.info(f"Etiqueta producto Leica {Variant} generada correctamente -> {path}")
    return path, warnings

def Impr_WS_product_label(Variant, IMEI, Serial, dpmm=None):
    """Etiqueta de producto WS ComBox70 63x50 mm (template EU o ROW).
    dpmm: resolución del render (None = 300 dpi). Devuelve (ruta, avisos)."""
    output_path = os.path.join(OUTPUT_DIR, "output_ws_producto.png")
    try:
        path, warnings = ws_product.render_product_label(
            Variant, IMEI, Serial, assets_dir=WS_PRODUCT_ASSETS_DIR, out_path=output_path,
            font_regular=LEICA_PRODUCT_FONT_REGULAR, font_bold=LEICA_PRODUCT_FONT_BOLD,
            dpmm=dpmm)
    except ValueError as e:
        raise LabelError(str(e)) from e
    for w in warnings:
        logger.warning(f"WS producto: {w}")
    logger.info(f"Etiqueta producto WS {Variant} generada correctamente -> {path}")
    return path, warnings

# =========================================================================
# INTERFAZ GRÁFICA
# =========================================================================

def _calibration_row(row, product):
    """Fila para calibrar la posición desde la propia pantalla: en la QL
    (packaging, o producto si no hay Zebra) o en la Zebra (producto).
    Los valores se aplican al momento y se guardan en config.json."""
    if product and ZEBRA_PRINTER:
        key, title, note = "ZEBRA_SHIFT_MM", "Calibración Zebra (mm):", ""
    elif product:
        key, title = "LEICA_PRODUCT_QL_SHIFT_MM", "Calibración QL (mm):"
        note = "" if LEICA_QL_PRINTER else "(solo con impresión directa)"
    else:
        key, title = "LEICA_QL_SHIFT_MM", "Calibración QL (mm):"
        note = "" if LEICA_QL_PRINTER else "(solo con impresión directa)"
    cur = globals()[key]
    calib_right.set(f"{cur[0]:g}")
    calib_up.set(f"{cur[1]:g}")

    def apply():
        try:
            val = (float(calib_right.get().replace(",", ".")), float(calib_up.get().replace(",", ".")))
        except ValueError:
            messagebox.showwarning("Calibración", "Introduce números en mm (p. ej. 1.5 o -0.3).")
            return
        globals()[key] = val
        try:
            save_config_key(key, list(val))
            logger.info(f"Calibración {key} = {list(val)} guardada en config.json")
            messagebox.showinfo("Calibración", f"Aplicado y guardado: derecha {val[0]:g} mm, arriba {val[1]:g} mm.")
        except Exception as e:
            logger.error(f"Calibración aplicada pero NO guardada en config.json: {e}")
            messagebox.showwarning("Calibración", f"Aplicado solo para esta sesión.\nNo se pudo guardar en config.json:\n{e}")

    f = tk.Frame(dynamic_container)
    f.grid(row=row, column=1, sticky="w", pady=(8, 2))
    tk.Label(dynamic_container, text=title).grid(row=row, column=0, sticky="w", pady=(8, 2))
    tk.Label(f, text="derecha").pack(side="left")
    tk.Entry(f, textvariable=calib_right, width=6).pack(side="left", padx=(4, 12))
    tk.Label(f, text="arriba").pack(side="left")
    tk.Entry(f, textvariable=calib_up, width=6).pack(side="left", padx=(4, 12))
    tk.Button(f, text="Aplicar y guardar", command=apply).pack(side="left")
    if note:
        tk.Label(f, text=note, fg="#888").pack(side="left", padx=8)


def switch_view():
    mode = selected_mode.get()
    for widget in dynamic_container.winfo_children():
        widget.destroy()

    if mode == 1:  # ARCHIVO
        tk.Label(dynamic_container, text="Archivo Excel:").grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=file_entry_var, width=60).grid(row=0, column=1, padx=5)
        tk.Button(dynamic_container, text="...", command=lambda: file_entry_var.set(filedialog.askopenfilename())).grid(row=0, column=2)

        tk.Label(dynamic_container, text="Escanear/Filtrar:").grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=filter_value, width=60).grid(row=1, column=1)
        tk.Button(dynamic_container, text="Buscar", command=search_record).grid(row=1, column=2)

    elif mode == 2:  # DISPOSITIVO MANUAL
        fields = [("Model:", manual_model), ("Brand:", manual_brand), ("PN:", manual_pn),
                  ("Serial:", manual_sn), ("Batch:", manual_batch)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, width=50).grid(row=i, column=1, sticky="w")

    elif mode == 3:  # ACCESORIO MANUAL
        tk.Label(dynamic_container, text="Model:").grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_model, width=50).grid(row=0, column=1, sticky="w")
        tk.Label(dynamic_container, text="PN:").grid(row=1, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_pn, width=50).grid(row=1, column=1, sticky="w")

    elif mode == 4:  # ETIQUETA CHILE
        tk.Label(dynamic_container, text="Nº Copias:").grid(row=0, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=num_copias_var, width=10).grid(row=0, column=1, sticky="w")

    elif mode == 5:  # BATERIAS
        fields = [("Product:", manual_pn), ("LOT:", manual_batch), ("Expiration_Date:", manual_expire)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, width=50).grid(row=i, column=1, sticky="w")

    elif mode == 6:  # LEICA
        fields = [("P/N Leica (7 díg.):", leica_pn), ("Nombre producto (SAP, EN):", leica_name),
                  ("Pcs/Sets:", leica_pcs), ("Made in:", leica_made_in),
                  ("S/N (vacío = código fecha):", leica_sn), ("EAN (solo B2C, opcional):", leica_ean),
                  ("Nº Copias:", num_copias_var)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, width=50).grid(row=i, column=1, sticky="w")
        _calibration_row(len(fields), product=False)

    elif mode == 7:  # LEICA PRODUCTO
        templates = leica_product.TEMPLATES
        info = tk.StringVar()

        def update_info(*_):
            t = templates.get(leica_variant.get())
            info.set(f"Model: {t['fixed']['model']}    Article No: {t['fixed']['article']}" if t else "")

        tk.Label(dynamic_container, text="Variante:").grid(row=0, column=0, sticky="w", pady=2)
        cb = ttk.Combobox(dynamic_container, textvariable=leica_variant, state="readonly",
                          values=list(templates), width=10)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", update_info)
        tk.Label(dynamic_container, textvariable=info).grid(row=1, column=1, sticky="w", pady=2)
        update_info()

        fields = [("IMEI (15 díg.):", leica_imei), ("Serial No:", leica_prod_sn), ("Nº Copias:", num_copias_var)]
        for i, (txt, var) in enumerate(fields, 2):
            tk.Label(dynamic_container, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, width=50).grid(row=i, column=1, sticky="w")
        _calibration_row(2 + len(fields), product=True)

    elif mode == 8:  # WS PRODUCTO
        templates = ws_product.TEMPLATES
        info = tk.StringVar()

        def update_info(*_):
            t = templates.get(leica_variant.get())
            f = t["fixed"] if t else {}
            info.set(f"Product: {f.get('product', '')}    Model: {f.get('model', '')}    "
                     f"Article No: {f.get('article', '')}" if t else "")

        tk.Label(dynamic_container, text="Variante:").grid(row=0, column=0, sticky="w", pady=2)
        cb = ttk.Combobox(dynamic_container, textvariable=leica_variant, state="readonly",
                          values=list(templates), width=10)
        cb.grid(row=0, column=1, sticky="w")
        cb.bind("<<ComboboxSelected>>", update_info)
        tk.Label(dynamic_container, textvariable=info).grid(row=1, column=1, sticky="w", pady=2)
        update_info()

        fields = [("IMEI (15 díg.):", leica_imei), ("Serial No:", leica_prod_sn), ("Nº Copias:", num_copias_var)]
        for i, (txt, var) in enumerate(fields, 2):
            tk.Label(dynamic_container, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, width=50).grid(row=i, column=1, sticky="w")
        _calibration_row(2 + len(fields), product=True)

    logger.debug(f"Vista cambiada a modo {mode}")


def search_record():
    file_path = file_entry_var.get()
    filter_val = filter_value.get().lower()
    if "ñ" in filter_val:
        filter_val = filter_val.split("ñ")[1]
    if ";" in filter_val:
        filter_val = filter_val.split(";")[1]
    if "%" in filter_val:
        filter_val = filter_val.split("%")[1]

    if not file_path:
        logger.warning("No se ha seleccionado ningún archivo Excel")
        messagebox.showwarning("Aviso", "Selecciona primero un archivo Excel.")
        return

    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        for row in sheet.iter_rows(values_only=True):
            if filter_val in row:
                label1_value.set(row[5] if len(row) > 5 else "N/A")   # ERP Code
                #label2_value.set(str(label1_value.get()).replace("-", ""))  # Model
                label2_value.set(row[10] if len(row) > 10 else "N/A")  # Model
                label3_value.set(row[13] if len(row) > 13 else "N/A")  # Serial
                logger.info(
                    f"Unidad encontrada (serial={filter_val}) -> "
                    f"ERP={label1_value.get()}, Model={label2_value.get()}, Serial={label3_value.get()}"
                )
                return
        logger.warning(f"No se encontró ninguna unidad con serial '{filter_val}' en el archivo")
        messagebox.showwarning("Aviso", f"No se encontró ninguna unidad con serial '{filter_val}'.")
    except Exception as e:
        logger.error(f"Error al leer el archivo Excel: {e}")
        messagebox.showerror("Error", str(e))


def generate_label():
    """Genera la etiqueta del modo actual con los datos del formulario.
    Devuelve (ruta, avisos). Lanza LabelError si faltan datos."""
    mode = selected_mode.get()
    warnings = []
    batch_n = Crear_Batch()

    if mode == 1:
        logger.info("Generando etiqueta - modo 1 (Archivo)")
        erp_code, model, serial = label1_value.get(), label2_value.get(), label3_value.get()
        datam = f"{erp_code};{serial};{batch_n}"
        path = Impr_Node_packaging_label_Peru(datam, model, erp_code, serial, batch_n)

    elif mode == 2:
        logger.info("Generando etiqueta - modo 2 (Dispositivo Manual)")
        brand = manual_brand.get()
        model, erp_code, serial = manual_model.get(), manual_pn.get(), manual_sn.get()
        batch = manual_batch.get() if manual_batch.get() else batch_n
        datam = f"{erp_code};{serial};{batch}"
        path = Impr_Node_packaging_label(datam, model, brand, erp_code, serial, batch)

    elif mode == 3:
        logger.info("Generando etiqueta - modo 3 (Accesorio Manual)")
        model, erp_code = manual_model.get(), manual_pn.get()
        datam = f"{erp_code}"
        path = Impr_Acc_packaging_label(datam, model, erp_code)

    elif mode == 5:
        logger.info("Generando etiqueta - modo 5 (BATERIAS)")
        Product, LOT, Expiration_Date = manual_pn.get(), manual_batch.get(), manual_expire.get()
        datam = f"{Product};{LOT}"  # sin fecha de caducidad en el DataMatrix
        path = Impr_Bateria_label(datam, Product, LOT, Expiration_Date)

    elif mode == 4:
        logger.info("Generando etiqueta - modo 4 (Chile)")
        path = Impr_Chile_label()

    elif mode == 6:
        logger.info("Generando etiqueta - modo 6 (Leica)")
        path, warnings = Impr_Leica_label(
            leica_pn.get(), leica_name.get(), leica_pcs.get(), leica_made_in.get(),
            leica_sn.get().strip(), leica_ean.get())

    elif mode == 7:
        logger.info(f"Generando etiqueta - modo 7 (Leica producto {leica_variant.get()})")
        path, warnings = Impr_Leica_product_label(leica_variant.get(), leica_imei.get(),
                                                  leica_prod_sn.get(), dpmm=_product_dpmm())
    
    elif mode == 8:
        logger.info(f"Generando etiqueta - modo 8 (WS producto {leica_variant.get()})")
        path, warnings = Impr_WS_product_label(leica_variant.get(), leica_imei.get(),
                                               leica_prod_sn.get(), dpmm=_product_dpmm())

    else:
        raise LabelError(f"Modo de etiqueta desconocido: {mode}")

    return path, warnings


def show_preview(path):
    img = Image.open(path)
    preview_img = img.copy()
    preview_img.thumbnail((PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT), Image.Resampling.LANCZOS)
    foto = IMG.PhotoImage(preview_img)
    label_preview.config(image=foto)
    label_preview.image = foto


def display_label():
    mode = selected_mode.get()
    try:
        path, warnings = generate_label()
        show_preview(path)
        if mode in QL_MODES and warnings:
            titulo = "Avisos etiqueta WS" if mode == 8 else "Avisos etiqueta Leica"
            messagebox.showwarning(titulo, "\n\n".join(warnings))

    except LabelError as e:
        logger.warning(f"Generación de etiqueta cancelada: {e}")
        messagebox.showwarning("Datos incompletos", str(e))
    except Exception as e:
        logger.error(f"Error inesperado al generar la etiqueta (modo {mode}): {e}")
        messagebox.showerror("Error", str(e))


def print_label():
    mode = selected_mode.get()

    try:
        # Se regenera siempre: lo que se imprime es lo que hay ahora en el formulario
        path, warnings = generate_label()
        show_preview(path)
    except LabelError as e:
        logger.warning(f"Impresión cancelada: {e}")
        messagebox.showwarning("Datos incompletos", str(e))
        return
    except Exception as e:
        logger.error(f"Error inesperado al generar la etiqueta (modo {mode}): {e}")
        messagebox.showerror("Error", str(e))
        return

    if mode in QL_MODES and any("Faltan imágenes" in w for w in warnings):
        marca = "WS" if mode == 8 else "Leica"
        logger.error(f"Impresión {marca} bloqueada: faltan imágenes oficiales")
        messagebox.showerror(marca, "No se puede imprimir: faltan imágenes oficiales.\n\n" + "\n\n".join(warnings))
        return

    try:
        if mode in (4,) + QL_MODES:
            try:
                n = int(num_copias_var.get())
                if n < 1:
                    raise ValueError
            except ValueError:
                logger.warning(f"Nº de copias inválido ('{num_copias_var.get()}'), se usará 1")
                n = 1
        else:
            n = 1

        # Rollo de la QL: packaging (6) o producto (7 Leica / 8 WS)
        tape = LEICA_PRODUCT_QL_TAPE if mode in QL_PRODUCT_MODES else LEICA_QL_TAPE
        clear_vars = [manual_model, manual_pn, manual_sn, manual_batch, manual_expire,
                      filter_value, leica_sn, leica_imei, leica_prod_sn]

        # Etiquetas de producto en la Zebra (ZPL raw)
        if mode in QL_PRODUCT_MODES and ZEBRA_PRINTER:
            zs = zebra_settings()
            z_dpi, z_dpmm = zebra_resolution()
            dx, dy = ZEBRA_SHIFT_MM
            logger.debug(f"Impresión Zebra -> {ZEBRA_PRINTER} ({z_dpi} dpi = {z_dpmm} p/mm, giro {ZEBRA_ROTATE}°, "
                         f"desplazamiento dcha {dx} mm / arriba {dy} mm, brillo {zs['brightness']:g} / "
                         f"contraste {zs['contrast']:g}, darkness {zs['darkness']}, velocidad {zs['speed']})")
            st = WS_label.print_zebra(path, ZEBRA_PRINTER, copies=n,
                                      zpl_path=os.path.join(OUTPUT_DIR, "output_zebra.zpl"),
                                      bitmap_path=os.path.join(OUTPUT_DIR, "output_zebra_bitmap.png"),
                                      dpmm=z_dpmm, src_dpmm=z_dpmm, rotate=ZEBRA_ROTATE, threshold=ZEBRA_THRESHOLD,
                                      shift_right_mm=dx, shift_up_mm=dy, **zs)
            logger.info(f"Enviadas {n} copia(s) a la Zebra ({z_dpi} dpi) por {st['via']}. ZPL: {st['zpl_path']}")
            messagebox.showinfo("Impresión", f"Enviadas {n} etiqueta(s) a la Zebra correctamente.")
            for v in clear_vars:
                v.set("")
            return

        if mode in QL_MODES:
            brillo, contraste = ql_tone()
            bitmap_path = os.path.join(OUTPUT_DIR, "output_ql_bitmap.png")

        if mode in QL_MODES and LEICA_QL_PRINTER:
            dx, dy = LEICA_PRODUCT_QL_SHIFT_MM if mode in QL_PRODUCT_MODES else LEICA_QL_SHIFT_MM
            ident, _backend = WS_label.normalize_ql_printer(LEICA_QL_PRINTER)
            logger.debug(f"Impresión directa brother_ql -> {ident} [{_backend}] (rollo {tape} mm, "
                         f"desplazamiento dcha {dx} mm / arriba {dy} mm, "
                         f"brillo {brillo:g} / contraste {contraste:g})")
            st = WS_label.print_brother_ql(path, LEICA_QL_PRINTER, model=LEICA_QL_MODEL,
                                           tape=tape, copies=n, rotate=LEICA_QL_ROTATE,
                                           threshold=LEICA_QL_THRESHOLD, trim_mm=LEICA_QL_TRIM_MM,
                                           shift_right_mm=dx, shift_up_mm=dy,
                                           brightness=brillo, contrast=contraste,
                                           bitmap_path=bitmap_path)
            nominal = 63.0 if mode in QL_PRODUCT_MODES else 75.0
            length = st.get("length_mm") if isinstance(st, dict) else None
            if isinstance(length, (int, float)) and abs(length - nominal) > 0.2:
                logger.warning(f"Con el desplazamiento horizontal la tira mide {length} mm (nominal {nominal} mm)")
            logger.info(f"Enviadas {n} copia(s) a '{ident}' (directo). Bitmap enviado: {bitmap_path}")
            messagebox.showinfo("Impresión", f"Enviadas {n} etiqueta(s) correctamente.")
            for v in clear_vars:
                v.set("")
            return

        if mode in QL_MODES:
            # Por CUPS: se manda ya girada, en 1 bit y a 300 ppi para que no se reescale
            src = path
            path = bitmap_path
            WS_label.make_ql_bitmap(src, tape=tape, rotate=LEICA_QL_ROTATE,
                                    threshold=LEICA_QL_THRESHOLD, trim_mm=LEICA_QL_TRIM_MM or 0,
                                    brightness=brillo, contrast=contraste, out_path=path)
            logger.debug(f"Bitmap QL por CUPS (brillo {brillo:g} / contraste {contraste:g}) -> {path}")
            printer = LEICA_PRINTER
            print_opts = list(LEICA_PRODUCT_LP_OPTIONS if mode in QL_PRODUCT_MODES else LEICA_LP_OPTIONS)
        else:
            printer = IMPRESORA
            print_opts = ["-o", "PageSize=62X1"] if mode == 4 else ["-o", "orientation-requested=3"]

        cmd = ["lp", "-d", printer, "-n", str(n)] + print_opts + [path]
        logger.debug(f"Ejecutando: {' '.join(cmd)}")
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"lp ha fallado: {(r.stderr or r.stdout).strip()}")

        logger.info(f"Enviadas {n} copia(s) a la impresora '{printer}'")
        messagebox.showinfo("Impresión", f"Enviadas {n} etiqueta(s) correctamente.")

        for v in clear_vars:
            v.set("")

    except LabelError as e:
        logger.warning(f"Impresión cancelada: {e}")
        messagebox.showwarning("Configuración", str(e))
    except Exception as e:
        logger.error(f"Error al imprimir: {e}")
        messagebox.showerror("Error", str(e))


# =========================================================================
# SETUP PRINCIPAL
# =========================================================================

root = tk.Tk()
root.title("WS Labelling - Rev 4.1.1")
monitor = get_monitors()[0]
root.geometry(f"{monitor.width}x{monitor.height}")

selected_mode = tk.IntVar(value=1)
file_entry_var, filter_value = tk.StringVar(), tk.StringVar()
label1_value, label2_value, label3_value = tk.StringVar(value="N/A"), tk.StringVar(value="N/A"), tk.StringVar(value="N/A")
manual_model, manual_brand, manual_pn, manual_sn, manual_batch, manual_expire = (
    tk.StringVar(), tk.StringVar(value="LOADSENSING G7"), tk.StringVar(),
    tk.StringVar(), tk.StringVar(), tk.StringVar()
)
num_copias_var = tk.StringVar(value="1")
leica_pn, leica_name, leica_pcs, leica_sn, leica_ean = (
    tk.StringVar(), tk.StringVar(), tk.StringVar(value="1"), tk.StringVar(), tk.StringVar()
)
leica_made_in = tk.StringVar(value="Spain")
leica_variant = tk.StringVar(value="EU")
leica_imei, leica_prod_sn = tk.StringVar(), tk.StringVar()
calib_right, calib_up = tk.StringVar(value="0"), tk.StringVar(value="0")

# --- Header ---
canvas_logo = tk.Canvas(root, height=70, highlightthickness=0)
canvas_logo.pack(fill="x")
try:
    ws_logo_ui = PhotoImage(file=os.path.join(DIRECTORIO_LOGO, "WS_logo.png"))
    canvas_logo.create_image(10, 10, anchor="nw", image=ws_logo_ui)
except Exception as e:
    logger.warning(f"No se pudo cargar el logo de cabecera: {e}")

# --- Panel de logs (parte inferior) --- se empaqueta ANTES que el resto
# de widgets "normales" para reservarle el espacio inferior de la ventana.
log_frame = tk.Frame(root)
log_frame.pack(side="bottom", fill="both", expand=False)

log_header = tk.Frame(log_frame)
log_header.pack(fill="x")
tk.Label(log_header , text="Registro de actividad", font=("TkDefaultFont", 9, "bold")).pack(side="left", padx=5, pady=(4, 0))

log_scroll = tk.Scrollbar(log_frame)
log_scroll.pack(side="right", fill="y")

log_text = tk.Text(
    log_frame, height=10, bg="white", fg="#333333",
    font=("Consolas", 9), state="disabled", yscrollcommand=log_scroll.set, wrap="none"
)
log_text.pack(side="bottom", fill="both", expand=True, padx=5, pady=(0, 5))
log_scroll.config(command=log_text.yview)

logger.addHandler(TkTextHandler(log_text))
logger.info("Aplicación iniciada - WS Labelling Rev 4.1.1")
for _w in CONFIG_WARNINGS:
    logger.warning(_w)
for _i in CONFIG_INFO:
    logger.info(_i)
logger.info(f"Calibración QL: packaging {list(LEICA_QL_SHIFT_MM)} / producto {list(LEICA_PRODUCT_QL_SHIFT_MM)} mm"
            f" | Zebra {list(ZEBRA_SHIFT_MM)} mm")
logger.info(f"Carpeta de trabajo: {OUTPUT_DIR}")
if LEICA_QL_PRINTER:
    try:
        _id, _bk = WS_label.normalize_ql_printer(LEICA_QL_PRINTER)
        if _id != LEICA_QL_PRINTER:
            logger.info(f"Impresora QL: '{LEICA_QL_PRINTER}' -> {_id} [{_bk}]")
        else:
            logger.info(f"Impresora QL: {_id} [{_bk}]")
    except ValueError as _e:
        logger.warning(f"LEICA_QL_PRINTER: {_e}")
try:
    _b, _c = ql_tone()
    logger.info(f"QL brillo {_b:g} / contraste {_c:g} (LEICA_QL_BRIGHTNESS / LEICA_QL_CONTRAST)")
except LabelError as _e:
    logger.warning(str(_e))
if ZEBRA_PRINTER:
    try:
        _z = zebra_settings()
        _zdpi, _zdpmm = zebra_resolution()
        logger.info(f"Etiquetas de producto -> Zebra '{ZEBRA_PRINTER}' (ZPL raw, {_zdpi} dpi = {_zdpmm} p/mm): "
                    f"brillo {_z['brightness']:g} / contraste {_z['contrast']:g} / "
                    f"darkness {_z['darkness']} / velocidad {_z['speed']}")
    except LabelError as _e:
        logger.warning(str(_e))
else:
    logger.info("Etiquetas de producto -> Brother QL (ZEBRA_PRINTER sin definir)")
if RUBIK_FONT_PATH:
    logger.info(f"Fuente Rubik localizada en: {RUBIK_FONT_PATH}")
else:
    logger.warning(
        "No se encontró la fuente Rubik en ninguna ruta conocida "
        f"({[p for p in _FONT_CANDIDATES if p]}). Se usará la fuente por defecto."
    )

# --- Modos ---
m_frame = tk.LabelFrame(root, text="Tipo de etiqueta", padx=10, pady=5)
m_frame.pack(fill="x", padx=20)
for i, txt in enumerate(["Archivo", "Dispositivo Manual", "Accesorio Manual", "Etiqueta Chile", "BATERIAS", "Leica", "Leica Producto", "WS Producto"], 1):
    tk.Radiobutton(m_frame, text=txt, variable=selected_mode, value=i, command=switch_view).pack(side="left", padx=10)

dynamic_container = tk.Frame(root, pady=15)
dynamic_container.pack()

# --- Acciones ---
b_frame = tk.Frame(root)
b_frame.pack(pady=10)
tk.Button(b_frame, text="GENERAR ETIQUETA", bg="#f0f0f0", command=display_label, width=20, height=2).pack(side="left", padx=5)
tk.Button(b_frame, text="IMPRIMIR", bg="#d1ffd1", command=print_label, width=20, height=2).pack(side="left", padx=5)

label_preview = tk.Label(root, bg="white", relief="solid", width=PREVIEW_MAX_WIDTH, height=PREVIEW_MAX_HEIGHT)
label_preview.pack(pady=10)

switch_view()
root.mainloop()
