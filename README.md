# Projekt 1: Wskazanie optymalnej lokalizacji farmy fotowoltaicznej – analizy wielokryterialne (MCE)

Celem projektu jest przeprowadzenie analizy wielokryterialnej w celu znalezienia optymalnej lokalizacji farmy fotowoltaicznej dla gminy Świeradów Zdrój.

## Narzędzia

* Python (arcpy)
* ArcGIS Pro
* QGIS (kryterium 7)

## Kryteria

### Kryteria rozmyte

| Lp | Kryterium | Parametry | Źródło danych |
| ------------- | ------------- | ------------- | ------------- |
| 1  | odległość od rzek i zbiorników wodnych | jak najbliżej | BDOT10k(SWRS, PTWP) |
| 2  | odległość od budynków mieszkalnych | jak najdalej | BDOT10k(BUBD) |
| 3  | pokrycie terenu  | optymalnie powyżej 100m od lasu  | BDOT10k(PTLZ) |
| 4  | dostęp do dróg utwardzonych  | jak największe zagęszczenie | BDOT10k(SKDR) |
| 5  | nachylenie stoków | optymalnie – płasko | NMT |
| 6  | dostęp światła słonecznego  | optymalnie - stoki południowe (SW-SE) | NMT |
| 7  | dobry dojazd od istotnych drogowych węzłów komunikacyjnych | jak najkrótszy czas dojazdu | BDOT10k(SKDR) |

### Kryteria ostre

| Lp | Kryterium | Parametry | Źródło danych |
| ------------- | ------------- | ------------- | ------------- |
| 1  | odległość od rzek i zbiorników wodnych | powyżej 100m | BDOT10k(SWRS, PTWP) |
| 2  | odległość od budynków mieszkalnych | powyżej 150m | BDOT10k(BUBD) |
| 3  | pokrycie terenu  | powyżej 15m od lasu  | BDOT10k(PTLZ) |
| 4  | nachylenie stoków  | maksymalnie 10% | NMT |

### Łączenie kryteriów

| Lp | Kryterium | Parametry | Źródło danych |
| ------------- | ------------- | ------------- | ------------- |
| 1  | ocena przydatności terenu (próg przydatności) | 80% / 90% max. przydatności |  |
| 2  | Przydatne działki / grupy działek | min. 60 % działki na terenie przydatnym | EGiB |
| 3  | Powierzchnia i min. szerokość obszaru | 2ha / 50m |  |
| 4  | Koszt przyłącza do sieci SN (mapy kosztów) | jak najniższy |  |
