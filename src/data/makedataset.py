import pandas as pd
import numpy as np
import glob
import os


def read_and_process_files(directory):
    """
    Liest und verarbeitet Wetterdaten aus allen Unterordnern eines angegebenen Verzeichnisses.

    Args:
    directory (str): Pfad zum Verzeichnis mit den Wetterdatendateien.

    Returns:
    DataFrame: Ein DataFrame, der alle verarbeiteten Wetterdaten enthält.
    """
    dfs = []
    for folder in glob.glob(f"{directory}/*"):
        if os.path.isdir(folder):
            product_files = glob.glob(f"{folder}/produkt_klima_tag*")
            if product_files:
                product_df = pd.read_csv(
                    product_files[0], sep=";", decimal=",", dtype={3: object, 4: object}
                )
                product_df.columns = product_df.columns.str.strip()
                product_df = product_df.replace(" ", "", regex=True)

                metadata_files = glob.glob(f"{folder}/Metadaten_Geographie_*")
                if metadata_files:
                    metadata_df = pd.read_csv(
                        metadata_files[0], sep=";", decimal=",", encoding="iso-8859-1"
                    )
                    metadata_df.columns = metadata_df.columns.str.strip()
                    metadata_df.rename(
                        columns={"Stations_id": "STATIONS_ID"}, inplace=True
                    )
                    metadata_df = metadata_df.drop_duplicates(
                        subset=["STATIONS_ID"], keep="first"
                    )

                    merged_df = pd.merge(
                        product_df,
                        metadata_df[
                            [
                                "STATIONS_ID",
                                "Geogr.Breite",
                                "Geogr.Laenge",
                                "Stationshoehe",
                            ]
                        ],
                        on="STATIONS_ID",
                        how="left",
                    )

                    dfs.append(merged_df)

    if dfs:
        gesamt_df = pd.concat(dfs, ignore_index=True)
        return gesamt_df
    else:
        return pd.DataFrame()


def create_weather_dataset(data_directory):
    """
    Erstellt ein DataFrame mit Wetterdaten aus einem gegebenen Verzeichnis.

    Args:
    data_directory (str): Pfad zum Verzeichnis mit den Rohdaten.

    Returns:
    DataFrame: Ein DataFrame, der die verarbeiteten und zusammengeführten Wetterdaten enthält.
    """
    df = read_and_process_files(data_directory)
    if not df.empty:
        df["MESS_DATUM"] = pd.to_datetime(df["MESS_DATUM"], format="%Y%m%d")
        nan_columns = [
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
        for col in nan_columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.replace(-999, np.nan, inplace=True)
        df.set_index(["STATIONS_ID", "MESS_DATUM"], inplace=True)

        # Weiterverarbeitung wie im Originalskript
        grouped_df = df.groupby("STATIONS_ID")
        new_df = pd.DataFrame()
        start_date = pd.Timestamp("1994-01-01")
        end_date = pd.Timestamp("2023-12-23")
        for name, group in grouped_df:
            group = group.droplevel("STATIONS_ID")
            group = group.reindex(
                pd.date_range(start=start_date, end=end_date, freq="D"),
                fill_value=np.nan,
            )
            for col in nan_columns:
                if col not in group.columns:
                    group[col] = np.nan
            group["STATIONS_ID"] = name
            new_df = pd.concat([new_df, group])
        result_df = new_df.reset_index().rename(columns={"index": "MESS_DATUM"})
        for col in ["eor", "Geogr.Breite", "Geogr.Laenge", "Stationshoehe"]:
            result_df[col] = result_df.groupby("STATIONS_ID")[col].transform(
                lambda x: x.fillna(method="ffill").fillna(method="bfill")
            )

        return result_df
    else:
        return df


def create_revenue_dataset(
    filepath,
    separator=";",
    encoding="ISO-8859-1",
    umsatz_col="UMS002__Umsatz__2015=100",
    time_col="Zeit",
    region_code_col="4_Auspraegung_Code",
    region_label_col="5_Auspraegung_Label",
):
    # Einlesen der Daten
    data = pd.read_csv(filepath, sep=separator, encoding=encoding)

    # Verarbeiten der regionalen Codes
    data[region_code_col] = data[region_code_col].str[-2:].astype(int)

    # Umbenennen der Umsatzspalte für Klarheit
    data.rename(columns={umsatz_col: "Umsatz"}, inplace=True)

    # Bereinigen der Umsatzdaten
    data["Umsatz"] = data["Umsatz"].replace("...", float("NaN"))
    data["Umsatz"] = data["Umsatz"].str.replace(",", ".").astype(float)

    # Umwandlung der Zeitdaten in ein datetime-Objekt
    data[time_col] = pd.to_datetime(
        data[time_col].astype(str) + "-" + data[region_code_col].astype(str),
        format="%Y-%m",
    )

    # Sortierung der Daten nach Region und Zeit
    data.sort_values([region_label_col, time_col], inplace=True)

    return data


if __name__ == "__main__":

    output_directory = "data/interim"
    os.makedirs(output_directory, exist_ok=True)

    # Wetterdatensatz erstellen
    weather_data = create_weather_dataset("data/raw/Wetterdaten")
    # weather_data.to_csv(os.path.join(output_directory, "weather_dataset.csv"), index=False)
    # weather_data.to_parquet(os.path.join(output_directory, "weather_dataset.parquet"))

    # Umsatzdatensatz erstellen
    revenue_data = create_revenue_dataset(
        "data/raw/Umsatzdaten/Gastronomieumsätze_flat.csv"
    )
    # revenue_data.to_csv(os.path.join(output_directory, "revenue_dataset.csv"), index=False)
    # revenue_data.to_parquet(os.path.join(output_directory, "revenue_dataset.parquet"))
