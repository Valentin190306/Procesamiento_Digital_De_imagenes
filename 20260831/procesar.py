import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import salida
from readers import imagen_2d, satelital


EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}


def _submuestrear_espacial(arr, factor):
    if factor <= 1:
        return arr
    f = int(factor)
    return arr[::f, ::f]


def _reducir_radiometria(arr, bits_nuevos):
    if np.issubdtype(arr.dtype, np.integer):
        info = np.iinfo(arr.dtype)
        vmin_in, vmax_in = 0.0, float(info.max)
        vmin_out, vmax_out = 0.0, float(max(1, info.max))
    else:
        vmin_in = float(np.nanmin(arr))
        vmax_in = float(np.nanmax(arr))
        if vmax_in == vmin_in:
            vmax_in = vmin_in + 1.0
        vmin_out, vmax_out = vmin_in, vmax_in

    bits_act = arr.dtype.itemsize * 8 if np.issubdtype(arr.dtype, np.integer) else 64
    if bits_nuevos >= bits_act:
        return arr

    niveles_out = (1 << bits_nuevos) - 1
    norm = (arr.astype("float64") - vmin_in) / (vmax_in - vmin_in)
    cuant = np.round(norm * niveles_out)
    desnormal = cuant / niveles_out * (vmax_out - vmin_out) + vmin_out

    if np.issubdtype(arr.dtype, np.integer):
        out = np.clip(np.round(desnormal), np.iinfo(arr.dtype).min,
                      np.iinfo(arr.dtype).max).astype(arr.dtype)
    else:
        out = desnormal.astype(arr.dtype)
    return out


def procesar(ruta, factor=1, bits=None, salida_ruta=None):
    ext = os.path.splitext(ruta)[1].lower()

    if ext in {".tif", ".tiff"} and satelital.es_geotiff(ruta):
        return _procesar_satelital(ruta, factor, bits, salida_ruta)
    return _procesar_2d(ruta, factor, bits, salida_ruta)


def _normalizar_color(imagen):
    modo = imagen.mode
    if modo in ("L", "1", "I", "I;16", "I;16L", "I;16B", "F"):
        return imagen
    if modo == "P":
        if "transparency" in imagen.info:
            return imagen.convert("RGBA")
        return imagen.convert("RGB")
    if modo in ("RGBA", "LA", "PA"):
        return imagen.convert("RGBA")
    return imagen.convert("RGB")


def _procesar_2d(ruta, factor, bits, salida_ruta):
    from PIL import Image

    imagen = Image.open(ruta)
    imagen = _normalizar_color(imagen)
    arr = np.asarray(imagen)

    if factor > 1:
        arr = _submuestrear_espacial(arr, factor)

    if bits is not None:
        arr = _reducir_radiometria(arr, bits)

    salida_img = Image.fromarray(arr)
    salida_img.save(salida_ruta)
    return _resumen_2d(ruta, imagen.size, arr, factor, bits)


def _procesar_satelital(ruta, factor, bits, salida_ruta):
    import rasterio
    from rasterio.transform import Affine

    with rasterio.open(ruta) as src:
        arr = src.read()
        transform = src.transform
        crs = src.crs

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
    return _resumen_satelital(ruta, arr, factor, bits)


def _resumen_2d(ruta, orig, arr, factor, bits):
    return {
        "Archivo origen": ruta,
        "Tamaño original": f"{orig[0]} x {orig[1]} px",
        "Factor de submuestreo espacial": factor,
        "Tamaño resultante": f"{arr.shape[1]} x {arr.shape[0]} px",
        "Bits por muestra (radiometría)": None if bits is None else bits,
        "dtype resultante": arr.dtype.name,
    }


def _resumen_satelital(ruta, arr, factor, bits):
    return {
        "Archivo origen": ruta,
        "Factor de submuestreo espacial": factor,
        "Tamaño resultante": f"{arr.shape[2]} x {arr.shape[1]} px",
        "Bandas": arr.shape[0],
        "Bits por muestra (radiometría)": None if bits is None else bits,
        "dtype resultante": arr.dtype.name,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Procesa una imagen: sub-muestreo espacial y/o reducción de resolución radiométrica."
    )
    parser.add_argument("imagen", help="Ruta del archivo de imagen de entrada")
    parser.add_argument("-o", "--salida", default=None, help="Ruta del archivo de salida (por defecto: <nombre>_proc.<ext>)")
    parser.add_argument("-f", "--factor", type=int, default=1, help="Factor de sub-muestreo espacial (>=1; 1 = sin cambio)")
    parser.add_argument("-b", "--bits", type=int, default=None,
                        help="Nueva resolución radiométrica en bits/muestra (p.ej. 4, 6, 1)")
    args = parser.parse_args()

    if not os.path.isfile(args.imagen):
        candidata = os.path.join("entrada", args.imagen)
        if os.path.isfile(candidata):
            args.imagen = candidata
        else:
            print(f"Error: el archivo no existe -> {args.imagen}", file=sys.stderr)
            sys.exit(1)
    if args.factor < 1:
        print("Error: el factor debe ser >= 1", file=sys.stderr)
        sys.exit(1)
    if args.bits is not None and args.bits < 1:
        print("Error: los bits deben ser >= 1", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(args.imagen)[1] or ".png"
    os.makedirs("salida", exist_ok=True)
    salida_ruta = (
        args.salida
        or os.path.join("salida", f"{os.path.basename(os.path.splitext(args.imagen)[0])}_proc{ext}")
    )

    resumen = procesar(args.imagen, args.factor, args.bits, salida_ruta)
    print(f"Imagen procesada guardada en: {salida_ruta}")
    for k, v in resumen.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
