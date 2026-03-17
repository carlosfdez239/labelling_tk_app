'''
C. Fdez
Rev 3.0 --> 16/03/2026
- Nueva funcionalidad: Generación manual de etiquetas para Dispositivos y Accesorios.
- Integración de campo 'BRAND'.
- Implementación de impresión múltiple (bucle) para Accesorios.
- Ajuste de DataMatrix y Logo oficial.
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
DIRECTORIO_LOGO = config.get("DIRECTORIO_LOGO", "")
RUBIK_FONT_PATH = os.path.expanduser("~/.local/share/fonts/Rubik-Light.ttf")
BATCH_N = config.get("batch", "")

# --- Lógica de Generación de Etiqueta ---

def Impr_Node_packaging_label(datam, Model, Brand, ERP_Code, Serial_N):
    mm_to_px = 11.81  # 300 DPI
    width, height = int(50 * mm_to_px), int(45 * mm_to_px)
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)

    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except:
        font_main = font_small = ImageFont.load_default()

    # Logo e Info
    try:
        logo_path = "/home/ws-prod23/labelling_tk_app/images/W_Label_Devices_new.png"
        logo = Image.open(logo_path).resize((int(42 * mm_to_px), int(8 * mm_to_px)))
        label.paste(logo, (0, 0))
    except: pass

    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    # Datos
    y_pos, spacing = 14 * mm_to_px, 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing), f"BRAND:  {Brand}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 3), f"SERIAL NUMBER:  {Serial_N}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 4), f"BATCH NUMBER:  {manual_batch.get()}", font=font_main, fill="black")

    # DataMatrix e Iconos
    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels).resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(36 * mm_to_px), int(10 * mm_to_px)))
    
    try:
        icons = Image.open(os.path.join(DIRECTORIO_LOGO, "iconos.png"))
        label.paste(icons, (int(34 * mm_to_px), int(20 * mm_to_px)))
    except: pass
    
    output_path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    label.save(output_path)
    return output_path

def Impr_Acc_packaging_label(datam, Model, ERP_Code):
    mm_to_px = 11.81
    width, height = int(50 * mm_to_px), int(45 * mm_to_px)
    label = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(label)

    try:
        font_main = ImageFont.truetype(RUBIK_FONT_PATH, 26)
        font_small = ImageFont.truetype(RUBIK_FONT_PATH, 18)
    except:
        font_main = font_small = ImageFont.load_default()

    try:
        logo_path = "/home/ws-prod23/labelling_tk_app/images/W_Label_Devices_new.png"
        logo = Image.open(logo_path).resize((int(42 * mm_to_px), int(8 * mm_to_px)))
        label.paste(logo, (0, 0))
    except: pass

    draw.text((1 * mm_to_px, 7 * mm_to_px), "Viriat 47, 10th Floor, 08014 Barcelona, Spain", font=font_small, fill="black")

    y_pos, spacing = 14 * mm_to_px, 3 * mm_to_px
    draw.text((1 * mm_to_px, y_pos), f"MODEL:  {Model}", font=font_main, fill="black")
    draw.text((1 * mm_to_px, y_pos + spacing * 2), f"PN:  {ERP_Code}", font=font_main, fill="black")

    encoded = encode(datam.encode('utf8'))
    dmtx = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels).resize((int(10 * mm_to_px), int(10 * mm_to_px)))
    label.paste(dmtx, (int(34 * mm_to_px), int(10 * mm_to_px)))
    
    try:
        icons = Image.open(os.path.join(DIRECTORIO_LOGO, "iconos.png"))
        label.paste(icons, (int(34 * mm_to_px), int(20 * mm_to_px)))
    except: pass
    
    output_path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    label.save(output_path)
    return output_path

# --- Funciones Interfaz ---

def switch_view():
    mode = selected_mode.get()
    for widget in dynamic_container.winfo_children():
        widget.destroy()
    
    if mode == 1:
        tk.Label(dynamic_container, text="Archivo Excel:", font=fuente_labels).grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=file_entry_var, width=60, font=fuente_entradas).grid(row=0, column=1, padx=5)
        tk.Button(dynamic_container, text="...", font=fuente_botones, command=lambda: file_entry_var.set(filedialog.askopenfilename())).grid(row=0, column=2)
        tk.Label(dynamic_container, text="Escanear/Filtrar:", font=fuente_labels).grid(row=1, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=filter_value, width=60, font=fuente_entradas).grid(row=1, column=1)
        tk.Button(dynamic_container, text="Buscar", font=fuente_botones ,command=search_record).grid(row=1, column=2)
    elif mode == 2:
        fields = [("Model:", manual_model), ("Brand:", manual_brand), ("PN:", manual_pn), ("Serial:", manual_sn), ("Batch:", manual_batch)]
        for i, (txt, var) in enumerate(fields):
            tk.Label(dynamic_container, text=txt, font=fuente_labels).grid(row=i, column=0, sticky="w", pady=2)
            tk.Entry(dynamic_container, textvariable=var,font=fuente_entradas, width=50).grid(row=i, column=1, sticky="w")
    elif mode == 3:
        tk.Label(dynamic_container, text="Model:", font=fuente_labels).grid(row=0, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_model,font=fuente_entradas, width=50).grid(row=0, column=1, sticky="w")
        tk.Label(dynamic_container, text="PN:", font=fuente_labels).grid(row=1, column=0, sticky="w")
        tk.Entry(dynamic_container, textvariable=manual_pn, font=fuente_entradas, width=50).grid(row=1, column=1, sticky="w")
        tk.Label(dynamic_container, text="Nº Copias:", font=fuente_labels).grid(row=2, column=0, sticky="w", pady=10)
        tk.Entry(dynamic_container, textvariable=num_copias_var, font= fuente_entradas, width=10).grid(row=2, column=1, sticky="w")

def search_record():
    file_path, filter_val = file_entry_var.get(), filter_value.get()
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
        if mode == 1:
            brand, m, p, s = manual_brand.get(), label1_value.get(), label2_value.get(), label3_value.get()
            datam = f"{m};{s};{BATCH_N}"
            path = Impr_Node_packaging_label(datam, m, brand, p, s)
        elif mode == 2:
            brand, m, p = manual_brand.get(), manual_model.get(), manual_pn.get(),
            s =  manual_sn.get()
            #print(f"valor leido para el serial --> {s}\n")
            s = s.split(";")[1]
            #print(f"valor transformado para el serial --> {s}\n")
            b = manual_batch.get() if manual_batch.get() else BATCH_N
            datam = f"{p};{s};{b}"
            path = Impr_Node_packaging_label(datam, m, brand, p, s)
        else:
            m, p = manual_model.get(), manual_pn.get()
            datam = f"{p}"
            path = Impr_Acc_packaging_label(datam, m, p)
        
        img = Image.open(path)
        foto = IMG.PhotoImage(img)
        label_preview.config(image=foto); label_preview.image = foto
    except Exception as e: messagebox.showerror("Error", str(e))

def print_label():
    path = os.path.expanduser("~/labelling_tk_app/output_test2.png")
    if not os.path.exists(path): return
    
    try:
        # Lógica de copias
        n_copias = 1
        if selected_mode.get() == 3:
            try:
                n_copias = int(num_copias_var.get())
            except: n_copias = 1
            
        for i in range(n_copias):
            os.system(f'lp -o orientation-requested=3 -d {IMPRESORA} {path}')
            
        messagebox.showinfo("Impresión", f"Enviado correctamente ({n_copias} copias).")
        for v in [manual_model, manual_pn, manual_sn, filter_value]: v.set("")
        num_copias_var.set("1")
    except Exception as e: messagebox.showerror("Error", str(e))

# --- Setup Principal ---
root = tk.Tk()
root.title("WS Labelling - Rev 3.0")
monitor = get_monitors()[0]
root.geometry(f"{monitor.width}x{monitor.height}")

fuente_labels = tkfont.Font(family="Arial", size=30, weight="normal")
fuente_botones = tkfont.Font(family="Arial", size=30, weight="bold")
fuente_entradas = tkfont.Font(family="Arial", size=20)

selected_mode = tk.IntVar(value=1)
file_entry_var, filter_value = tk.StringVar(), tk.StringVar()
label1_value, label2_value, label3_value = tk.StringVar(value="N/A"), tk.StringVar(value="N/A"), tk.StringVar(value="N/A")
manual_model, manual_brand, manual_pn, manual_sn, manual_batch = tk.StringVar(), tk.StringVar(value="LOADSENSING G7",), tk.StringVar(), tk.StringVar(), tk.StringVar()
num_copias_var = tk.StringVar(value="1")

# Header UI
canvas_logo = tk.Canvas(root, height=70, highlightthickness=0); canvas_logo.pack(fill="x")
try:
    ws_logo_ui = PhotoImage(file=os.path.join(DIRECTORIO_LOGO, "WS_logo.png"))
    canvas_logo.create_image(10, 10, anchor="nw", image=ws_logo_ui)
except: pass

m_frame = tk.LabelFrame(root, text="Tipo de etiqueta", font=fuente_labels ,padx=10, pady=5); m_frame.pack(fill="x", padx=20)
for i, txt in enumerate(["Archivo", "Dispositivo Manual", "Accesorio Manual"], 1):
    tk.Radiobutton(m_frame, text=txt, font=fuente_labels ,variable=selected_mode, value=i, command=switch_view).pack(side="left", padx=10)

dynamic_container = tk.Frame(root, pady=15); dynamic_container.pack()

b_frame = tk.Frame(root); b_frame.pack(pady=10)
tk.Button(b_frame, text="GENERAR ETIQUETA", bg="#f0f0f0", font=fuente_botones,command=display_label, width=20, height=2).pack(side="left", padx=5)
tk.Button(b_frame, text="IMPRIMIR", bg="#d1ffd1", font=fuente_botones,command=print_label, width=20, height=2).pack(side="left", padx=5)

label_preview = tk.Label(root, bg="white", relief="solid", width=650, height=450); label_preview.pack(pady=10)

switch_view()
root.mainloop()