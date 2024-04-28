import pandas as pd
import numpy as np
import glob
import os

dfs = []

for ordner in glob.glob("../data/raw/Wetterdaten/*"):
    if os.path.isdir(ordner):
        # Einlesen der "produkt_klima_tag"-Dateien
        produkt_dateien = glob.glob(f"{ordner}/produkt_klima_tag*")
        if produkt_dateien:
            produkt_df = pd.read_csv(
                produkt_dateien[0], sep=";", decimal=",", dtype={3: object, 4: object}
            )
            produkt_df.columns = produkt_df.columns.str.strip()
            produkt_df = produkt_df.replace(" ", "", regex=True)

            # Einlesen der "Metadaten_Geographie_"-Dateien
            metadaten_dateien = glob.glob(f"{ordner}/Metadaten_Geographie_*")
            if metadaten_dateien:
                metadaten_df = pd.read_csv(
                    metadaten_dateien[0], sep=";", decimal=",", encoding="iso-8859-1"
                )
                metadaten_df.columns = metadaten_df.columns.str.strip()
                # Anpassung der Spaltennamen für konsistentes Merging
                metadaten_df.rename(
                    columns={"Stations_id": "STATIONS_ID"}, inplace=True
                )

                # Entfernen von Duplikaten basierend auf 'STATIONS_ID', nur der erste Eintrag bleibt erhalten
                metadaten_df = metadaten_df.drop_duplicates(
                    subset=["STATIONS_ID"], keep="first"
                )

                # Zusammenführen der geografischen Daten mit den Wetterdaten
                merged_df = pd.merge(
                    produkt_df,
                    metadaten_df[
                        ["STATIONS_ID", "Geogr.Breite", "Geogr.Laenge", "Stationshoehe"]
                    ],
                    on="STATIONS_ID",
                    how="left",
                )

                dfs.append(merged_df)

gesamt_df = pd.concat(dfs, ignore_index=True)

gesamt_df["MESS_DATUM"] = pd.to_datetime(gesamt_df["MESS_DATUM"], format="%Y%m%d")
for spalte in gesamt_df.columns:
    if spalte not in ["MESS_DATUM", "eor"]:
        gesamt_df[spalte] = pd.to_numeric(gesamt_df[spalte], errors="coerce")
gesamt_df = gesamt_df[gesamt_df["MESS_DATUM"].dt.year >= 1994]
gesamt_df.replace(-999, np.nan, inplace=True)

gesamt_df["MESS_DATUM"] = pd.to_datetime(gesamt_df["MESS_DATUM"])
gesamt_df.set_index(["STATIONS_ID", "MESS_DATUM"], inplace=True)

# NaN Spalten
nan_spalten = [
    "QN_3",
    "FX",
    "FM",
    "QN_4",
    "RSK",
    "RSKF",
    "SDK",
    "SHK_TAG",
    "NM",
    "VPM",
    "PM",
    "TMK",
    "UPM",
    "TXK",
    "TNK",
    "TGK",
]

# Gruppieren nach 'STATIONS_ID'
gruppierte_df = gesamt_df.groupby("STATIONS_ID")

# Erstellen eines neuen DataFrames, um die interpolierten und gefüllten Daten aufzunehmen
neuer_df = pd.DataFrame()

start_datum = pd.Timestamp("1994-01-01")
ende_datum = pd.Timestamp("2023-12-23")

for name, gruppe in gruppierte_df:
    gruppe = gruppe.droplevel(
        "STATIONS_ID"
    )  # Entfernen des 'STATIONS_ID' Levels, um 'MESS_DATUM' als einzigen Index zu haben
    gruppe = gruppe.reindex(
        pd.date_range(start=start_datum, end=ende_datum, freq="D"), fill_value=np.nan
    )  # Erweiterung der Zeitreihe und Füllen mit NaN
    for spalte in nan_spalten:
        if spalte not in gruppe.columns:
            gruppe[spalte] = np.nan  # Füllen der spezifizierten Spalten mit NaN
    gruppe["STATIONS_ID"] = name  # Hinzufügen der 'STATIONS_ID' zurück zur Gruppe
    neuer_df = pd.concat(
        [neuer_df, gruppe]
    )  # Hinzufügen der Gruppe zum neuen DataFrame

# Zurücksetzen des Index, um 'STATIONS_ID' und 'MESS_DATUM' wieder als Spalten zu haben
gesamt_df2 = neuer_df.reset_index().rename(columns={"index": "MESS_DATUM"})

# Gruppieren nach 'STATIONS_ID' und Auffüllen der fehlenden Werte für spezifische Spalten
for spalte in ["eor", "Geogr.Breite", "Geogr.Laenge", "Stationshoehe"]:
    gesamt_df2[spalte] = gesamt_df2.groupby("STATIONS_ID")[spalte].transform(
        lambda x: x.fillna(method="ffill").fillna(method="bfill")
    )
