'''
C. Fdez
Rev 3.1 --> 31/03/2026
- Restauración de Modo GW y búsqueda en Modo 1.
- Implementación de visibilidad dinámica con .grid_forget().
- Soporte para etiquetas de Producto y Packaging.
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
from tkinter import font as tkfont

# --- Configuración y Carga ---
def load_config(file_path="config.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception:
        return {}

config = load_config()
IMPRESORA = config.get("IMPRESORA", "")
PRODUCT_PRINTER = config.get("PRODUCT_PRINTER","")
DIRECTORIO_LOGO = config.get("DIRECTORIO_LOGO", "")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUBIK_FONT_PATH = os.path.join(BASE_DIR, "Rubik", "Rubik-Light.ttf")
BATCH_N = config.get("batch", "")


# --- Funciones de Dibujo (Packaging, Producto, GW) ---

def Impr_Node_packaging_label(datam, Model, Brand, ERP_Code, Serial_N):
    mm_to_px = 11.81
    width, height = int(50 * mm_to_px), int(45 * mm_to_px)
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except: font_main = font_small = ImageFont.load_default()
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(BASE_DIR, "images", "W_Label_Devices_new.png")
        logo = Image.open(logo_path).resize((int(42 * mm_to_px), int(8 * mm_to_px)))
        label.paste(logo, (0, 0))
    except: pass
    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")
    y_pos, spacing = 14 * mm_to_px, 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 3), f"SERIAL NUMBER:  {Serial_N}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 4), f"BATCH NUMBER:  {manual_batch.get()}", font=font_main, fill="black")
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels).resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(36 * mm_to_px), int(10 * mm_to_px)))
    try:
        icons = Image.open(os.path.join(DIRECTORIO_LOGO, "iconos.png"))
        label.paste(icons, (int(34 * mm_to_px), int(20 * mm_to_px)))
    except: pass
    #path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    path = os.path.join(BASE_DIR, "output_test2.png")
    label.save(path); return path

def Impr_Acc_packaging_label(datam, Model, ERP_Code):
    mm_to_px = 11.81
    width, height = int(50 * mm_to_px), int(45 * mm_to_px)
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except: font_main = font_small = ImageFont.load_default()
    y_pos, spacing = 14 * mm_to_px, 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels).resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))
    #path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    path = os.path.join(BASE_DIR, "output_test2.png")
    label.save(path); return path

def Impr_GW_packaging_label(datam, Model, ERP, SN, MAC, GW_ID):
    mm_to_px = 11.81
    width, height = int(50 * mm_to_px), int(45 * mm_to_px)
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)
    try: font_main = ImageFont.truetype(RUBIK_FONT_PATH, 22)
    except: font_main = ImageFont.load_default()
    y_pos, spacing = 10 * mm_to_px, 4 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL: {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"ERP: {ERP}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing*2), f"SN: {SN}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing*3), f"MAC: {MAC}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing*4), f"GW ID: {GW_ID}", font=font_main, fill="black")
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels).resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(36 * mm_to_px), int(10 * mm_to_px)))
    path = os.path.join(BASE_DIR, "output_gw.png")
    label.save(path); return path

def Impr_Node_Product_label(datam, Model, Brand, ERP_Code):
    
    mm_to_px = 11.81  # 300 DPI
    #width, height = int(71 * mm_to_px), int(41 * mm_to_px)
    #width, height = int(51 * mm_to_px), int(35 * mm_to_px)
    width, height = int(55 * mm_to_px), int(35 * mm_to_px)

    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 22)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 15)
        font_direction = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except:
        font_main = font_small = ImageFont.load_default()

    # Logo e Info
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(BASE_DIR, "images", "W_Label_Devices_new.png")
        logo = Image.open(logo_path).resize((int(33 * mm_to_px), int(7 * mm_to_px)))
        label.paste(logo, (1, 4))
    except: pass

    draw.text((1 * mm_to_px, 8 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_direction, fill="black")

    # Datos
    y_pos, spacing = 12 * mm_to_px, 2 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 3), f"MADE IN SPAIN", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 4), f"CONTAINS FCC ID 2AHN4-WSBRDLR112X, SQG-LYRAP", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 5), f"CONTAINS IC ID 21260-WSBRDLR112X, 3147A-LYRAP", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 7), f"This device complies with part 15 of the FCC Rules. Operation is subjet to the following", font=font_small, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 7.7), f"two conditions: (1) this device mayt not cause harmfil interference, and (2) this device must", font=font_small, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 8.4), f"accept any interference received, including interference that may cause undesired operation.", font=font_small, fill="black")


    # DataMatrix e Iconos
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels).resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(38 * mm_to_px), int(5 * mm_to_px)))
    
    try:
        icons = Image.open(os.path.join(DIRECTORIO_LOGO, "iconos_producto.png")).resize((int(15* mm_to_px), int(5 * mm_to_px)))
        
        label.paste(icons, (int(35 * mm_to_px), int(15 * mm_to_px)))
    except: pass
    
    #output_path = os.path.expanduser("~/labelling_tk_app/output_producto.png")
    output_path = os.path.join(BASE_DIR, "output_producto.png")
    #label = label.resize(int(50 * mm_to_px), int(36 * mm_to_px))
    label.save(output_path)
    return output_path


# --- Funciones de Interfaz ---

def switch_view():
    mode = selected_mode.get()
    for widget in dynamic_container.winfo_children(): widget.destroy()
    
    # Control de visibilidad de botones e interfaz de PRODUCTO
    if mode == 2 or mode == 1: # DISPOSITIVO o Archivo
        ver_producto.grid(row=0, column=2, padx=5)
        imp_producto.grid(row=0, column=3, padx=5)
        product_preview.grid(row=0, column=1, padx=10, pady=10)
    else:
        ver_producto.grid_forget()
        imp_producto.grid_forget()
        product_preview.grid_forget()

    if mode == 1: # ARCHIVO
        tk.Label(dynamic_container, text="Archivo Excel:", font=fuente_labels).grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=file_entry_var, width=60, font=fuente_entradas).grid(row=0, column=1, padx=5)
        tk.Button(dynamic_container, text="...", font=fuente_botones, command=lambda: file_entry_var.set(filedialog.askopenfilename())).grid(row=0, column=2)
        tk.Label(dynamic_container, text="Escanear/Filtrar:", font=fuente_labels).grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=filter_value, width=60, font=fuente_entradas).grid(row=1, column=1)
        tk.Button(dynamic_container, text="Buscar", font=fuente_botones ,command=search_record).grid(row=1, column=2)
    
    elif mode == 2: # DISPOSITIVO
        fields = [("Model:", manual_model), ("Brand:", manual_brand), ("PN:", manual_pn), ("Serial:", manual_sn), ("Batch:", manual_batch)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt, font=fuente_labels).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, font=fuente_entradas, width=50).grid(row=i, column=1, sticky="w")
    
    elif mode == 3: # ACCESORIO
        tk.Label(dynamic_container, text="Model:", font=fuente_labels).grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_model, font=fuente_entradas, width=50).grid(row=0, column=1, sticky="w")
        tk.Label(dynamic_container, text="PN:", font=fuente_labels).grid(row=1, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_pn, font=fuente_entradas, width=50).grid(row=1, column=1, sticky="w")
        tk.Label(dynamic_container, text="Nº Copias:", font=fuente_labels).grid(row=2, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=num_copias_var, font=fuente_entradas, width=10).grid(row=2, column=1, sticky="w")
    
    elif mode == 4: # GW 
        fields = [("Model:", manual_model), ("ERP:", manual_pn), ("SN:", manual_sn), ("MAC:", manual_mac), ("GW ID:", manual_gw_id)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt, font=fuente_labels).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var, font=fuente_entradas, width=50).grid(row=i, column=1, sticky="w")

def search_record():
    file_path = file_entry_var.get()
    filter_val = filter_value.get()
    
    # Limpieza de serial si viene con formato de escáner "X;Y"
    if ";" in filter_val: 
        filter_val = filter_val.split(";")[1]

    try:
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        
        for row in sheet.iter_rows(values_only=True):
            # Comparamos con la columna D (índice 3 en Python) según tu captura
            # Usamos str() por si el Excel lo lee como número (ej. 177487.0)
            if str(filter_val) in str(row[3]):
                # 1. Actualizamos variables de control (Opcional)
                label1_value.set(row[0]) # MODEL
                label2_value.set(row[2]) # PN
                label3_value.set(row[3]) # SERIAL NUMBER
                label4_value.set(row[4]) # BATCH NUMBER
                
                # 2. CRITICO: Actualizamos las variables que usa display_label()
                manual_model.set(row[0])
                manual_brand.set(row[1])
                manual_pn.set(row[2])
                manual_sn.set(row[3])
                manual_batch.set(row[4])
                
                # Forzamos la generación visual de la etiqueta tras la búsqueda
                display_label()
                return

        messagebox.showwarning("No encontrado", f"El serial {filter_val} no existe en el archivo.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al leer el archivo: {e}")

def display_label():
    try:
        mode = selected_mode.get()
        m, p, s = manual_model.get(), manual_pn.get(), manual_sn.get()
        if ";" in s: s = s.split(";")[1]
        
        if mode == 1 or mode == 2:
            path = Impr_Node_packaging_label(f"{p};{s};{manual_batch.get()}", m, manual_brand.get(), p, s)
        elif mode == 3:
            path = Impr_Acc_packaging_label(f"{p}", m, p)
        elif mode == 4:
            path = Impr_GW_packaging_label(f"{p};{s}", m, p, s, manual_mac.get(), manual_gw_id.get())
        
        img = Image.open(path); foto = IMG.PhotoImage(img)
        label_preview.config(image=foto); label_preview.image = foto
    except Exception as e: messagebox.showerror("Error", str(e))

def display_product_label():
    try:
        path = Impr_Node_Product_label(f"{manual_pn.get()};{manual_batch.get()}", manual_model.get(), manual_brand.get(), manual_pn.get())
        img = Image.open(path); foto = IMG.PhotoImage(img)
        product_preview.config(image=foto); product_preview.image = foto
    except Exception as e: messagebox.showerror("Error", str(e))

def print_label():
    mode = selected_mode.get()
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #path = os.path.expanduser("~/labelling_tk_app/output_gw.png") if mode == 4 else os.path.expanduser("~/labelling_tk_app/output_test2.png")
    path = os.path.join(BASE_DIR, "output_gw.png") if mode == 4 else os.path.join(BASE_DIR, "output_test2.png")

    if not os.path.exists(path): return
    try:
        n = int(num_copias_var.get()) if mode == 3 else 1
        for _ in range(n): os.system(f'lp -o orientation-requested=3 -d {IMPRESORA} {path}')
        messagebox.showinfo("Impresión", "Enviado.")
        filter_value.set("")
        # limpiar label_preview
        label_preview.config(image=""); label_preview.image = None
        
    except Exception as e: messagebox.showerror("Error", str(e))

def print_product_label():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    #path = os.path.expanduser("~/labelling_tk_app/output_producto.png")
    path = os.path.join(BASE_DIR, "output_producto.png")
    if os.path.exists(path): os.system(f'lp -d {PRODUCT_PRINTER} {path}')

# --- Setup Principal ---
root = tk.Tk(); root.title("WS Labelling - Rev 3.1")
monitor = get_monitors()[0]; root.geometry(f"{monitor.width}x{monitor.height}")
fuente_labels = tkfont.Font(family="Arial", size=18); fuente_botones = tkfont.Font(family="Arial", size=14, weight="bold"); fuente_entradas = tkfont.Font(family="Arial", size=14)

selected_mode = tk.IntVar(value=1); file_entry_var, filter_value = tk.StringVar(), tk.StringVar()
label1_value, label2_value, label3_value, label4_value = tk.StringVar(value="N/A"), tk.StringVar(value="N/A"), tk.StringVar(value="N/A"), tk.StringVar(value="N/A")
manual_model, manual_brand, manual_pn, manual_sn, manual_batch, manual_mac, manual_gw_id = tk.StringVar(), tk.StringVar(value="LOADSENSING G7"), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()
num_copias_var = tk.StringVar(value="1")

# Header
canvas_logo = tk.Canvas(root, height=90, highlightthickness=0); canvas_logo.pack(fill="x")
try:
    ws_logo_ui = PhotoImage(file=os.path.join(DIRECTORIO_LOGO, "WS_logo.png"))
    canvas_logo.create_image(10, 10, anchor="nw", image=ws_logo_ui)
except: pass

m_frame = tk.LabelFrame(root, text="Tipo de etiqueta", font=fuente_labels, padx=10, pady=5); m_frame.pack(fill="x", padx=20)
for i, txt in enumerate(["Archivo", "Dispositivo Manual", "Accesorio Manual", "GW"], 1):
    tk.Radiobutton(m_frame, text=txt, font=fuente_labels, variable=selected_mode, value=i, command=switch_view).pack(side="left", padx=10)

dynamic_container = tk.Frame(root, pady=15); dynamic_container.pack()

# Botones
b_frame = tk.Frame(root); b_frame.pack(pady=10)
tk.Button(b_frame, text="GENERAR ETIQUETA", bg="#f0f0f0", font=fuente_botones, command=display_label, width=20, height=2).grid(row=0, column=0, padx=5)
tk.Button(b_frame, text="IMPRIMIR", bg="#d1ffd1", font=fuente_botones, command=print_label, width=20, height=2).grid(row=0, column=1, padx=5)
ver_producto = tk.Button(b_frame, text="GENERAR ET. PRODUCTO", bg="#f0f0f0", font=fuente_botones, command=display_product_label, width=25, height=2)
imp_producto = tk.Button(b_frame, text="IMPRIMIR PRODUCTO", bg="#d1ffd1", font=fuente_botones, command=print_product_label, width=20, height=2)

# Previews
preview_frame = tk.Frame(root); preview_frame.pack(pady=10)
label_preview = tk.Label(preview_frame, bg="white", relief="solid", width=700, height=450); label_preview.grid(row=0, column=0, padx=10)
product_preview = tk.Label(preview_frame, bg="white", relief="solid", width=700, height=450)

switch_view(); root.mainloop()