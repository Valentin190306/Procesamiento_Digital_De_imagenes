zip -r TP2_PUYELLI_HERRNEDER_MONTEAGUDO.zip Operaciones.ipynb Operaciones.html img requirements.txt

.venv/bin/python -m jupyter nbconvert --to html --embed-images Operaciones.ipynb --output Operaciones.html