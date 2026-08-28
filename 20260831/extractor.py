import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from readers import imagen_2d, satelital
from salida import a_json, a_tabla


EXT_IMAGEN = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}


def detectar_y_leer(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    if ext not in EXT_IMAGEN:
        return None, f"Formato no soportado: {ext or '(sin extensión)'}"

    if ext in {".tif", ".tiff"} and satelital.es_geotiff(ruta):
        return satelital.leer(ruta), None

    try:
        return imagen_2d.leer(ruta), None
    except Exception as e:
        return None, f"Error al leer imagen: {e}"


def main():
    parser = argparse.ArgumentParser(
        description="Extrae muestreo y resoluciones (temporal, espacial, radiométrica) de una imagen."
    )
    parser.add_argument("imagen", help="Ruta del archivo de imagen")
    parser.add_argument("--json", action="store_true", help="Salida en formato JSON")
    args = parser.parse_args()

    if not os.path.isfile(args.imagen):
        candidata = os.path.join("entrada", args.imagen)
        if os.path.isfile(candidata):
            args.imagen = candidata
        else:
            print(f"Error: el archivo no existe -> {args.imagen}", file=sys.stderr)
            sys.exit(1)

    datos, error = detectar_y_leer(args.imagen)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(a_json(datos) if args.json else a_tabla(datos))


if __name__ == "__main__":
    main()
