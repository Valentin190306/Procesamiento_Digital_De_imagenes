import numpy as np
import rasterio
from rasterio.errors import RasterioIOError

from .modelo import DatosImagen


def _es_geo(dataset):
    try:
        if dataset.transform.is_identity and dataset.crs is None:
            return False
        return True
    except Exception:
        return False


def _uom(crs):
    try:
        uom = (crs or rasterio.crs.CRS()).linear_units
        return uom or "metros"
    except Exception:
        return "metros"


def leer(ruta):
    with rasterio.open(ruta) as src:
        d = DatosImagen(tipo="Imagen satelital/GeoTIFF", archivo=ruta)
        d.ancho, d.alto = src.width, src.height
        d.bandas = src.count
        d.dtype = src.dtypes[0]
        d.bits_por_muestra = np.dtype(d.dtype).itemsize * 8
        d.crs = getattr(src, "crs", None)
        d.uom = _uom(getattr(src, "crs", None))

        vals = src.read()
        minimo = float(np.nanmin(vals))
        maximo = float(np.nanmax(vals))
        d.rango_dinamico = f"{minimo:.6g} - {maximo:.6g}"

        if not getattr(src.transform, "is_identity", False):
            res_x = abs(src.transform.a)
            res_y = abs(src.transform.e)
            d.gsd_metros = (res_x + res_y) / 2.0 if src.crs and src.crs.is_geographic is False else None
            d.tamanio_pixel = f"{res_x:.6g} x {res_y:.6g} {d.uom}"

        d.nota_muestreo = (
            "Muestreo espacial definido por el tamaño de píxel (GSD) y la rejilla "
            "regular de muestras del embaldosado (raster)."
        )
        return d


def es_geotiff(ruta):
    try:
        with rasterio.open(ruta) as src:
            return _es_geo(src)
    except (RasterioIOError, Exception):
        return False
