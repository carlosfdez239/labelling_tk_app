'''
Etiqueta de PRODUCTO WS ComBox70 (63 x 50 mm).

Se dibuja directamente a la resolución de la impresora (parámetro dpmm de
render_product_label: 8 = 203 dpi, 12 = 300 dpi de Zebra; por defecto la de
la QL, 300 dpi). Así no hay que reescalar la imagen al imprimir y el texto
pequeño sale nítido.

Dibuja los templates de WS_product_templates.py (uno por variante: EU y
ROW). Reutiliza de WS_label.py la carga de imágenes (PNG/SVG, conversión
a tinta sólida) y la impresión en la Brother QL.

assets_dir puede ser una carpeta o una lista de carpetas: cada imagen se
toma de la primera en la que aparezca.

Requiere: pip install qrcode
'''

import os
from PIL import Image, ImageDraw, ImageFont

import WS_label as LL
from WS_product_templates import TEMPLATES, ASSET_NAMES, LABEL_W_MM, LABEL_H_MM

DPI = LL.DPI                # resolución por defecto (QL, 300 dpi)

# Resolución activa del render (puntos por mm). render_product_label la fija
# mientras dibuja; todas las medidas pasan por mm() y _pt().
_DPMM = LL.DPMM


def mm(v):
    return int(round(v * _DPMM))


def _pt(size):
    """Puntos tipográficos -> píxeles a la resolución activa."""
    return int(round(size * _DPMM * 25.4 / 72))


# El QR puede pasarse un poco de su caja para no tener que bajar a un módulo
# más pequeño (a 203 dpi, 7,6 mm = 60 puntos no da para módulos de 3).
QR_OVERSIZE_MM = 0.4
ASSETS_DIR = [os.path.join(LL.ASSETS_DIR, "ws"), os.path.join(LL.ASSETS_DIR, "leica"), LL.ASSETS_DIR]
OUTPUT_PATH = os.path.join(LL.BASE_DIR, "output_ws_producto.png")

# Texto: dibujado a 4x y reducido por área, igual que en la de packaging.
TEXT_SUPERSAMPLE = 4
TEXT_INK_CUT = 120
SMALL_TEXT_PT = 6
SMALL_TEXT_INK_CUT = 70
MIN_TEXT_PT = 3.0           # nunca se reduce por debajo de esto

# --- Fuentes (sans normal, no "Narrow") -------------------------------------
_FONTS_DIR = os.path.join(LL.BASE_DIR, "fonts")
_REGULAR = [
    os.path.join(_FONTS_DIR, "arial.ttf"),
    os.path.join(_FONTS_DIR, "LiberationSans-Regular.ttf"),
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
_BOLD = [
    os.path.join(_FONTS_DIR, "arialbd.ttf"),
    os.path.join(_FONTS_DIR, "LiberationSans-Bold.ttf"),
    "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


class _Fonts:
    def __init__(self, regular=None, bold=None):
        first = lambda paths: next((p for p in paths if p and os.path.exists(p)), None)
        self.paths = {"regular": first([regular] + _REGULAR), "bold": first([bold] + _BOLD)}
        self._cache = {}

    def get(self, style, size_pt, scale=1):
        key = (style, size_pt, scale)
        if key not in self._cache:
            px = max(1, round(_pt(size_pt) * scale))
            try:
                self._cache[key] = ImageFont.truetype(self.paths[style], px)
            except Exception:
                self._cache[key] = ImageFont.load_default()
        return self._cache[key]

    def width_mm(self, runs, size_pt):
        return sum(self.get(st, size_pt).getlength(t) for st, t in runs) / _DPMM


# --- Dibujo de texto -------------------------------------------------------
def _draw_runs(label, fonts, x_mm, y_mm, runs, size_pt, anchor="l"):
    """Una línea con tramos de distinto estilo. y_mm = línea media."""
    k = TEXT_SUPERSAMPLE
    big = [(fonts.get(st, size_pt, k), t) for st, t in runs if t]
    if not big:
        return
    widths = [f.getlength(t) for f, t in big]
    total = sum(widths)
    asc = max(f.getmetrics()[0] for f, _ in big)
    desc = max(f.getmetrics()[1] for f, _ in big)
    pad = 2 * k
    w, h = int(total) + 2 * pad, asc + desc + 2 * pad
    tmp = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(tmp)
    cx = pad
    for (f, t), fw in zip(big, widths):
        d.text((cx, pad + asc), t, font=f, fill=255, anchor="ls")
        cx += fw
    out_w, out_h = max(1, round(w / k)), max(1, round(h / k))
    tmp = tmp.resize((out_w, out_h), Image.BOX)
    cut = SMALL_TEXT_INK_CUT if size_pt <= SMALL_TEXT_PT else TEXT_INK_CUT
    mask = tmp.point(lambda v: 255 if v >= cut else 0)

    text_w = total / k
    x0 = mm(x_mm) - pad // k
    if anchor == "m":
        x0 -= round(text_w / 2)
    elif anchor == "r":
        x0 -= round(text_w)
    # línea media entre la línea base y la altura de las mayúsculas
    cap = asc * 0.72 / k
    y0 = mm(y_mm) - round(pad / k + asc / k - cap / 2)
    label.paste(Image.new("RGB", mask.size, "black"), (x0, y0), mask)


def _fit_size(fonts, rows, size_pt, max_w_mm):
    """Mayor tamaño <= size_pt con el que todas las filas caben en max_w_mm."""
    size = size_pt
    while max_w_mm and size > MIN_TEXT_PT and \
            max(fonts.width_mm(r, size) for r in rows) > max_w_mm:
        size = round(size - 0.1, 2)
    return size


def _wrap(fonts, text, style, size_pt, width_mm):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if cur and fonts.width_mm([(style, trial)], size_pt) > width_mm:
            lines.append(cur)
            cur = wd
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


# --- Otros elementos -------------------------------------------------------
def _draw_qr(label, data, x_mm, y_mm, size_mm):
    try:
        import qrcode
    except ImportError:
        raise RuntimeError("Falta la librería qrcode: pip install qrcode")
    qr = qrcode.QRCode(border=0, box_size=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    n = len(matrix)
    mod = (mm(size_mm) + mm(QR_OVERSIZE_MM)) // n   # módulo entero en puntos: QR nítido
    if mod < 2:
        raise ValueError("El contenido del QR es demasiado largo para su tamaño.")
    side = mod * n
    ox = mm(x_mm) + (mm(size_mm) - side) // 2
    oy = mm(y_mm) + (mm(size_mm) - side) // 2
    draw = ImageDraw.Draw(label)
    for r, row in enumerate(matrix):
        for c, v in enumerate(row):
            if v:
                draw.rectangle([ox + c * mod, oy + r * mod,
                                ox + (c + 1) * mod - 1, oy + (r + 1) * mod - 1], fill="black")


def _draw_dc_symbol(label, x_mm, y_mm, w_mm):
    """IEC 60417-5031: línea continua arriba y tres trazos debajo."""
    draw = ImageDraw.Draw(label)
    t = max(2, mm(0.3))
    x0, x1 = mm(x_mm), mm(x_mm + w_mm)
    y_top, y_bot = mm(y_mm - 0.45), mm(y_mm + 0.45)
    draw.rectangle([x0, y_top, x1, y_top + t - 1], fill="black")
    gap = (x1 - x0) * 0.14
    dash = ((x1 - x0) - 2 * gap) / 3
    for i in range(3):
        a = x0 + i * (dash + gap)
        draw.rectangle([round(a), y_bot, round(a + dash), y_bot + t - 1], fill="black")


def _as_dirs(assets_dir):
    if isinstance(assets_dir, (list, tuple)):
        return [d for d in assets_dir if d]
    return [assets_dir]


def _find_asset(assets_dir, names):
    for d in _as_dirs(assets_dir):
        p = LL._find_asset(d, names)
        if p:
            return p
    return None


def _load_ink_trimmed(path, box_w, box_h, crop=None):
    """Carga la imagen y la recorta por la TINTA que se imprime, no por el
    blanco: un fondo o marco gris claro (que desaparece al pasar a blanco y
    negro) ya no ocupa sitio. Se procesa a 4x y se reduce por área, igual que
    el texto, para que los trazos queden limpios."""
    k = 4
    big = LL._load_asset(path, box_w * k, box_h * k, trim=True, crop=crop)
    bbox = big.getchannel("A").getbbox()
    if bbox:
        big = big.crop(bbox)
    s = min(box_w / big.width, box_h / big.height)
    size = (max(1, round(big.width * s)), max(1, round(big.height * s)))
    alpha = big.getchannel("A").resize(size, Image.BOX).point(lambda v: 255 if v >= 128 else 0)
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste((0, 0, 0, 255), (0, 0), alpha)
    return out


def _draw_asset(label, name, box, align, assets_dir, missing, trim=True, crop=None):
    x, y, w, h = box
    path = _find_asset(assets_dir, ASSET_NAMES.get(name, [name]))
    img = None
    if path:
        try:
            if trim == "ink":              # recorte por la tinta impresa
                img = _load_ink_trimmed(path, mm(w), mm(h), crop=crop)
            else:
                img = LL._load_asset(path, mm(w), mm(h), trim=trim, crop=crop)
        except Exception as e:
            missing.append(f"{os.path.basename(path)} (no se pudo abrir: {e})")
    else:
        names = ASSET_NAMES.get(name, [name])
        missing.append(f"{name} (nombres aceptados: {', '.join(names)})")
    if img is None:                        # recuadro discontinuo (solo preview)
        draw = ImageDraw.Draw(label)
        x0, y0, x1, y1 = mm(x), mm(y), mm(x + w), mm(y + h)
        for xx in range(x0, x1, 10):
            draw.line([xx, y0, min(xx + 5, x1), y0], fill="#999", width=2)
            draw.line([xx, y1, min(xx + 5, x1), y1], fill="#999", width=2)
        for yy in range(y0, y1, 10):
            draw.line([x0, yy, x0, min(yy + 5, y1)], fill="#999", width=2)
            draw.line([x1, yy, x1, min(yy + 5, y1)], fill="#999", width=2)
        return
    px = mm(x) if align == "l" else mm(x) + (mm(w) - img.width) // 2
    py = mm(y) + (mm(h) - img.height) // 2
    label.paste(img, (px, py), img)


# --- Validación ----------------------------------------------------------------
def imei_is_valid(imei):
    if not (imei.isdigit() and len(imei) == 15):
        return False
    s = 0
    for i, ch in enumerate(reversed(imei)):
        d = int(ch)
        if i % 2:
            d *= 2
            if d > 9:
                d -= 9
        s += d
    return s % 10 == 0


# --- Etiqueta completa -------------------------------------------------------
def render_product_label(variant, imei, serial, assets_dir=ASSETS_DIR,
                         out_path=OUTPUT_PATH, font_regular=None, font_bold=None, dpmm=None):
    """Genera la etiqueta de producto. variant: 'EU' o 'ROW'.
    dpmm: resolución del render en puntos/mm (8 = Zebra 203 dpi, 12 = Zebra
    300 dpi). None = la de la QL (300 dpi).
    Devuelve (ruta_png, avisos). Lanza ValueError si los datos no son válidos."""
    global _DPMM
    prev = _DPMM
    _DPMM = float(dpmm) if dpmm else LL.DPMM
    try:
        return _render(variant, imei, serial, assets_dir, out_path, font_regular, font_bold)
    finally:
        _DPMM = prev


def _render(variant, imei, serial, assets_dir, out_path, font_regular, font_bold):
    if variant not in TEMPLATES:
        raise ValueError(f"Variante desconocida '{variant}' (disponibles: {', '.join(TEMPLATES)}).")
    tpl = TEMPLATES[variant]

    imei = str(imei).strip().replace(" ", "")
    serial = str(serial).strip()
    if ";" in serial:                      # lectura de escáner "XX;serie"
        serial = serial.split(";")[1].strip()
    if not imei_is_valid(imei):
        raise ValueError("IMEI no válido: deben ser 15 dígitos con el dígito de control correcto.")
    if not serial:
        raise ValueError("Falta el nº de serie.")
    if any(not (32 <= ord(c) <= 126) for c in serial):
        raise ValueError("El nº de serie contiene caracteres no válidos.")

    data = dict(tpl["fixed"], imei=imei, serial=serial)

    def fmt(s):
        try:
            return s.format(**data)
        except KeyError as e:
            raise ValueError(f"El template {variant} usa el campo {{{e.args[0]}}}, que no está "
                             f"definido en su 'fixed' (disponibles: {', '.join(sorted(data))}).") from None

    fonts = _Fonts(font_regular, font_bold)
    warnings, missing = [], []
    label = Image.new("RGB", (mm(LABEL_W_MM), mm(LABEL_H_MM)), "white")
    draw = ImageDraw.Draw(label)

    dx, dy = tpl.get("offset", (0.0, 0.0))

    def shifted(el):
        el = dict(el)
        if "x" in el:
            el["x"] += dx
        if "y" in el:
            el["y"] += dy
        if "box" in el:
            x, y, w, h = el["box"]
            el["box"] = (x + dx, y + dy, w, h)
        return el

    for el in map(shifted, tpl["elements"]):
        t = el["type"]
        if t == "asset":
            _draw_asset(label, el["name"], el["box"], el.get("align", "c"), assets_dir, missing,
                        trim=el.get("trim", True), crop=el.get("crop"))

        elif t == "text":
            runs = [(st, fmt(tx)) for st, tx in el["runs"]]
            size = _fit_size(fonts, [runs], el["size"], el.get("max_w"))
            _draw_runs(label, fonts, el["x"], el["y"], runs, size, el.get("anchor", "l"))

        elif t == "lines":
            rows = [[(el["style"], fmt(l))] for l in el["lines"]]
            size = _fit_size(fonts, rows, el["size"], el.get("max_w"))
            if size < el["size"] - 0.3:
                warnings.append(f"'{el['lines'][0][:25]}…' reducido a {size} pt para que quepa.")
            for i, r in enumerate(rows):
                _draw_runs(label, fonts, el["x"], el["y"] + i * el["lead"], r, size)

        elif t == "paragraph":
            x, y, w, h = el["box"]
            size, lead = el["size"], el["lead"]
            while True:
                lines = _wrap(fonts, fmt(el["text"]), el["style"], size, w)
                if len(lines) * lead <= h + 0.01 or size <= MIN_TEXT_PT:
                    break
                size = round(size - 0.1, 2)
                lead = el["lead"] * size / el["size"]
            if size < el["size"] - 0.3:
                warnings.append(f"Párrafo reducido a {size} pt para que quepa.")
            for i, ln in enumerate(lines):
                _draw_runs(label, fonts, x, y + lead / 2 + i * lead, [(el["style"], ln)], size)

        elif t == "rbox":
            x, y, w, h = el["box"]
            draw.rounded_rectangle([mm(x), mm(y), mm(x + w), mm(y + h)],
                                   radius=mm(el.get("radius", 1.0)),
                                   outline="black", width=max(2, mm(el.get("line", 0.3))))

        elif t == "hline":
            th = max(1, mm(el.get("line", 0.3)))
            y0 = mm(el["y"]) - th // 2
            draw.rectangle([mm(el["x"]), y0, mm(el["x"] + el["w"]) - 1, y0 + th - 1], fill="black")

        elif t == "qr":
            _draw_qr(label, fmt(el["data"]), el["x"], el["y"], el["size"])

        elif t == "dc_symbol":
            x = el["x"]
            if "after" in el:
                st, txt, sz = el["after"]
                x += fonts.width_mm([(st, fmt(txt))], sz) + el.get("gap", 0.8)
            _draw_dc_symbol(label, x, el["y"], el["w"])

        else:
            raise ValueError(f"Tipo de elemento desconocido en el template: {t}")

    if missing:
        warnings.append("Faltan imágenes en " + " | ".join(_as_dirs(assets_dir)) + ": " + ", ".join(missing))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    dpi = round(_DPMM * 25.4)
    label.save(out_path, dpi=(dpi, dpi))
    return out_path, warnings


if __name__ == "__main__":
    for v in TEMPLATES:
        p, w = render_product_label(v, "357575100129238", "477934",
                                    out_path=os.path.join(LL.BASE_DIR, f"output_ws_producto_{v}.png"))
        print(p)
        for x in w:
            print("AVISO:", x)
