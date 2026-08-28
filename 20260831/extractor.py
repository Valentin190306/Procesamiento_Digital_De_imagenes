import argparse
import sys

import lectura
from readers import imagen_2d, satelital
from salida import a_json, a_tabla


def detectar_y_leer(ruta):
    if not lectura.es_imagen(ruta):
        return None, f"Formato no soportado: {lectura.extension(ruta) or '(sin extensión)'}"
    if lectura.es_geotiff_por_extension(ruta) and satelital.es_geotiff(ruta):
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

    entrada = lectura.resolver_entrada(args.imagen)
    if entrada is None:
        print(f"Error: el archivo no existe -> {args.imagen}", file=sys.stderr)
        sys.exit(1)

    datos, error = detectar_y_leer(entrada)
    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    print(a_json(datos) if args.json else a_tabla(datos))


if __name__ == "__main__":
    main()
