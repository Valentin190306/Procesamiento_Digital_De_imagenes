# Comandos (ejecutar dentro de 2-calculo-puntual/)

zip -r TP2_PUYELLI_HERRNEDER_MONTEAGUDO.zip Operaciones.ipynb Operaciones.html img requirements.txt

../20260907/.venv/bin/python -m jupyter nbconvert --to html --embed-images Operaciones.ipynb --output Operaciones.html

# Notas
- Operaciones.ipynb (32 celdas) es la versión final; no se regenera desde un builder.
- El venv de trabajo está en ../20260907/.venv (el Python global no tiene matplotlib).

# Ex1 (ejecutar dentro de 1-extraer-datos/)

../20260907/.venv/bin/python -m jupyter nbconvert --to html --embed-images procesamiento_imagenes.ipynb --output procesamiento_imagenes.html