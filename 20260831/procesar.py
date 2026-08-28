import argparse
import os
import sys

import numpy as np

import lectura
from readers import imagen_2d, satelital


# ---------------------------------------------------------------------------
# Operaciones de procesamiento
# ---------------------------------------------------------------------------

def _reducir_radiometria(arr, bits):
    """Cuantiza los valores a `2^bits` niveles y los re-expande al rango
    completo, de modo que la imagen se posteriza pero no se oscurece."""
    dtype = arr.dtype
    if np.issubdtype(dtype, np.integer):
        minimo, maximo = 0.0, float(np.iinfo(dtype).max)
    else:
        minimo = float(np.nanmin(arr))
        maximo = float(np.nanmax(arr))
        if maximo == minimo:
            maximo = minimo + 1.0

    if bits >= (dtype.itemsize * 8 if np.issubdtype(dtype, np.integer) else 64):
        return arr

    niveles = (1 << bits) - 1
    normalizado = (arr.astype("float64") - minimo) / (maximo - minimo)
    cuantizado = np.round(normalizado * niveles) / niveles
    reexpandido = cuantizado * (maximo - minimo) + minimo
    if np.issubdtype(dtype, np.integer):
        return np.clip(np.round(reexpandido), np.iinfo(dtype).min,
                       np.iinfo(dtype).max).astype(dtype)
    return reexpandido.astype(dtype)


def _normalizar_color(imagen):
    """Convierte a RGB/RGBA las imágenes de color pero deja intactas las de grises."""
    grises = {"L", "1", "I", "I;16", "I;16L", "I;16B", "F"}
    if imagen.mode in grises:
        return imagen
    if imagen.mode in {"RGBA", "LA", "PA"} or imagen.mode == "P" and "transparency" in imagen.info:
        return imagen.convert("RGBA")
    return imagen.convert("RGB")


# ---------------------------------------------------------------------------
# Procesado por tipo de imagen
# ---------------------------------------------------------------------------

def _procesar_2d(ruta, factor, bits, salida_ruta):
    from PIL import Image

    imagen = _normalizar_color(Image.open(ruta))
    if factor > 1:
        imagen = imagen.reduce(factor)
    if bits is not None:
        arr = _reducir_radiometria(np.asarray(imagen), bits)
        imagen = Image.fromarray(arr)
    imagen.save(salida_ruta)

    return _resumen(ruta, imagen.size, factor, bits, canales=len(imagen.getbands()))


def _procesar_satelital(ruta, factor, bits, salida_ruta):
    import rasterio
    from rasterio.transform import Affine

    with rasterio.open(ruta) as src:
        arr = src.read()
        transform, crs = src.transform, src.crs

    if factor > 1:
        f = int(factor)
        arr = arr[:, ::f, ::f]
        transform = Affine(transform.a * f, transform.b, transform.c,
                           transform.d, transform.e * f, transform.f)
    if bits is not None:
        arr = _reducir_radiometria(arr, bits)

    with rasterio.open(
        salida_ruta, "w", driver="GTiff",
        height=arr.shape[1], width=arr.shape[2],
        count=arr.shape[0], dtype=arr.dtype.name,
        crs=crs, transform=transform,
    ) as dst:
        dst.write(arr)

    return _resumen(ruta, (arr.shape[2], arr.shape[1]), factor, bits, bandas=arr.shape[0])


def _resumen(ruta, tamano, factor, bits, canales=None, bandas=None):
    return {
        "Archivo origen": ruta,
        "Factor de submuestreo espacial": factor,
        "Tamaño resultante": f"{tamano[0]} x {tamano[1]} px",
        "Bits por muestra": None if bits is None else bits,
        "Canales": canales,
        "Bandas": bandas,
        "dtype resultante": None,
    }


def procesar(ruta, factor=1, bits=None, salida_ruta=None):
    if lectura.es_geotiff_por_extension(ruta) and satelital.es_geotiff(ruta):
        return _procesar_satelital(ruta, factor, bits, salida_ruta)
    return _procesar_2d(ruta, factor, bits, salida_ruta)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _error(mensaje):
    print(f"Error: {mensaje}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Sub-muestrea espacialmente y/o reduce la resolución radiométrica de una imagen."
    )
    parser.add_argument("imagen", help="Ruta del archivo de imagen de entrada")
    parser.add_argument("-o", "--salida", default=None,
                        help="Ruta de salida (por defecto: salida/<nombre>_proc.<ext>)")
    parser.add_argument("-f", "--factor", type=int, default=1,
                        help="Factor de sub-muestreo espacial (>=1)")
    parser.add_argument("-b", "--bits", type=int, default=None,
                        help="Nueva resolución radiométrica en bits/muestra (p.ej. 4, 1)")
    args = parser.parse_args()

    entrada = lectura.resolver_entrada(args.imagen)
    if entrada is None:
        _error(f"el archivo no existe: {args.imagen}")
    if args.factor < 1:
        _error("el factor debe ser >= 1")
    if args.bits is not None and args.bits < 1:
        _error("los bits deben ser >= 1")

    ext = os.path.splitext(entrada)[1] or ".png"
    os.makedirs("salida", exist_ok=True)
    base = os.path.basename(os.path.splitext(entrada)[0])
    salida_ruta = args.salida or os.path.join("salida", f"{base}_proc{ext}")

    resumen = procesar(entrada, args.factor, args.bits, salida_ruta)
    print(f"Imagen procesada guardada en: {salida_ruta}")
    for clave, valor in resumen.items():
        if valor is not None:
            print(f"  {clave}: {valor}")


if __name__ == "__main__":
    main()
