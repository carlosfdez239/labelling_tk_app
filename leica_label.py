'''
Etiqueta de packaging Leica Geosystems AG
Plantilla: DOC-0003950 Rev D (2026-04-13)

Etiqueta 75 x 50 mm a 300 DPI. Todas las posiciones están en mm medidos
desde la esquina superior izquierda de la etiqueta, según el plano.

Elementos fijos (logo, marcas regulatorias, bloque de reciclaje) se cargan
desde imágenes en ASSETS_DIR. Deben ser los ficheros oficiales: el plano
indica que los símbolos tienen que seguir las normas de regulación.
Si falta alguno, se dibuja un recuadro discontinuo y se devuelve un aviso.
'''

import os
import io
import shutil
import datetime
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageChops

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "images", "leica")
OUTPUT_PATH = os.path.join(BASE_DIR, "output_leica.png")

DPI = 300
DPMM = DPI / 25.4          # 11.811 px/mm
LABEL_W_MM, LABEL_H_MM = 75, 50

# --- Textos fijos ---------------------------------------------------------
COMPANY_ADDRESS = [
    "Leica Geosystems AG",
    "Heinrich-Wild-Strasse",
    "CH-9435 Heerbrugg",
    "www.leica-geosystems.com",
]
EU_IMPORTER = [
    "EU Importer: Leica Geosystems GmbH",
    "Vertrieb, Parkring 3, 85748 Garching, DE",
]
GB_IMPORTER = [
    "GB Importer: Leica Geosystems Ltd.",
    "Hexagon House, Michigan Drive,",
    "Tongwell, Milton Keynes, MK15 8HT",
]
# Prefijo cuando no hay nº de serie y se imprime el código de fecha.
# (El plano no lo especifica: confirmar con Leica.)
DATECODE_PREFIX = "Date Code:"

# --- Tamaños del texto pequeño (pt) ----------------------------------------
# El plano los da entre corchetes [ ], es decir, como recomendación.
# El interlineado se calcula solo. Si un texto no cabe en su hueco, se
# reduce automáticamente y se avisa. Máximos que caben con Arial/Liberation
# Narrow: dirección 5,5 pt; importadores 4,5 pt; "Made in" 6 pt (países
# largos, p. ej. United Kingdom).
ADDRESS_PT = 5        # E  - dirección junto al logo (cursiva). Plano: [5 pt]
IMPORTER_PT = 4       # J1, J2 - importadores UE y UK.          Plano: [4 pt]
MADE_IN_PT = 5        # H  - "Made in ...".                      Plano: [5 pt]
LINE_SPACING = 1.2    # interlineado = tamaño x 1,2

# --- Ficheros de imagen fijos (en ASSETS_DIR) -----------------------------
# clave -> (nombres aceptados sin extensión, caja (x, y, ancho, alto) en mm)
# Se busca cada nombre con extensión .png/.svg/.jpg/.webp, sin distinguir
# mayúsculas: "UKCA.svg", "ukca.png"... valen todos.
ASSET_EXTS = (".png", ".svg", ".jpg", ".jpeg", ".webp")
ASSETS = {
    "leica_logo":      (["leica_logo", "leica"],                      (35.0,  2.8, 13.5,  9.0)),  # D  (mín. 12 mm largo)
    "ukca":            (["ukca"],                                     ( 3.0, 22.0,  5.5,  5.0)),  # I1 (mín. 5 mm alto)
    "ce":              (["ce"],                                       (10.5, 22.0,  7.0,  5.0)),  # I2
#    "china_rohs":      (["china_rohs", "rohs"],                       (22.0, 22.0,  5.5,  5.0)),  # I3
#    "weee":            (["weee"],                                     (31.0, 21.0,  5.5,  7.0)),  # I4 (mín. 7 mm alto)
    "recycling_block": (["recycling_block", "recycling_symbol",
                         "recycling"],                                (45.0, 29.5, 26.5, 17.0)),  # O  (26.5 x 17 mm)
}

# --- Fuentes ---------------------------------------------------------------
# Arial Narrow Bold / Italic. Se puede forzar la ruta con config.json
# (LEICA_FONT_BOLD / LEICA_FONT_ITALIC). Si no se encuentra ninguna fuente
# "Narrow", se usa Arial/Liberation normal comprimida horizontalmente.
NARROW_SQUEEZE = 0.82

# Calidad en impresora térmica (solo blanco o negro):
# el texto se dibuja a 4x y se reduce midiendo cuánto cubre cada punto.
# Un punto se imprime si la tinta cubre al menos CUT/255 de su superficie.
# Valores más bajos = trazo más grueso. El texto pequeño (<= 6 pt, dirección
# e importadores) se engrosa un poco para que la cursiva no se pierda.
TEXT_SUPERSAMPLE = 4
TEXT_INK_CUT = 120
SMALL_TEXT_PT = 6
SMALL_TEXT_INK_CUT = 70
# Imágenes (logo, marcas): todo lo que no sea casi blanco se imprime negro.
# Se mira el canal más oscuro, así un logo rojo sale negro sólido.
ASSET_INK_CUT = 170

_FONTS_DIR = os.path.join(BASE_DIR, "fonts")
_BOLD_NARROW = [
    os.path.join(_FONTS_DIR, "ARIALNB.TTF"),
    os.path.join(_FONTS_DIR, "LiberationSansNarrow-Bold.ttf"),
    "C:/Windows/Fonts/ARIALNB.TTF",
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Narrow_Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSansNarrow-Bold.ttf",
]
_ITALIC_NARROW = [
    os.path.join(_FONTS_DIR, "ARIALNI.TTF"),
    os.path.join(_FONTS_DIR, "LiberationSansNarrow-Italic.ttf"),
    "C:/Windows/Fonts/ARIALNI.TTF",
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Narrow_Italic.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSansNarrow-Italic.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSansNarrow-Italic.ttf",
]
_BOLD_WIDE = [
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
_ITALIC_WIDE = [
    "C:/Windows/Fonts/ariali.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
]


def mm(v):
    return int(round(v * DPMM))


def pt(size):
    """Puntos tipográficos -> píxeles a 300 DPI."""
    return int(round(size * DPI / 72))


def _first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


class _Fonts:
    def __init__(self, bold_path=None, italic_path=None):
        self.bold = _first_existing([bold_path] + _BOLD_NARROW)
        self.italic = _first_existing([italic_path] + _ITALIC_NARROW)
        self.squeeze_bold = 1.0
        self.squeeze_italic = 1.0
        if not self.bold:
            self.bold = _first_existing(_BOLD_WIDE)
            self.squeeze_bold = NARROW_SQUEEZE
        if not self.italic:
            self.italic = _first_existing(_ITALIC_WIDE)
            self.squeeze_italic = NARROW_SQUEEZE
        self._cache = {}

    def get(self, style, size_pt):
        key = (style, size_pt)
        if key not in self._cache:
            path = self.bold if style == "bold" else self.italic
            try:
                f = ImageFont.truetype(path, pt(size_pt))
            except Exception:
                f = ImageFont.load_default()
            sq = self.squeeze_bold if style == "bold" else self.squeeze_italic
            self._cache[key] = (f, sq)
        return self._cache[key]

    @property
    def emulated(self):
        return self.squeeze_bold != 1.0 or self.squeeze_italic != 1.0


def _text_width(fonts, text, style, size_pt):
    font, sq = fonts.get(style, size_pt)
    return font.getlength(text) * sq


def _draw_text(label, fonts, x_mm, y_mm, text, style="bold", size_pt=10,
               anchor="l", max_w_mm=None):
    """Dibuja texto con su línea media en y_mm, ya en blanco/negro puro.
    anchor: 'l' = x es el borde izquierdo, 'm' = x es el centro.
    Si max_w_mm está definido y el texto no cabe, reduce el tamaño."""
    size = size_pt
    if max_w_mm:
        while size > 4 and _text_width(fonts, text, style, size) > mm(max_w_mm):
            size -= 0.5
    font, sq = fonts.get(style, size)
    k = TEXT_SUPERSAMPLE
    big = font.font_variant(size=font.size * k)

    left, top, right, bottom = big.getbbox(text, anchor="lm")
    pad = 2 * k
    w, h = right - left + 2 * pad, bottom - top + 2 * pad
    tmp = Image.new("L", (w, h), 0)
    ImageDraw.Draw(tmp).text((pad - left, pad - top), text, font=big, fill=255, anchor="lm")

    # Reducción por área (BOX) + compresión "Narrow" si hace falta, y umbral
    out_w, out_h = max(1, round(w * sq / k)), max(1, round(h / k))
    tmp = tmp.resize((out_w, out_h), Image.BOX)
    cut = SMALL_TEXT_INK_CUT if size <= SMALL_TEXT_PT else TEXT_INK_CUT
    mask = tmp.point(lambda v: 255 if v >= cut else 0)

    x = mm(x_mm) + round((left - pad) * sq / k)
    if anchor == "m":
        x = mm(x_mm) - out_w // 2
    y = mm(y_mm) + round((top - pad) / k)
    label.paste(Image.new("RGB", mask.size, "black"), (x, y), mask)
    return size


# --- Código de barras Code 128 (EN 799) ------------------------------------
_C128 = [
    '11011001100', '11001101100', '11001100110', '10010011000', '10010001100', '10001001100', '10011001000', '10011000100',
    '10001100100', '11001001000', '11001000100', '11000100100', '10110011100', '10011011100', '10011001110', '10111001100',
    '10011101100', '10011100110', '11001110010', '11001011100', '11001001110', '11011100100', '11001110100', '11101101110',
    '11101001100', '11100101100', '11100100110', '11101100100', '11100110100', '11100110010', '11011011000', '11011000110',
    '11000110110', '10100011000', '10001011000', '10001000110', '10110001000', '10001101000', '10001100010', '11010001000',
    '11000101000', '11000100010', '10110111000', '10110001110', '10001101110', '10111011000', '10111000110', '10001110110',
    '11101110110', '11010001110', '11000101110', '11011101000', '11011100010', '11011101110', '11101011000', '11101000110',
    '11100010110', '11101101000', '11101100010', '11100011010', '11101111010', '11001000010', '11110001010', '10100110000',
    '10100001100', '10010110000', '10010000110', '10000101100', '10000100110', '10110010000', '10110000100', '10011010000',
    '10011000010', '10000110100', '10000110010', '11000010010', '11001010000', '11110111010', '11000010100', '10001111010',
    '10100111100', '10010111100', '10010011110', '10111100100', '10011110100', '10011110010', '11110100100', '11110010100',
    '11110010010', '11011011110', '11011110110', '11110110110', '10101111000', '10100011110', '10001011110', '10111101000',
    '10111100010', '11110101000', '11110100010', '10111011110', '10111101110', '11101011110', '11110101110', '11010000100',
    '11010010000', '11010011100',
]
_C128_STOP = '1100011101011'
_START_B, _START_C, _TO_B, _TO_C = 104, 105, 100, 99


def code128_values(data, allow_c=False):
    """Valores de símbolo Code 128. Por defecto juego B puro (lo que pide
    el plano). Con allow_c=True los tramos de >=4 dígitos se codifican en
    juego C (2 dígitos por símbolo) para que quepa en menos espacio."""
    for ch in data:
        if not (32 <= ord(ch) <= 126):
            raise ValueError(f"Carácter no válido para Code 128 B: {ch!r}")

    if not allow_c:
        return [_START_B] + [ord(c) - 32 for c in data]

    # Partir en tramos numéricos / no numéricos
    segs, i = [], 0
    while i < len(data):
        j = i
        if data[i].isdigit():
            while j < len(data) and data[j].isdigit():
                j += 1
            segs.append(("d", data[i:j]))
        else:
            while j < len(data) and not data[j].isdigit():
                j += 1
            segs.append(("t", data[i:j]))
        i = j

    vals, cur = [], None

    def use(cs):
        nonlocal cur
        if cur is None:
            vals.append(_START_C if cs == "C" else _START_B)
        elif cur != cs:
            vals.append(_TO_C if cs == "C" else _TO_B)
        cur = cs

    for kind, s in segs:
        if kind == "d" and len(s) >= 4:
            if len(s) % 2:          # dígito suelto en B, el resto en C
                use("B"); vals.append(ord(s[0]) - 32); s = s[1:]
            use("C")
            vals += [int(s[k:k + 2]) for k in range(0, len(s), 2)]
        else:
            use("B")
            vals += [ord(c) - 32 for c in s]
    return vals


def code128_modules(data, allow_c=False):
    vals = code128_values(data, allow_c)
    check = (vals[0] + sum(v * i for i, v in enumerate(vals[1:], 1))) % 103
    return "".join(_C128[v] for v in vals + [check]) + _C128_STOP


# --- EAN-13 (ISO/IEC 15420) -----------------------------------------------
_EAN_L = ['0001101', '0011001', '0010011', '0111101', '0100011',
          '0110001', '0101111', '0111011', '0110111', '0001011']
_EAN_R = [''.join('1' if b == '0' else '0' for b in c) for c in _EAN_L]
_EAN_G = [c[::-1] for c in _EAN_R]
_EAN_PARITY = ['LLLLLL', 'LLGLGG', 'LLGGLG', 'LLGGGL', 'LGLLGG',
               'LGGLLG', 'LGGGLL', 'LGLGLG', 'LGLGGL', 'LGGLGL']


def ean13_check_digit(d12):
    s = sum(int(c) * (3 if i % 2 else 1) for i, c in enumerate(d12))
    return str((10 - s % 10) % 10)


def ean13_normalize(code):
    """Acepta 12 dígitos (calcula el de control) o 13 (lo verifica)."""
    code = code.strip().replace(" ", "")
    if not code.isdigit() or len(code) not in (12, 13):
        raise ValueError("El EAN debe tener 12 o 13 dígitos.")
    if len(code) == 12:
        return code + ean13_check_digit(code)
    if ean13_check_digit(code[:12]) != code[12]:
        raise ValueError(f"Dígito de control EAN incorrecto (debería ser {ean13_check_digit(code[:12])}).")
    return code


def ean13_modules(code):
    par = _EAN_PARITY[int(code[0])]
    left = "".join((_EAN_L if p == "L" else _EAN_G)[int(d)] for p, d in zip(par, code[1:7]))
    right = "".join(_EAN_R[int(d)] for d in code[7:13])
    return "101" + left + "01010" + right + "101"


def _draw_modules(label, modules, x_mm, y_mm, h_mm, max_w_mm, guard=None):
    """Dibuja barras con ancho de módulo entero en píxeles (lo que mejor
    imprime). Devuelve (ancho_módulo_px, ancho_total_mm)."""
    mod_px = int(mm(max_w_mm) // len(modules))
    if mod_px < 1:
        raise ValueError("El código de barras no cabe en el espacio asignado.")
    draw = ImageDraw.Draw(label)
    x0, y0, y1 = mm(x_mm), mm(y_mm), mm(y_mm + h_mm)
    for i, b in enumerate(modules):
        if b == "1":
            ext = mm(1.2) if guard and guard[i] else 0
            draw.rectangle([x0 + i * mod_px, y0, x0 + (i + 1) * mod_px - 1, y1 + ext], fill="black")
    return mod_px, len(modules) * mod_px / DPMM


def draw_code128(label, data, x_mm, y_mm, h_mm, max_w_mm, warnings):
    modules = code128_modules(data)
    if mm(max_w_mm) // len(modules) < 2:      # módulo < 0,17 mm: difícil de leer
        modules = code128_modules(data, allow_c=True)
        warnings.append(f"'{data}': demasiado largo para Code 128 B puro en {max_w_mm} mm; "
                        "se han usado tramos en juego C para los dígitos.")
    mod_px, _ = _draw_modules(label, modules, x_mm, y_mm, h_mm, max_w_mm)
    if mod_px < 2:
        warnings.append(f"'{data}': módulo de {mod_px} px ({mod_px / DPMM:.2f} mm), "
                        "puede no leerse bien con el escáner.")


def draw_ean13(label, fonts, code, x_mm, y_mm, h_mm, max_w_mm):
    modules = ean13_modules(code)
    guard = [False] * 95
    for i in list(range(0, 3)) + list(range(45, 50)) + list(range(92, 95)):
        guard[i] = True
    mod_px, _ = _draw_modules(label, modules, x_mm, y_mm, h_mm, max_w_mm, guard)
    m = mod_px / DPMM                                  # mm por módulo
    ty = y_mm + h_mm + 0.9
    _draw_text(label, fonts, x_mm - 1.2, ty, code[0], size_pt=7)
    _draw_text(label, fonts, x_mm + 24 * m, ty, code[1:7], size_pt=7, anchor="m")
    _draw_text(label, fonts, x_mm + 71 * m, ty, code[7:], size_pt=7, anchor="m")


# --- Imágenes fijas ---------------------------------------------------------
def _find_asset(assets_dir, names):
    """Busca el fichero sin distinguir mayúsculas ni extensión."""
    try:
        files = {f.lower(): f for f in os.listdir(assets_dir)}
    except OSError:
        return None
    for n in names:
        for ext in ASSET_EXTS:
            f = files.get((n + ext).lower())
            if f:
                return os.path.join(assets_dir, f)
    return None


def _svg_size(path):
    """Ancho/alto intrínsecos del SVG (para conservar la proporción)."""
    import re
    head = open(path, "r", errors="ignore").read(4000)
    m = re.search(r'viewBox\s*=\s*["\']\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', head)
    if m:
        return float(m.group(1)), float(m.group(2))
    w = re.search(r'<svg[^>]*\swidth\s*=\s*["\']([\d.]+)', head)
    h = re.search(r'<svg[^>]*\sheight\s*=\s*["\']([\d.]+)', head)
    if w and h:
        return float(w.group(1)), float(h.group(1))
    return None


def _load_svg(path, box_w, box_h):
    """Rasteriza el SVG al tamaño exacto de la caja (sin pérdida de nitidez).
    Usa cairosvg si está instalado; si no, rsvg-convert."""
    size = _svg_size(path)
    if size:
        k = min(box_w / size[0], box_h / size[1])
        w, h = max(1, int(size[0] * k)), max(1, int(size[1] * k))
    else:
        w, h = box_w, box_h
    try:
        import cairosvg
        png = cairosvg.svg2png(url=path, output_width=w, output_height=h)
    except ImportError:
        if not shutil.which("rsvg-convert"):
            raise RuntimeError("para usar SVG instala cairosvg "
                               "(pip install cairosvg) o librsvg2-bin (rsvg-convert)")
        png = subprocess.run(["rsvg-convert", "-w", str(w), "-h", str(h), path],
                             capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def _is_svg(path):
    """Mira el contenido, no la extensión: hay ficheros .svg que en realidad
    son PNG/JPG renombrados (y al revés)."""
    with open(path, "rb") as f:
        head = f.read(512).lstrip(b"\xef\xbb\xbf").lstrip()
    return head.startswith(b"<?xml") or (head.startswith(b"<") and b"<svg" in head.lower())


def _load_asset(path, box_w, box_h):
    if _is_svg(path):
        img = _load_svg(path, box_w, box_h)
    else:
        img = Image.open(path).convert("RGBA")   # PNG/JPG/WebP, aunque se llame .svg
    # Encajar en la caja manteniendo proporción (también amplía si es pequeña)
    k = min(box_w / img.width, box_h / img.height)
    if abs(k - 1) > 0.01:
        img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
    return _to_solid_ink(img)


def _to_solid_ink(img):
    """Convierte la imagen a tinta negra sólida sobre transparente.
    Evita el granulado: colores (p. ej. el rojo Leica), grises y ruido de
    compresión se convierten en negro limpio o en blanco."""
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    flat = Image.alpha_composite(bg, img).convert("RGB")
    r, g, b = flat.split()
    darkest = ImageChops.darker(ImageChops.darker(r, g), b)     # canal más oscuro
    ink = darkest.point(lambda v: 255 if v < ASSET_INK_CUT else 0)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste((0, 0, 0, 255), (0, 0), ink)
    return out


def _paste_asset(label, key, assets_dir, missing):
    names, (x, y, w, h) = ASSETS[key]
    path = _find_asset(assets_dir, names)
    img = None
    if path:
        try:
            img = _load_asset(path, mm(w), mm(h))
        except Exception as e:
            missing.append(f"{os.path.basename(path)} (no se pudo abrir: {e})")
    else:
        missing.append(f"{names[0]}.png/.svg")

    if img is None:
        draw = ImageDraw.Draw(label)
        x0, y0, x1, y1 = mm(x), mm(y), mm(x + w), mm(y + h)
        for xx in range(x0, x1, 12):
            draw.line([xx, y0, min(xx + 6, x1), y0], fill="#999", width=2)
            draw.line([xx, y1, min(xx + 6, x1), y1], fill="#999", width=2)
        for yy in range(y0, y1, 12):
            draw.line([x0, yy, x0, min(yy + 6, y1)], fill="#999", width=2)
            draw.line([x1, yy, x1, min(yy + 6, y1)], fill="#999", width=2)
        return

    # Se centra en su caja (la transparencia se respeta como máscara)
    px = mm(x) + (mm(w) - img.width) // 2
    py = mm(y) + (mm(h) - img.height) // 2
    label.paste(img, (px, py), img)


# --- Código de fecha YMMY --------------------------------------------------
def date_code_ymmy(date=None):
    """Ejemplo del plano: 26.01.2026 -> 2016
    (decena del año, mes con 2 dígitos, unidad del año)."""
    d = date or datetime.date.today()
    y = d.year % 100
    return f"{y // 10}{d.month:02d}{y % 10}"


# --- Etiqueta completa -------------------------------------------------------
def render_leica_label(pn, product_name, pcs, made_in, serial="", ean="",
                       date=None, assets_dir=ASSETS_DIR, out_path=OUTPUT_PATH,
                       font_bold=None, font_italic=None):
    """Genera la etiqueta. Devuelve (ruta_png, lista_de_avisos).
    Lanza ValueError si algún dato no cumple el formato del plano."""
    pn = str(pn).strip()
    product_name = str(product_name).strip()
    pcs = str(pcs).strip()
    made_in = str(made_in).strip()
    serial = str(serial).strip()
    ean = str(ean).strip()

    if not (pn.isdigit() and len(pn) == 7):
        raise ValueError("El P/N de Leica debe tener exactamente 7 dígitos.")
    if not product_name:
        raise ValueError("Falta el nombre del producto (descripción SAP en inglés).")
    if not (pcs.isdigit() and 1 <= len(pcs) <= 4):
        raise ValueError("Pcs/Sets debe ser un número de hasta 4 dígitos.")
    if not made_in:
        raise ValueError("Falta el país de fabricación (Made in).")
    if ean:
        ean = ean13_normalize(ean)

    warnings, missing = [], []
    fonts = _Fonts(font_bold, font_italic)
    if fonts.emulated:
        warnings.append("No se ha encontrado Arial Narrow: se usa Arial comprimida. "
                        "Instala la fuente o indica la ruta en config.json.")

    label = Image.new("RGB", (mm(LABEL_W_MM), mm(LABEL_H_MM)), "white")
    draw = ImageDraw.Draw(label)

    # A, B, C: P/N, código de barras y número
    # _draw_text(label, fonts, 3.0, 4.7, "P/N:", size_pt=10)
    # draw_code128(label, pn, 9.5, 2.2, 5.0, 22.5, warnings)
    # _draw_text(label, fonts, 9.5, 10.3, pn, size_pt=10)
    _draw_text(label, fonts, 3.0, 3.7, "P/N:", size_pt=10)
    draw_code128(label, pn, 9.5, 1.5, 5.0, 21.2, warnings)
    _draw_text(label, fonts, 9.5, 8.5, pn, size_pt=10)

    # D, E: logo y dirección dentro de su recuadro
    draw.rectangle([mm(34), mm(1.8), mm(72), mm(13)], outline="black", width=3)
    _paste_asset(label, "leica_logo", assets_dir, missing)
    def lead(size):                       # interlineado en mm
        return size * 25.4 / 72 * LINE_SPACING

    def check(what, wanted, got):
        if got < wanted:
            warnings.append(f"{what}: {wanted} pt no cabe, se ha reducido a {got} pt.")

    # Dirección centrada verticalmente en el recuadro (1,8 a 13 mm)
    y0 = 7.4 - lead(ADDRESS_PT) * (len(COMPANY_ADDRESS) - 1) / 2
    used = min(_draw_text(label, fonts, 60.8, y0 + i * lead(ADDRESS_PT), line, style="italic",
                          size_pt=ADDRESS_PT, anchor="m", max_w_mm=21)
               for i, line in enumerate(COMPANY_ADDRESS))
    check("Dirección", ADDRESS_PT, used)

    # F: nombre del producto
    _draw_text(label, fonts, 3.0, 14.8, product_name, size_pt=10, max_w_mm=69)

    # G, H: Pcs/Sets y Made in
    _draw_text(label, fonts, 3.0, 18.5, f"Pcs/Sets: {pcs}", size_pt=8)
    used = _draw_text(label, fonts, 22.5, 18.7, f"Made in {made_in}", size_pt=MADE_IN_PT, max_w_mm=21.5)
    check("Made in", MADE_IN_PT, used)

    # J1, J2: importadores
    # La primera línea de cada bloque se queda en su sitio y crece hacia abajo
    used = min(_draw_text(label, fonts, 45.5, 17.4 + i * lead(IMPORTER_PT), line,
                          size_pt=IMPORTER_PT, max_w_mm=27)
               for i, line in enumerate(EU_IMPORTER))
    used = min([used] + [_draw_text(label, fonts, 45.5, 23.2 + i * lead(IMPORTER_PT), line,
                                    size_pt=IMPORTER_PT, max_w_mm=27)
                         for i, line in enumerate(GB_IMPORTER)])
    check("Importadores", IMPORTER_PT, used)

    # I1..I4: marcas regulatorias y O: bloque de reciclaje
    #for key in ("ukca", "ce", "china_rohs", "weee", "recycling_block"):
    for key in ("ukca", "ce", "recycling_block"):
        _paste_asset(label, key, assets_dir, missing)

    # K, L: EAN (solo B2C)
    if ean:
        _draw_text(label, fonts, 3.0, 31.8, "EAN:", size_pt=10)
        draw_ean13(label, fonts, ean, 11.5, 29.5, 5.0, 25.0)

    # M, N: nº de serie o, si no hay, código de fecha YMMY
    if serial:
        text, bc = f"S/N: {serial}", serial
    else:
        dc = date_code_ymmy(date)
        text, bc = f"{DATECODE_PREFIX} {dc}", dc
    #_draw_text(label, fonts, 3.0, 39.6, text, size_pt=9, max_w_mm=41)
    _draw_text(label, fonts, 3.0, 38.0, text, size_pt=9, max_w_mm=41)
    #draw_code128(label, bc, 3.0, 41.4, 5.0, 39.0, warnings)
    draw_code128(label, bc, 3.0, 39.5, 5.0, 37.5, warnings)

    if missing:
        warnings.append("Faltan imágenes en " + assets_dir + ": " + ", ".join(missing))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    label.save(out_path, dpi=(DPI, DPI))
    return out_path, warnings


# --- Impresión en Brother QL (QL-820NWB) ------------------------------------
# La QL imprime a 300 dpi y no llega al borde del rollo:
#   rollo 50 mm (DK-22223): 554 puntos imprimibles = 46,9 mm
#   rollo 62 mm (DK-22205): 696 puntos imprimibles = 58,9 mm
# Se gira 90° (75 mm a lo largo del rollo) y se recorta el margen blanco del
# lado de 50 mm hasta el ancho imprimible, SIN reescalar: el contenido de la
# etiqueta va de 1,8 a 46,5 mm y cabe entero. Si el recorte fuese a quitar
# algo impreso, se detiene con un error en vez de imprimir mal.
QL_TAPE_DOTS = {"50": 554, "62": 696, "62red": 696}
# En rollo continuo la impresora añade un avance en blanco de 35 puntos
# (2,96 mm) al principio y al final de cada etiqueta: 75 + 2x3 = 81 mm.
# La etiqueta ya trae 3 mm de blanco en cada extremo, así que se recortan
# esos 35 puntos y el avance de la impresora ocupa su lugar: 75 mm exactos y
# el contenido queda a la misma distancia del borde que en el plano.
QL_FEED_MARGIN_DOTS = 35


def _crop_checked(im, box, what):
    """Recorta comprobando que no se pierde ningún píxel negro."""
    kept = im.crop(box)
    lost = (im.histogram()[0] - kept.histogram()[0])
    if lost > 0:
        raise ValueError(f"Al ajustar {what} se perderían {lost} píxeles impresos. "
                         "Revisa el giro, el rollo o LEICA_QL_TRIM_MM.")
    return kept


def make_ql_bitmap(src_path, tape="50", rotate=90, threshold=128, trim_mm=0.0,
                   out_path=None, trim_dots=None):
    """Prepara la etiqueta para la QL: girada, 1 bit, ajustada al ancho
    imprimible del rollo. trim_mm recorta blanco en cada extremo del largo
    (para compensar el margen de avance que añade la impresora).
    Devuelve una imagen 'L' con solo 0/255."""
    if tape not in QL_TAPE_DOTS:
        raise ValueError(f"Rollo '{tape}' no soportado (usa: {', '.join(QL_TAPE_DOTS)}).")
    dots = QL_TAPE_DOTS[tape]
    im = Image.open(src_path).convert("L")
    if rotate:
        im = im.rotate(rotate, expand=True)
    im = im.point(lambda v: 0 if v < threshold else 255)

    t = trim_dots if trim_dots is not None else (mm(trim_mm) if trim_mm else 0)
    if t:
        im = _crop_checked(im, (0, t, im.width, im.height - t), "el largo")

    if im.width > dots:                      # recorte centrado del lado de 50 mm
        left = (im.width - dots) // 2
        im = _crop_checked(im, (left, 0, left + dots, im.height), f"al rollo de {tape} mm")
    elif im.width < dots:                    # centrar en rollos más anchos
        canvas = Image.new("L", (dots, im.height), 255)
        canvas.paste(im, ((dots - im.width) // 2, 0))
        im = canvas

    if out_path:
        im.convert("1").save(out_path, dpi=(DPI, DPI))
    return im


def print_brother_ql(src_path, printer, model="QL-820NWB", tape="50", copies=1,
                     rotate=90, threshold=128, trim_mm=None):
    """Imprime directamente en la Brother sin pasar por CUPS.
    printer: 'tcp://192.168.1.50' (red), 'file:///dev/usb/lp0' (USB) o
             'usb://0x04f9:0x209d' (USB con pyusb).
    Necesita: pip install brother_ql"""
    try:
        from brother_ql.raster import BrotherQLRaster
        from brother_ql.conversion import convert
        from brother_ql.backends.helpers import send
    except ImportError:
        raise RuntimeError("Falta la librería brother_ql: pip install brother_ql")

    # trim_mm=None -> automático: compensa el avance de la impresora (75 mm exactos)
    img = make_ql_bitmap(src_path, tape=tape, rotate=rotate, threshold=threshold,
                         trim_mm=trim_mm or 0,
                         trim_dots=QL_FEED_MARGIN_DOTS if trim_mm is None else None)
    qlr = BrotherQLRaster(model)
    qlr.exception_on_warning = True
    # rotate=0 y ancho exacto del rollo: brother_ql no reescala nada
    instructions = convert(qlr=qlr, images=[img] * max(1, int(copies)), label=tape,
                           rotate=0, threshold=50.0, dither=False, compress=True,
                           red=(tape == "62red"), dpi_600=False, hq=True, cut=True)
    status = send(instructions=instructions, printer_identifier=printer, blocking=True)
    if status.get("outcome") == "error":
        raise RuntimeError(f"La impresora ha devuelto un error: {status.get('printer_state')}")
    return status


if __name__ == "__main__":
    p, w = render_leica_label("1234567", "GS18 I GNSS RTK Rover", "1", "Spain",
                              serial="177487", ean="761234567890")
    print(p)
    for x in w:
        print("AVISO:", x)
