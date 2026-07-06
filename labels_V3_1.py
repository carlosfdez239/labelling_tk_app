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
'''

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, PhotoImage
import openpyxl
import subprocess
from pylibdmtx.pylibdmtx import encode
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageTk as IMG
import os
import json
import datetime
from screeninfo import get_monitors

# --- Configuración y Carga ---
def load_config(file_path="config.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        return {}

config = load_config()
IMPRESORA = config.get("IMPRESORA", "")
DIRECTORIO_LOGO = config.get("DIRECTORIO_LOGO", "")
# Ruta de fuente corregida para entorno local
RUBIK_FONT_PATH = os.path.expanduser("~/.local/share/fonts/Rubik-Light.ttf")
BATCH_N = config.get("batch", "")

# --- Lógica de Generación de Etiqueta ---

def Crear_Batch():
    fecha = datetime.datetime.today().strftime("%Y%m%d")
    return fecha + BATCH_N

def Impr_Node_packaging_label(datam, Model, Brand, ERP_Code, Serial_N):
    mm_to_px = 11.81  # 300 DPI
    width = int(50 * mm_to_px)
    height = int(45 * mm_to_px)
    
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)

    # Cargar Fuentes
    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except:
        font_main = font_small = ImageFont.load_default()

    # 1. Logo Worldsensing (Cabecera)
    try:
        # logo_path = "/home/ws-prod23/labelling_tk_app/images/W_Label_Devices_new.png"
        # logo = Image.open(logo_path)
        # logo_w = int(44 * mm_to_px)
        # logo_h = int(logo.height * (logo_w / logo.width))
        # logo = logo.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        # label.paste(logo, (int(3 * mm_to_px), int(2 * mm_to_px)))
                
        logo_path = "/home/ws-prod23/labelling_tk_app/images/W_Label_Devices_new.png"
        logo = Image.open(logo_path).resize((int(42 * mm_to_px), int(8 * mm_to_px)))
        label.paste(logo, (0, 0))
    except:
        draw.text((2 * mm_to_px, 2 * mm_to_px), "WORLDSENSING", font=font_main, fill="black")

    # 2. Dirección
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    # 3. Datos del Producto
    y_pos = 14 * mm_to_px
    spacing = 3 * mm_to_px
    
    

    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 3), f"SERIAL NUMBER:  {Serial_N}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 4), f"BATCH NUMBER:  {manual_batch.get()}", font=font_main, fill="black")

    # DataMatrix
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    dmtx = dmtx.resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))
    icon_path = os.path.join(DIRECTORIO_LOGO, "iconos.png")
    icons = Image.open(icon_path)
    label.paste(icons, (int(34 * mm_to_px), int(20 * mm_to_px)))
    
    output_path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    label.save(output_path)
    return output_path

def Impr_Acc_packaging_label(datam, Model, ERP_Code):
    mm_to_px = 11.81  # 300 DPI
    width = int(50 * mm_to_px)
    height = int(45 * mm_to_px)
    
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)

    # Cargar Fuentes
    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except:
        font_main = font_small = ImageFont.load_default()

    # 1. Logo Worldsensing (Cabecera)
    try:               
        logo_path = "/home/ws-prod23/labelling_tk_app/images/W_Label_Devices_new.png"
        logo = Image.open(logo_path).resize((int(42 * mm_to_px), int(8 * mm_to_px)))
        label.paste(logo, (0, 0))
    except:
        draw.text((2 * mm_to_px, 2 * mm_to_px), "WORLDSENSING", font=font_main, fill="black")

    # 2. Dirección
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    # 3. Datos del Producto
    y_pos = 14 * mm_to_px
    spacing = 3 * mm_to_px
    
    

    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    #draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    #draw.text((1 * mm_to_px, y_pos + spacing * 3), f"SERIAL NUMBER:  {Serial_N}", font=font_main, fill="black")
    #draw.text((1 * mm_to_px, y_pos + spacing * 4), f"BATCH NUMBER:  {manual_batch.get()}", font=font_main, fill="black")

    # DataMatrix
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    dmtx = dmtx.resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))
    icon_path = os.path.join(DIRECTORIO_LOGO, "iconos.png")
    icons = Image.open(icon_path)
    label.paste(icons, (int(34 * mm_to_px), int(20 * mm_to_px)))
    
    output_path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    label.save(output_path)
    return output_path

def Impr_Chile_label():
    mm_to_px = 11.81  # 300 DPI
    size = int(62 * mm_to_px)

    label = Image.new("RGB", (size, size), "white")
    DIRECTORIO_LOGO = os.path.expanduser("~/Documents/Testing/labelling_tk_app/images")
    img_path = os.path.join(DIRECTORIO_LOGO, "chile.png")
    img = Image.open(img_path)
    img.thumbnail((size, size), Image.Resampling.LANCZOS)
    x = (size - img.width) // 2
    y = (size - img.height) // 2
    label.paste(img, (x, y))

    output_path = os.path.expanduser("~/Documents/Testing/labelling_tk_app/output_chile.png")
    label.save(output_path)
    return output_path

# --- Interfaz Gráfica ---

def switch_view():
    mode = selected_mode.get()
    for widget in dynamic_container.winfo_children():
        widget.destroy()
    
    if mode == 1: # ARCHIVO
        tk.Label(dynamic_container, text="Archivo Excel:").grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=file_entry_var, width=60).grid(row=0, column=1, padx=5)
        tk.Button(dynamic_container, text="...", command=lambda: file_entry_var.set(filedialog.askopenfilename())).grid(row=0, column=2)
        
        tk.Label(dynamic_container, text="Escanear/Filtrar:").grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=filter_value, width=60).grid(row=1, column=1)
        tk.Button(dynamic_container, text="Buscar", command=search_record).grid(row=1, column=2)

    elif mode == 2: # DISPOSITIVO MANUAL
        fields = [("Model:", manual_model), ("Brand:", manual_brand), ("PN:", manual_pn), 
                  ("Serial:", manual_sn), ("Batch:", manual_batch)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, width=50).grid(row=i, column=1, sticky="w")

    elif mode == 3: # ACCESORIO MANUAL
        tk.Label(dynamic_container, text="Model:").grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_model, width=50).grid(row=0, column=1, sticky="w")
        tk.Label(dynamic_container, text="PN:").grid(row=1, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_pn, width=50).grid(row=1, column=1, sticky="w")

    elif mode == 4: # ETIQUETA CHILE
        tk.Label(dynamic_container, text="Nº Copias:").grid(row=0, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=num_copias_var, width=10).grid(row=0, column=1, sticky="w")

def search_record():
    file_path = file_entry_var.get()
    filter_val = filter_value.get()
    if ";" in filter_val: filter_val = filter_val.split(";")[1]
    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        for row in sheet.iter_rows(values_only=True):
            if filter_val in row:
                label1_value.set(row[5] if len(row) > 5 else "N/A")
                label2_value.set(str(label1_value.get()).replace("-", ""))
                label3_value.set(row[13] if len(row) > 13 else "N/A")
                return
    except Exception as e: messagebox.showerror("Error", str(e))

def display_label():
    try:
        mode = selected_mode.get()
        #batch_n = Crear_Batch()
        
        if mode == 1:
            print(f"Estamos en modo 1")
            brand = manual_brand.get()
            m, p, s = label1_value.get(), label2_value.get(), label3_value.get()
            datam = f"{m};{s};{batch_n}"
            path = Impr_Node_packaging_label(datam, m, brand, p, s)
        elif mode == 2:
            print(f"Estamos en modo 2")
            brand = manual_brand.get()
            m, p, s = manual_model.get(), manual_pn.get(), manual_sn.get()
            b = manual_batch.get() if manual_batch.get() else batch_n
            datam = f"{p};{s};{b}"
            path = Impr_Node_packaging_label(datam, m, brand, p, s)
        elif mode == 3:
            print(f"Estamos en modo 3")
            m, p = manual_model.get(), manual_pn.get()
            #batch_n = Crear_Batch()
            datam = f"{p}"
            path = Impr_Acc_packaging_label(datam, m, p)
        else:
            print(f"Estamos en modo 4")
            path = Impr_Chile_label()


        img = Image.open(path)
        foto = IMG.PhotoImage(img)
        label_preview.config(image=foto)
        label_preview.image = foto
    except Exception as e: messagebox.showerror("Error", str(e))

def print_label():
    mode = selected_mode.get()
    path = os.path.expanduser("~/Documents/Testing/labelling_tk_app/output_chile.png") if mode == 4 else os.path.expanduser("~/Documents/Testing/labelling_tk_app/output_test2.png")
    if not os.path.exists(path): return

    try:
        # Si estamos en modo Etiqueta Chile (4), leemos las copias, si no, solo 1
        if mode == 4:
            try:
                n = int(num_copias_var.get())
            except ValueError:
                n = 1 # Por seguridad, si no es un número, imprime 1
        else:
            n = 1

        # Bucle de impresión
        print_opts = "-o PageSize=62X1" if mode == 4 else "-o orientation-requested=3"
        for i in range(n):
            os.system(f'lp {print_opts} -d {IMPRESORA} {path}')

        messagebox.showinfo("Impresión", f"Enviadas {n} etiqueta(s) correctamente.")

        # Limpieza tras imprimir
        for v in [manual_model, manual_pn, manual_sn, filter_value]:
            v.set("")

    except Exception as e:
        messagebox.showerror("Error", str(e))
# --- Setup Principal ---
root = tk.Tk()
root.title("WS Labelling - Rev 3.1")
monitor = get_monitors()[0]
root.geometry(f"{monitor.width}x{monitor.height}")

selected_mode = tk.IntVar(value=1)
file_entry_var, filter_value = tk.StringVar(), tk.StringVar()
label1_value, label2_value, label3_value = tk.StringVar(value="N/A"), tk.StringVar(value="N/A"), tk.StringVar(value="N/A")
manual_model, manual_brand, manual_pn, manual_sn, manual_batch = tk.StringVar(), tk.StringVar(value="LOADSENSING G7"), tk.StringVar(), tk.StringVar(), tk.StringVar()
num_copias_var = tk.StringVar(value="1")

# Header
canvas_logo = tk.Canvas(root, height=70, highlightthickness=0)
canvas_logo.pack(fill="x")
try:
    ws_logo_ui = PhotoImage(file=os.path.join(DIRECTORIO_LOGO, "WS_logo.png"))
    canvas_logo.create_image(10, 10, anchor="nw", image=ws_logo_ui)
except: pass

# Modos
m_frame = tk.LabelFrame(root, text="Tipo de etiqueta", padx=10, pady=5)
m_frame.pack(fill="x", padx=20)
for i, txt in enumerate(["Archivo", "Dispositivo Manual", "Accesorio Manual", "Etiqueta Chile"], 1):
    tk.Radiobutton(m_frame, text=txt, variable=selected_mode, value=i, command=switch_view).pack(side="left", padx=10)

dynamic_container = tk.Frame(root, pady=15)
dynamic_container.pack()

# Acciones
b_frame = tk.Frame(root)
b_frame.pack(pady=10)
tk.Button(b_frame, text="GENERAR ETIQUETA", bg="#f0f0f0", command=display_label, width=20, height=2).pack(side="left", padx=5)
tk.Button(b_frame, text="IMPRIMIR", bg="#d1ffd1", command=print_label, width=20, height=2).pack(side="left", padx=5)

label_preview = tk.Label(root, bg="white", relief="solid", width=650, height=450)
label_preview.pack(pady=10)

switch_view()
root.mainloop()