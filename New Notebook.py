import arcpy

# geobaza = r"C:/Users/adria/OneDrive/Pulpit/studia_foldery/analizy-przestrzenne/MyProject12/MyProject12.gdb"
geobaza = r"C:\Users\adria\Desktop\STUDIA_FOLDERY\analizy\MyProject12\MyProject12.gdb"
arcpy.env.workspace = "in_memory"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRS_1989_Poland_CS92")
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
dzialki = f'{geobaza}\\dzialki'
pt_merged = f'{geobaza}\\PT_merged'
linie_elektroenergetyczne = arcpy.management.Merge([f'{geobaza}\\SULN_L_0210', f'{geobaza}\\SULN_L_0212'], 'linie_elektroenergetyczne')

import arcpy.analysis
import arcpy.management
from arcpy.sa import *

# #kryterium 1
# out_distance_accumulation_raster = arcpy.sa.DistanceAccumulation(in_source_data=water)
# woda_rosnaca = FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 100 102")
# woda_malejaca = FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 400 200")
# woda_mapa = FuzzyOverlay([woda_rosnaca, woda_malejaca], 'AND')
# woda_mapa.save(f'{geobaza}\\kryterium_1')

# #kryterium 2
# query = "FOBUD = 'budynki mieszkalne'"
# arcpy.analysis.Select(budynki, 'budynki_mieszkalne', query)
# out_distance_accumulation_buildings = arcpy.sa.DistanceAccumulation(in_source_data='budynki_mieszkalne')
# budynki_mieszkalne = FuzzyMembership(out_distance_accumulation_buildings, fuzzy_function="LINEAR 150 1000")
# budynki_mieszkalne.save(f'{geobaza}\\kryterium_2')

# #kryterium 3
# query = "RODZAJ = 'las'"
# arcpy.analysis.Select(ptlz, 'ptlz_las', query)
# out_distance_accumulation_ptlz = arcpy.sa.DistanceAccumulation(in_source_data="ptlz_las")
# lasy_fuzzy = FuzzyMembership(out_distance_accumulation_ptlz, fuzzy_function="LINEAR 15 100")
# lasy_fuzzy.save(f'{geobaza}\\kryterium_3')

# #kryterium 4 
# # query = "MATA_NAWIE IN ('beton', 'bruk', 'kostka kamienna', 'kostka prefabrykowana', 'masa bitumiczna', 'płyty betonowe')"
# # arcpy.analysis.Select(drogi, 'drogi', query)
# #jak zrobić drogi?

# #kryterium 5
# arcpy.ddd.Slope(nmt, "slope", "PERCENT_RISE", 1)
# slope_fuzzy = FuzzyMembership("slope", fuzzy_function="LINEAR 10 1")
# slope_fuzzy.save(f'{geobaza}\\kryterium_5')

# #kryterium 6
# aspect = arcpy.ddd.Aspect(nmt)
# aspect_fuzzy = FuzzyMembership(aspect, fuzzy_function="LINEAR 135 180")
# aspect_fuzzy_1 = FuzzyMembership(aspect, fuzzy_function="LINEAR 225 181")
# aspect_overlay = FuzzyOverlay([aspect_fuzzy, aspect_fuzzy_1], 'OR')
# aspect_overlay.save(f'{geobaza}\\kryterium_6')

# #kryterium 7 - wezly
# wezly_fuzzy = FuzzyMembership(wezly, fuzzy_function="LINEAR 1000 4000")
# wezly_fuzzy.save(f'{geobaza}\\kryterium_7')

# weights = {
#     'kryterium_1': 1/7,
#     'kryterium_2': 1/7,
#     'kryterium_3': 1/7,
#     'kryterium_4': 1/7,
#     'kryterium_5': 1/7,
#     'kryterium_6': 1/7,
#     'kryterium_7': 1/7
# }

# #dodaj kryterium 4
# tabela_kryteriow = WSTable([[f'{geobaza}\\kryterium_1', "VALUE", weights['kryterium_1']], [f'{geobaza}\\kryterium_2', "VALUE", weights['kryterium_2']], [f'{geobaza}\\kryterium_3', "VALUE", weights['kryterium_3']], [f'{geobaza}\\kryterium_5', "VALUE", weights['kryterium_5']], [f'{geobaza}\\kryterium_6', "VALUE", weights['kryterium_6']], [f'{geobaza}\\kryterium_7', "VALUE", weights['kryterium_7']]])
# weighted_sum = WeightedSum(tabela_kryteriow)
# weighted_sum.save(f'{geobaza}\\suma_rozmyte')

# kryteria_ostre = FuzzyOverlay([woda_mapa, budynki_mieszkalne, lasy_fuzzy, aspect_overlay], 'AND')
# kryteria_ostre.save(f'{geobaza}\\kryteria_ostre')

# suma = FuzzyOverlay([kryteria_ostre, weighted_sum], 'AND')
# suma.save(f'{geobaza}\\wynik')

# #reclassify
# wynik_reclassified = Reclassify(suma, "VALUE", RemapRange([[0, 0.6, 0], [0.6, 1, 1]]))
# wynik_reclassified.save(f'{geobaza}\\wynik_reclassified')

# #wybierz dzialki na terenie przydatnym
# poligon_przydatnosci = "poligon_przydatnosci"
# arcpy.conversion.RasterToPolygon(wynik_reclassified, poligon_przydatnosci, "NO_SIMPLIFY", "VALUE")

# poligon_przydatnosci_layer = "poligon_przydatnosci_layer"
# arcpy.management.MakeFeatureLayer(poligon_przydatnosci, poligon_przydatnosci_layer)
# arcpy.management.SelectLayerByAttribute(poligon_przydatnosci_layer, "NEW_SELECTION", "gridcode = 1")
# arcpy.management.CopyFeatures(poligon_przydatnosci_layer, f"{geobaza}\\poligon_przydatnosci")

# dzialki_przeciete = "dzialki_przeciete"
# arcpy.analysis.Intersect([dzialki, poligon_przydatnosci], dzialki_przeciete, "ALL")
# arcpy.management.CopyFeatures(dzialki_przeciete, f"{geobaza}\\dzialki_przeciete_przez_poligony")

# arcpy.management.AddField(dzialki_przeciete, "pole", "DOUBLE")
# arcpy.management.CalculateField(dzialki_przeciete, "pole", "!shape.area@SQUAREMETERS!", "PYTHON3")

# arcpy.management.AddField(dzialki, "pole", "DOUBLE")
# arcpy.management.CalculateField(dzialki, "pole", "!shape.area@SQUAREMETERS!", "PYTHON3")

# arcpy.management.AddField(dzialki, "pole_przydatne", "DOUBLE")
# arcpy.management.CalculateField(dzialki, "pole_przydatne", 0, "PYTHON3")

# with arcpy.da.UpdateCursor(dzialki_przeciete, ["ID_DZIALKI", "pole", "gridcode"]) as cursor:
#     for row in cursor:
#         if row[2] == 1:
#             with arcpy.da.UpdateCursor(dzialki, ["ID_DZIALKI", "pole", "pole_przydatne"]) as cursor2:
#                 for row2 in cursor2:
#                     if row[0] == row2[0]:
#                         row2[2] += row[1]
#                         cursor2.updateRow(row2)

# arcpy.management.AddField(dzialki, "przydatnosc", "DOUBLE")
# arcpy.management.CalculateField(dzialki, "przydatnosc", "(!pole_przydatne! / !pole!) * 100", "PYTHON3")

# dzialki_layer = "dzialki_layer"
# arcpy.management.MakeFeatureLayer(dzialki, dzialki_layer)
# arcpy.management.SelectLayerByAttribute(dzialki_layer, "NEW_SELECTION", "przydatnosc > 50")
# arcpy.management.CopyFeatures(dzialki_layer, f"{geobaza}\\dzialki_przydatne_powyzej_50")

# costs = {
#     "PTWP01": 0,
#     "PTWP02": 200,
#     "PTWP03": 0,
#     "PTZB02": 100,
#     "PTZB01": 200,
#     "PTZB05": 50,
#     "PTZB04": 200,
#     "PTZB03": 200,
#     "PTLZ01": 100,
#     "PTLZ02": 50,
#     "PTLZ03": 50,
#     "PTRK01": 15,
#     "PTRK02": 15,
#     "PTUT03": 100,
#     "PTUT02": 90,
#     "PTUT04": 20,
#     "PTUT05": 20,
#     "PTUT01": 0,
#     "PTTR02": 1,
#     "PTTR01": 20,
#     "PTKM02": 200,
#     "PTKM01": 100,
#     "PTKM03": 200,
#     "PTKM04": 0,
#     "PTGN01": 1,
#     "PTGN02": 1,
#     "PTGN03": 1,
#     "PTGN04": 1,
#     "PTPL01": 50,
#     "PTSO01": 0,
#     "PTSO02": 0,
#     "PTWZ01": 0,
#     "PTWZ02": 0,
#     "PTNZ01": 150,
#     "PTNZ02": 150
# }

pt_merged_layer = "pt_merged_layer"
arcpy.management.MakeFeatureLayer(pt_merged, pt_merged_layer)
arcpy.management.AddField(pt_merged_layer, "cost", "FLOAT")
arcpy.management.CalculateField(
    in_table=pt_merged_layer,
    field="cost",
    expression="costs.get(!x_kod!, 0)",
    expression_type="PYTHON3",
    code_block="""
costs = {
    "PTWP01": 0,
    "PTWP02": 200,
    "PTWP03": 0,
    "PTZB02": 100,
    "PTZB01": 200,
    "PTZB05": 50,
    "PTZB04": 200,
    "PTZB03": 200,
    "PTLZ01": 100,
    "PTLZ02": 50,
    "PTLZ03": 50,
    "PTRK01": 15,
    "PTRK02": 15,
    "PTUT03": 100,
    "PTUT02": 90,
    "PTUT04": 20,
    "PTUT05": 20,
    "PTUT01": 0,
    "PTTR02": 1,
    "PTTR01": 20,
    "PTKM02": 200,
    "PTKM01": 100,
    "PTKM03": 200,
    "PTKM04": 0,
    "PTGN01": 1,
    "PTGN02": 1,
    "PTGN03": 1,
    "PTGN04": 1,
    "PTPL01": 50,
    "PTSO01": 0,
    "PTSO02": 0,
    "PTWZ01": 0,
    "PTWZ02": 0,
    "PTNZ01": 150,
    "PTNZ02": 150
}"""
)

out_cost = arcpy.conversion.PolygonToRaster(
    in_features=pt_merged_layer,
    value_field="cost",
    out_rasterdataset=f"{geobaza}\\cost_raster",
    cell_assignment="CELL_CENTER",
    cellsize=5
)

out_distance = arcpy.sa.CostDistance(
    in_source_data=f"{geobaza}\\dzialki_przydatne_powyzej_50",
    in_cost_raster=f"{geobaza}\\cost_raster",
    maximum_distance=None,
    out_backlink_raster=f"{geobaza}\\cost_backlink",
    source_cost_multiplier=None,
    source_start_cost=None,
    source_resistance_rate=None,
    source_capacity=None,
    source_direction=""
)
out_distance.save(f"{geobaza}\\cost_distance")

out_path = arcpy.sa.CostPath(
    in_destination_data=f"{geobaza}\\suln_l",
    in_cost_distance_raster=f"{geobaza}\\cost_distance",
    in_cost_backlink_raster=f"{geobaza}\\cost_backlink",
    path_type="BEST_SINGLE",
    destination_field="OBJECTID",
    force_flow_direction_convention="INPUT_RANGE"
)
out_path.save(f"{geobaza}\cost_path")

path_vector = arcpy.conversion.RasterToPolyline(in_raster=out_path, out_polyline_features=f"{geobaza}\\cost_path_vector")