# DABI2
------------

Die Projektarbeit für DSCB420 im Sommersemester 2024 konzentriert sich auf die Integration von Data-Science-Kenntnissen in eine moderne Gesamtarchitektur, einschließlich ETL, OLAP, Pandas-Analysen und Machine Learning. Studierende müssen vorgegebene Fragestellungen bearbeiten und eigene Anwendungsfälle aus vorhandenen Datensätzen entwickeln, wobei eine prototypische Umsetzung in der Cloud erfolgt. Die Aufgaben umfassen Datenaufbereitung, Analyse, Architekturspezifikation und Implementierung, wobei unter anderem Monatsstatistiken im Gastgewerbe und Wetterdaten auf Tagesbasis verwendet werden.

------------

### Die Verzeichnisstruktur des Projekts sieht folgendermaßen aus:

```
DABI2/
├── data
│   ├── raw                 <- Der ursprüngliche, unveränderliche Datendump.
│   ├── interim             <- Vorläufig verarbeitete Daten.
│   └── processed           <- Endgültig verarbeitete und für die Analyse bereitgestellte Daten
│
├── docs
├── models
├── notebooks               <- Jupyter Notebooks für Datenanalyse und Modellierung
├── references              <- Alle erläuternden Materialien
├── reports                 <- Erzeugte Analysen als PDF
│   └── figures             <- Erzeugte Grafiken und Abbildungen für die Berichterstattung
│
├── src
│   ├── data                <- Skripte zum Herunterladen oder Generieren von Daten
│   ├── features
│   ├── models
│   └── visualization
│
├── LICENSE
├── README
└── requirements.txt
```

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
