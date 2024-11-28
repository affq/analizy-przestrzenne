import arcpy

geobaza = r"C:/Users/adria/OneDrive/Pulpit/studia_foldery/analizy-przestrzenne/MyProject12/MyProject12.gdb"

arcpy.env.workspace = "in_memory"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRF2000-PL_CS92")
arcpy.env.extent = f"{geobaza}\\A03_Granice_gmin_Proj_Buffer"
arcpy.env.mask = f"{geobaza}\\A03_Granice_gmin_Proj_Buffer"
arcpy.env.cellSize = 5
arcpy.env.overwriteOutput = True

swrs_0210_buffer = arcpy.analysis.Buffer(f'{geobaza}\\SWRS_L_0210', f'{geobaza}\\SWRS_L_0210_buffer', '1 Centimeter')
swrs_0212_buffer = arcpy.analysis.Buffer(f'{geobaza}\\SWRS_L_0212', f'{geobaza}\\SWRS_L_0212_buffer', '1 Centimeter')
water = arcpy.management.Merge([swrs_0210_buffer, swrs_0212_buffer, f'{geobaza}\\PTWP_A_0210', f'{geobaza}\\PTWP_A_0212'], 'water')
budynki = arcpy.management.Merge([f'{geobaza}\\BUBD_A_0210', f'{geobaza}\\BUBD_A_0212'], 'budynki')
ptlz = arcpy.management.Merge([f'{geobaza}\\PTLZ_A_0210', f'{geobaza}\\PTLZ_A_0212'], 'ptlz')
nmt = f'{geobaza}\\nmt'
drogi = arcpy.management.Merge([f'{geobaza}\\SKDR_L_0210', f'{geobaza}\\SKDR_L_0212'], 'drogi')
wezly = f'{geobaza}\\wezly_raster'

import arcpy.analysis
import arcpy.management
from arcpy.sa import *

#kryterium 1
out_distance_accumulation_raster = arcpy.sa.DistanceAccumulation(in_source_data=water)
woda_rosnaca = FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 100 102")
woda_malejaca = FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 400 200")
woda_mapa = FuzzyOverlay([woda_rosnaca, woda_malejaca], 'AND')
woda_mapa.save(f'{geobaza}\\kryterium_1')

#kryterium 2
query = "FOBUD = 'budynki mieszkalne'"
arcpy.analysis.Select(budynki, 'budynki_mieszkalne', query)
out_distance_accumulation_buildings = arcpy.sa.DistanceAccumulation(in_source_data='budynki_mieszkalne')
budynki_mieszkalne = FuzzyMembership(out_distance_accumulation_buildings, fuzzy_function="LINEAR 150 1000")
budynki_mieszkalne.save(f'{geobaza}\\kryterium_2')

#kryterium 3
query = "RODZAJ = 'las'"
arcpy.analysis.Select(ptlz, 'ptlz_las', query)
out_distance_accumulation_ptlz = arcpy.sa.DistanceAccumulation(in_source_data="ptlz_las")
lasy_fuzzy = FuzzyMembership(out_distance_accumulation_ptlz, fuzzy_function="LINEAR 15 100")
lasy_fuzzy.save(f'{geobaza}\\kryterium_3')

#kryterium 4 
# query = "MATA_NAWIE IN ('beton', 'bruk', 'kostka kamienna', 'kostka prefabrykowana', 'masa bitumiczna', 'płyty betonowe')"
# arcpy.analysis.Select(drogi, 'drogi', query)
#jak zrobić drogi?

#kryterium 5
arcpy.ddd.Slope(nmt, "slope", "PERCENT_RISE", 1)
slope_fuzzy = FuzzyMembership("slope", fuzzy_function="LINEAR 10 1")
slope_fuzzy.save(f'{geobaza}\\kryterium_5')

#kryterium 6
aspect = arcpy.ddd.Aspect(nmt)
aspect_fuzzy = FuzzyMembership(aspect, fuzzy_function="LINEAR 135 180")
aspect_fuzzy_1 = FuzzyMembership(aspect, fuzzy_function="LINEAR 225 181")
aspect_overlay = FuzzyOverlay([aspect_fuzzy, aspect_fuzzy_1], 'OR')
aspect_overlay.save(f'{geobaza}\\kryterium_6')

#kryterium 7 - wezly
wezly_fuzzy = FuzzyMembership(wezly, fuzzy_function="LINEAR 1000 4000")
wezly_fuzzy.save(f'{geobaza}\\kryterium_7')

weights = {
    'kryterium_1': 1/7,
    'kryterium_2': 1/7,
    'kryterium_3': 1/7,
    'kryterium_4': 1/7,
    'kryterium_5': 1/7,
    'kryterium_6': 1/7,
    'kryterium_7': 1/7
}

#dodaj kryterium 4
tabela_kryteriow = WSTable([[f'{geobaza}\\kryterium_1', "VALUE", weights['kryterium_1']], [f'{geobaza}\\kryterium_2', "VALUE", weights['kryterium_2']], [f'{geobaza}\\kryterium_3', "VALUE", weights['kryterium_3']], [f'{geobaza}\\kryterium_5', "VALUE", weights['kryterium_5']], [f'{geobaza}\\kryterium_6', "VALUE", weights['kryterium_6']], [f'{geobaza}\\kryterium_7', "VALUE", weights['kryterium_7']]])
weighted_sum = WeightedSum(tabela_kryteriow)
weighted_sum.save(f'{geobaza}\\suma_rozmyte')

kryteria_ostre = FuzzyOverlay([woda_mapa, budynki_mieszkalne, lasy_fuzzy, aspect_overlay], 'AND')
kryteria_ostre.save(f'{geobaza}\\kryteria_ostre')

suma = FuzzyOverlay([kryteria_ostre, weighted_sum], 'AND')
suma.save(f'{geobaza}\\wynik')