import os

TIPOS_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}
TIPOS_GEOTIFF = {".tif", ".tiff"}


def extension(ruta):
    return os.path.splitext(ruta)[1].lower()


def es_imagen(ruta):
    return extension(ruta) in TIPOS_IMAGEN


def es_geotiff_por_extension(ruta):
    return extension(ruta) in TIPOS_GEOTIFF


def resolver_entrada(ruta):
    if os.path.isfile(ruta):
        return ruta
    candidata = os.path.join("entrada", ruta)
    return candidata if os.path.isfile(candidata) else None
