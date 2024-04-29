import os
import pandas as pd

# Überprüfe das aktuelle Arbeitsverzeichnis
print("Aktuelles Arbeitsverzeichnis:", os.getcwd())

# Pfad zur CSV-Datei
dateipfad = os.path.join(
    os.getcwd(), "../../data/raw/Umsatzdaten/Gastronomieumsätze_flat.csv"
)

# Versuche, die Datei zu lesen
try:
    data = pd.read_csv(dateipfad, sep=";", encoding="ISO-8859-1")
    print("Datei erfolgreich gelesen.")
except FileNotFoundError:
    print(f"Datei nicht gefunden: {dateipfad}")
