import pandas as pd
import numpy as np
import requests


def ersetze_umlaute(bundesland):
    umlaute = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}
    for original, ersatz in umlaute.items():
        bundesland = bundesland.replace(original, ersatz)
    return bundesland


bundesländer = [
    "Brandenburg",
    "Baden-Wuerttemberg",
    "Mecklenburg-Vorpommern",
    "Bayern",
    "Niedersachsen",
    "Nordrhein-Westfalen",
    "Rheinland-Pfalz",
    "Berlin",
    "Hamburg",
    "Hessen",
]
ferienarten = ["ostern", "pfingsten", "sommer", "herbst", "weihnachten", "winter"]

# Liste für die gesammelten DataFrames
df_liste = []

for ferienart in ferienarten:
    for land in bundesländer:
        url_land = ersetze_umlaute(land).lower()
        url = f"https://www.schulferien.org/deutschland/ferien/{ferienart}/{url_land}/"
        try:
            response = requests.get(url)
            tables = pd.read_html(response.content)
            # Nehmen Sie an, dass die erste Tabelle die gewünschten Daten enthält
            df = tables[0]
            df["Bundesland"] = land  # Fügen Sie eine Spalte für das Bundesland hinzu
            df["Ferienart"] = (
                ferienart.capitalize()
            )  # Fügen Sie eine Spalte für die Ferienart hinzu
            df_liste.append(df)
        except Exception as e:
            print(
                f"Fehler beim Abrufen der Daten für {land} {ferienart.capitalize()}ferien: {e}"
            )

gesamt_df = pd.concat(df_liste, ignore_index=True)

# Erstellen eines leeren DataFrames, um die neuen Zeilen aufzunehmen
neue_zeilen = pd.DataFrame(columns=gesamt_df.columns)

# Iterieren über den DataFrame und Aufteilen der Zeilen mit "+"
for index, row in gesamt_df.iterrows():
    if "+" in row[1]:  # Überprüfen, ob "+" im Datum vorhanden ist
        daten_teile = row[1].split(" + ")
        for teil in daten_teile:
            neue_zeile = pd.DataFrame([row.values], columns=gesamt_df.columns)
            neue_zeile.iloc[0, 1] = (
                teil  # Ersetzen des Datums durch den aufgeteilten Teil
            )
            neue_zeilen = pd.concat([neue_zeilen, neue_zeile], ignore_index=True)
        gesamt_df.drop(index, inplace=True)  # Entfernen der ursprünglichen Zeile

# Hinzufügen der neuen Zeilen zum ursprünglichen DataFrame
gesamt_df = pd.concat([gesamt_df, neue_zeilen], ignore_index=True)

gesamt_df[["Startdatum", "Enddatum"]] = gesamt_df.iloc[:, 1].str.split(
    " - ", expand=True
)

# Überprüfen, ob das Datum gültig ist, bevor das Jahr hinzugefügt wird
gesamt_df["Startdatum"] = np.where(
    gesamt_df.iloc[:, 1] != "-",
    gesamt_df["Startdatum"] + gesamt_df.iloc[:, 0].astype(str),
    np.nan,
)
gesamt_df["Enddatum"] = np.where(
    gesamt_df.iloc[:, 1] != "-",
    gesamt_df["Enddatum"] + gesamt_df.iloc[:, 0].astype(str),
    np.nan,
)

# Konvertieren von Startdatum und Enddatum zu datetime, dabei ungültige Daten als NaT behandeln
gesamt_df["Startdatum"] = pd.to_datetime(
    gesamt_df["Startdatum"], format="%d.%m.%Y", errors="coerce"
)
gesamt_df["Enddatum"] = pd.to_datetime(
    gesamt_df["Enddatum"], format="%d.%m.%Y", errors="coerce"
)

# Entfernen der ursprünglichen Datums- und Jahres-Spalten
gesamt_df = gesamt_df.drop(gesamt_df.columns[[0, 1]], axis=1)

# Speichern des DataFrames
# gesamt_df.to_parquet("data/interim/ferien.parquet", index=False)
# gesamt_df.to_csv("data/interim/ferien.csv", index=False, encoding="utf-8")
