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
'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import openpyxl
import logging
import os
import json
import datetime
from screeninfo import get_monitors
from pylibdmtx.pylibdmtx import encode
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk as IMG

# =========================================================================
# CONFIGURACIÓN
# =========================================================================

def load_config(file_path="config.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        return {}

config = load_config()
IMPRESORA = config.get("IMPRESORA", "")
DIRECTORIO_LOGO = config.get("DIRECTORIO_LOGO", "")
BATCH_N = config.get("batch", "")

# Rutas candidatas para la fuente Rubik, en orden de preferencia:
# 1) lo indicado en config.json, 2) instalación de sistema típica en Ubuntu,
# 3) copia local del usuario (entornos de desarrollo antiguos).
_FONT_CANDIDATES = [
    config.get("font_path"),
    config.get("Rubik_font_path"),
    "/usr/share/fonts/truetype/Rubik/Rubik-Light.ttf",
    os.path.expanduser("~/.local/share/fonts/Rubik-Light.ttf"),
]
RUBIK_FONT_PATH = next((p for p in _FONT_CANDIDATES if p and os.path.isfile(p)), None)

DATAMATRIX_SIZE = "36x36"  # Tamaño fijo para evitar el bug de auto-sizing de libdmtx
OUTPUT_DIR = os.path.expanduser("~/Documentos/labelling_tk_app")
IMAGES_DIR = os.path.join(OUTPUT_DIR, "images")

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


# =========================================================================
# INTERFAZ GRÁFICA
# =========================================================================

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
                label1_value.set(row[5] if len(row) > 5 else "N/A")  # ERP Code
                #label2_value.set(str(label1_value.get()).replace("-", ""))  # Model
                label2_value.set(row[10] if len(row) > 5 else "N/A")  # Model
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


def display_label():
    mode = selected_mode.get()
    path = None

    try:
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

        else:
            logger.info("Generando etiqueta - modo 4 (Chile)")
            path = Impr_Chile_label()

        img = Image.open(path)
        preview_img = img.copy()
        preview_img.thumbnail((PREVIEW_MAX_WIDTH, PREVIEW_MAX_HEIGHT), Image.Resampling.LANCZOS)
        foto = IMG.PhotoImage(preview_img)
        label_preview.config(image=foto)
        label_preview.image = foto

    except LabelError as e:
        logger.warning(f"Generación de etiqueta cancelada: {e}")
        messagebox.showwarning("Datos incompletos", str(e))
    except Exception as e:
        logger.error(f"Error inesperado al generar la etiqueta (modo {mode}): {e}")
        messagebox.showerror("Error", str(e))


def print_label():
    mode = selected_mode.get()
    path = os.path.join(OUTPUT_DIR, "output_chile.png") if mode == 4 else os.path.join(OUTPUT_DIR, "output_test2.png")

    if not os.path.exists(path):
        logger.warning(f"No hay ninguna etiqueta generada todavía en {path}")
        messagebox.showwarning("Aviso", "Genera la etiqueta antes de imprimir.")
        return

    try:
        if mode == 4:
            try:
                n = int(num_copias_var.get())
            except ValueError:
                logger.warning(f"Nº de copias inválido ('{num_copias_var.get()}'), se usará 1")
                n = 1
        else:
            n = 1

        print_opts = "-o PageSize=62X1" if mode == 4 else "-o orientation-requested=3"
        for _ in range(n):
            os.system(f"lp {print_opts} -d {IMPRESORA} {path}")

        logger.info(f"Enviadas {n} copia(s) a la impresora '{IMPRESORA}'")
        messagebox.showinfo("Impresión", f"Enviadas {n} etiqueta(s) correctamente.")

        for v in [manual_model, manual_pn, manual_sn, filter_value]:
            v.set("")

    except Exception as e:
        logger.error(f"Error al imprimir: {e}")
        messagebox.showerror("Error", str(e))


# =========================================================================
# SETUP PRINCIPAL
# =========================================================================

root = tk.Tk()
root.title("WS Labelling - Rev 3.1.1")
monitor = get_monitors()[0]
root.geometry(f"{monitor.width}x{monitor.height}")

selected_mode = tk.IntVar(value=1)
file_entry_var, filter_value = tk.StringVar(), tk.StringVar()
label1_value, label2_value, label3_value = tk.StringVar(value="N/A"), tk.StringVar(value="N/A"), tk.StringVar(value="N/A")
manual_model, manual_brand, manual_pn, manual_sn, manual_batch = (
    tk.StringVar(), tk.StringVar(value="LOADSENSING G7"), tk.StringVar(), tk.StringVar(), tk.StringVar()
)
num_copias_var = tk.StringVar(value="1")

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
    log_frame, height=10, bg="white", fg="#d4d4d4",
    font=("Consolas", 9), state="disabled", yscrollcommand=log_scroll.set, wrap="none"
)
log_text.pack(side="bottom", fill="both", expand=True, padx=5, pady=(0, 5))
log_scroll.config(command=log_text.yview)

logger.addHandler(TkTextHandler(log_text))
logger.info("Aplicación iniciada - WS Labelling Rev 3.2")
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
for i, txt in enumerate(["Archivo", "Dispositivo Manual", "Accesorio Manual", "Etiqueta Chile"], 1):
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
