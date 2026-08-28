# Procesamiento Digital De imágenes

Dos programas: `extractor.py` (leer datos) y `procesar.py` (sub-muestrear / reducir resolución radiométrica).

Hay dos carpetas:
- **`entrada/`** : colocá aquí los archivos de entrada.
- **`salida/`** : los resultados procesados se guardan aquí por defecto.

La ruta de un archivo se puede dar completa o relativa a `entrada/`, p. ej.
`python extractor.py ejemplo.png` usa `entrada/ejemplo.png`.

## Estructura

- `extractor.py` : extrae los datos de una imagen.
- `procesar.py` : sub-muestrea y/o reduce la resolución radiométrica.
- `lectura.py` : utilidades compartidas (detección de formato y resolución de `entrada/`).
- `readers/` : lectores por tipo (`imagen_2d.py` con Pillow, `satelital.py` con rasterio).
- `salida.py` : formateo de resultados (tabla / JSON).

El sub-muestreo espacial usa la API nativa de Pillow `Image.reduce(factor)`, y la
cuantización radiométrica se aplica con numpy (normaliza → cuantiza → re-expande).

## Extractor de datos de imagen

Extrae de una **imagen** los siguientes datos:

- **Muestreo**: matriz de píxeles (ancho x alto) y bits por muestra.
- **Resolución espacial**: píxeles, DPI y —para GeoTIFF— tamaño de píxel / GSD (m/píxel).
- **Resolución temporal**: `N/A` para una imagen estática (solo aplicable a video o secuencias).
- **Resolución radiométrica**: bits/muestra, niveles, nº de bandas y rango dinámico.

## Instalación

```bash
cd 20260831
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Imagen 2D
python extractor.py ejemplo.png

# GeoTIFF (satelital) con DPI / GSD
python extractor.py --json ejemplo_satelital.tif
```

- Salida por defecto en tabla; con `--json` en formato JSON.

## Procesar imagen (sub-muestreo y resolución radiométrica)

```
python procesar.py IMAGEN [-o SALIDA] [-f FACTOR] [-b BITS]
```

- `-f/--factor` : factor de **sub-muestreo espacial** (>=1; 1 = sin cambio). Cada `f` muestras conserva 1 (toma el píxel cada `f` posiciones), reduciendo la matriz a `alto/f x ancho/f`.
- `-b/--bits` : nueva **resolución radiométrica** en bits/muestra (p.ej. 4, 6, 1). Cuantiza los valores a `2^bits` niveles y los **re-expande al rango completo** del canal, de modo que la imagen se **posteriza (aparecen bandas de tono) pero NO se oscurece**. El modo de color se preserva. Si `bits >=` los actuales, no cambia.
- `-o/--salida` : ruta de salida (por defecto `salida/<nombre>_proc.<ext>`).

Ejemplos:
```bash
python procesar.py ejemplo.png -f 2            # imagen a la mitad
python procesar.py ejemplo.png -f 3 -b 4       # submuestreo x3 + 4 bits
python procesar.py ejemplo_satelital.tif -f 2  # GeoTIFF: actualiza GSD
```

Para **GeoTIFF** se preserva la georreferenciación y la transformada se recalcula
según el factor (el GSD queda multiplicado por `f`), por lo que el resultado se
puede inspeccionar con `extractor.py`.

## Tipos soportados

- **Imagen 2D** (`jpg`, `png`, `bmp`, `gif`, `webp`, …): usa Pillow.
- **GeoTIFF / satelital** (`tif`, `tiff` con geodatos): usa rasterio (leer GSD, bandas, rango).

La selección del lector es automática (extensión + presencia de geodatos).

## Nota sobre resolución temporal

Una imagen aislada es una captura instantánea, por lo que su resolución temporal
siempre se reporta como `N/A`. El campo se conserva y quedará listo para
soportar **video** (FPS) y **secuencias de imágenes** (intervalo de revisita)
en una próxima versión.
