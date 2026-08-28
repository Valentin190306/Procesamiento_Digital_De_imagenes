from dataclasses import asdict
import json


def construir(d):
    return {
        "Archivo": d.archivo,
        "Tipo": d.tipo,
        "Muestreo": _muestreo(d),
        "Resolución Espacial": _espacial(d),
        "Resolución Temporal": d.res_temporal,
        "Resolución Radiométrica": _radiometrica(d),
    }


def _muestreo(d):
    if d.ancho and d.alto:
        base = f"Matriz de muestreo: {d.ancho} x {d.alto} píxeles"
        if d.bits_por_muestra and d.canales:
            base += f" | {d.bits_por_muestra} bits/muestra x {d.canales} canal(es)"
    else:
        base = "No determinable"
    if d.nota_muestreo:
        base += f"\n   {d.nota_muestreo}"
    return base


def _espacial(d):
    celdas = []
    if d.ancho and d.alto:
        celdas.append(f"{d.ancho} x {d.alto} px")
    if d.dpi:
        celdas.append(f"DPI: {d.dpi[0]} x {d.dpi[1]}")
    if d.tamanio_pixel:
        celdas.append(f"Píxel: {d.tamanio_pixel}")
    if d.gsd_metros is not None:
        celdas.append(f"GSD: {d.gsd_metros:.4f} m/píxel")
    return "; ".join(celdas) if celdas else "No disponible"


def _radiometrica(d):
    celdas = []
    if d.bits_por_muestra:
        niveles = 2 ** min(d.bits_por_muestra, 32)
        celdas.append(f"{d.bits_por_muestra} bits/muestra ({niveles} niveles)")
    if d.bandas:
        celdas.append(f"{d.bandas} banda(s)")
    if d.dtype:
        celdas.append(f"tipo: {d.dtype}")
    if d.rango_dinamico:
        celdas.append(f"rango: {d.rango_dinamico}")
    return "; ".join(celdas) if celdas else "No disponible"


def a_tabla(d):
    datos = construir(d)
    ancho = max(len(k) for k in datos)
    lineas = []
    for k, v in datos.items():
        lineas.append(f"{k.ljust(ancho)} : {v}")
    return "\n".join(lineas)


def a_json(d):
    payload = construir(d)
    payload["Nota"] = "La resolución temporal solo es aplicable a video o secuencias de imágenes."
    return json.dumps(payload, ensure_ascii=False, indent=2)
