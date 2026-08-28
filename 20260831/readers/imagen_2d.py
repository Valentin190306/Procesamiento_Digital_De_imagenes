from PIL import Image
from PIL.ExifTags import TAGS

from .modelo import DatosImagen


BITS_POR_MODO = {
    "1": 1,
    "L": 8,
    "P": 8,
    "RGB": 8,
    "RGBA": 8,
    "CMYK": 8,
    "YCbCr": 8,
    "LAB": 8,
    "I": 32,
    "F": 32,
    "I;16": 16,
    "I;16L": 16,
    "I;16B": 16,
}


def _fecha_exif(imagen):
    try:
        exif = imagen.getexif()
        if not exif:
            return None
        tag = next((k for k, v in TAGS.items() if v == "DateTimeOriginal"), None)
        if tag and tag in exif:
            return str(exif[tag])
    except Exception:
        pass
    return None


def leer(ruta):
    imagen = Image.open(ruta)
    d = DatosImagen(tipo="Imagen 2D", archivo=ruta)
    d.ancho, d.alto = imagen.size
    d.modo = imagen.mode
    d.bits_por_muestra = BITS_POR_MODO.get(imagen.mode)
    d.canales = len(imagen.getbands())
    d.paleta = imagen.mode == "P"
    d.fecha_captura = _fecha_exif(imagen)

    try:
        dpi = imagen.info.get("dpi")
        if dpi:
            d.dpi = (round(float(dpi[0]), 1), round(float(dpi[1]), 1))
    except Exception:
        d.dpi = None

    d.nota_muestreo = "Contraste de imagen por muestreo en píxeles sobre la escena."
    return d
