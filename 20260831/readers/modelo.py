from dataclasses import dataclass
from typing import Optional


@dataclass
class DatosImagen:
    tipo: str
    archivo: str
    ancho: Optional[int] = None
    alto: Optional[int] = None
    modo: Optional[str] = None
    bits_por_muestra: Optional[int] = None
    canales: Optional[int] = None
    paleta: Optional[bool] = None
    dpi: Optional[tuple] = None
    fecha_captura: Optional[str] = None
    rango_dinamico: Optional[str] = None
    res_temporal: str = "N/A"
    nota_muestreo: Optional[str] = None
