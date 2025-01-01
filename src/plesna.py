import arcpy
import arcpy.analysis
import arcpy.management
import arcpy.sa

geobaza = r"C:\Users\adria\Desktop\STUDIA_FOLDERY\analizy\Plesna\Plesna.gdb"
arcpy.env.workspace = "in_memory"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRS_1989_Poland_CS92")
arcpy.env.extent = f"{geobaza}\\gmina_buffer"
arcpy.env.mask = f"{geobaza}\\gmina_buffer"
arcpy.env.cellSize = 5
arcpy.env.overwriteOutput = True

swrs = f"{geobaza}\\SWRS_L"
bubd = f"{geobaza}\\BUBD_A"
ptlz = f"{geobaza}\\PTLZ_A"
nmt = f"{geobaza}\\nmt"
skdr = f"{geobaza}\\SKDR_L"
wezly = f"{geobaza}\\wezly"
dzialki = f"{geobaza}\\dzialki"
# pt_merged = f'{geobaza}\\PT_merged'
linie_elektroenergetyczne = f'{geobaza}\\SULN_L'

#kryterium 1
out_distance_accumulation_raster = arcpy.sa.DistanceAccumulation(in_source_data=swrs)
woda_rosnaca = arcpy.sa.FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 100 102")
woda_malejaca = arcpy.sa.FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 400 200")
woda_mapa = arcpy.sa.FuzzyOverlay([woda_rosnaca, woda_malejaca], 'AND')
woda_mapa.save(f'{geobaza}\\kryterium_1')

#kryterium 2
query = "FOBUD = 'budynki mieszkalne'"
arcpy.analysis.Select(bubd, 'budynki_mieszkalne', query)
out_distance_accumulation_buildings = arcpy.sa.DistanceAccumulation(in_source_data='budynki_mieszkalne')
budynki_mieszkalne = arcpy.sa.FuzzyMembership(out_distance_accumulation_buildings, fuzzy_function="LINEAR 150 1000")
budynki_mieszkalne.save(f'{geobaza}\\kryterium_2')

#kryterium 3
query = "RODZAJ = 'las'"
arcpy.analysis.Select(ptlz, 'ptlz_las', query)
out_distance_accumulation_ptlz = arcpy.sa.DistanceAccumulation(in_source_data="ptlz_las")
lasy_fuzzy = arcpy.sa.FuzzyMembership(out_distance_accumulation_ptlz, fuzzy_function="LINEAR 15 100")
lasy_fuzzy.save(f'{geobaza}\\kryterium_3')

#kryterium 4 
query = "MATE_NAWIE IN ('beton', 'bruk', 'kostka kamienna', 'kostka prefabrykowana', 'masa bitumiczna', 'płyty betonowe')"
drogi_utwardzone = arcpy.analysis.Select(skdr, 'drogi', query)

density = arcpy.sa.LineDensity(
    in_polyline_features=drogi_utwardzone,
    population_field=None,
    cell_size=5,
    search_radius=1000,
    area_unit_scale_factor="SQUARE_METERS",
)

kryterium_4 = arcpy.sa.RescaleByFunction(
    in_raster=density,
    transformation_function="LINEAR 0 1",
    from_scale=0,
    to_scale=1   
)
kryterium_4.save(f'{geobaza}\\kryterium_4')

# kryterium 5
arcpy.ddd.Slope(nmt, "slope", "PERCENT_RISE", 1)
slope_fuzzy = arcpy.sa.FuzzyMembership("slope", fuzzy_function="LINEAR 10 1")
slope_fuzzy.save(f'{geobaza}\\kryterium_5')

#kryterium 6
aspect = arcpy.ddd.Aspect(nmt, f"{geobaza}\\aspect")
aspect_fuzzy = arcpy.sa.FuzzyMembership(f"{geobaza}\\aspect", fuzzy_function="LINEAR 90 135")
aspect_fuzzy_1 = arcpy.sa.FuzzyMembership(f"{geobaza}\\aspect", fuzzy_function="LINEAR 270 235")
aspect_overlay = arcpy.sa.FuzzyOverlay([aspect_fuzzy, aspect_fuzzy_1], 'AND')
aspect_overlay.save(f'{geobaza}\\kryterium_6')
exit()

# kryterium 7 - wezly
wezly_fuzzy = arcpy.sa.FuzzyMembership(wezly, fuzzy_function="LINEAR 8000 5000")
wezly_fuzzy.save(f'{geobaza}\\kryterium_7')

def licz_przydatnosc(wariant, waga_woda, waga_budynki, waga_lasy, waga_drogi, waga_wysokosc, waga_aspect, waga_wezly, prog_przydatnosci):
    tabela_kryteriow = arcpy.sa.WSTable([[f'{geobaza}\\kryterium_1', "VALUE", waga_woda], [f'{geobaza}\\kryterium_2', "VALUE", waga_budynki], [f'{geobaza}\\kryterium_3', "VALUE", waga_lasy], [f'{geobaza}\\kryterium_4', "VALUE", waga_drogi], [f'{geobaza}\\kryterium_5', "VALUE", waga_wysokosc], [f'{geobaza}\\kryterium_6', "VALUE", waga_aspect], [f'{geobaza}\\kryterium_7', "VALUE", waga_wezly]])
    weighted_sum = arcpy.sa.WeightedSum(tabela_kryteriow)
    weighted_sum.save(f'{geobaza}\\{wariant}_suma_rozmyte')

    kryteria_ostre = arcpy.sa.FuzzyOverlay([f"{geobaza}\\kryterium_1", f"{geobaza}\\kryterium_2", f"{geobaza}\\kryterium_3"], 'AND')
    kryteria_ostre.save(f'{geobaza}\\kryteria_ostre')

    suma = arcpy.sa.FuzzyOverlay([kryteria_ostre, weighted_sum], 'AND')
    suma.save(f'{geobaza}\\{wariant}_wynik')

    wynik_reclassified = arcpy.sa.Reclassify(suma, "VALUE", arcpy.sa.RemapRange([[0, prog_przydatnosci, 0], [prog_przydatnosci, 1, 1]]))
    wynik_reclassified.save(f'{geobaza}\\{wariant}_wynik_reclassified')

def wybierz_przydatne_dzialki(wariant, prog_przydatnosci):
    poligon_przydatnosci = "poligon_przydatnosci"
    arcpy.conversion.RasterToPolygon(f'{geobaza}\\{wariant}_wynik_reclassified', poligon_przydatnosci, "NO_SIMPLIFY", "VALUE")

    poligon_przydatnosci_layer = "poligon_przydatnosci_layer"
    arcpy.management.MakeFeatureLayer(poligon_przydatnosci, poligon_przydatnosci_layer)
    arcpy.management.SelectLayerByAttribute(poligon_przydatnosci_layer, "NEW_SELECTION", "gridcode = 1")
    arcpy.management.CopyFeatures(poligon_przydatnosci_layer, f"{geobaza}\\{wariant}_poligon_przydatnosci")

    dzialki_przeciete = "dzialki_przeciete"
    arcpy.analysis.Intersect([dzialki, poligon_przydatnosci], dzialki_przeciete, "ALL")
    arcpy.management.CopyFeatures(dzialki_przeciete, f"{geobaza}\\{wariant}_dzialki_przeciete_przez_poligony")

    arcpy.management.AddField(dzialki_przeciete, "pole", "DOUBLE")
    arcpy.management.CalculateField(dzialki_przeciete, "pole", "!shape.area@SQUAREMETERS!", "PYTHON3")

    arcpy.management.AddField(dzialki, "pole", "DOUBLE")
    arcpy.management.CalculateField(dzialki, "pole", "!shape.area@SQUAREMETERS!", "PYTHON3")

    arcpy.management.AddField(dzialki, "pole_przydatne", "DOUBLE")
    arcpy.management.CalculateField(dzialki, "pole_przydatne", 0, "PYTHON3")

    with arcpy.da.UpdateCursor(dzialki_przeciete, ["DZIALKAEWI", "pole", "gridcode"]) as cursor:
        for row in cursor:
            if row[2] == 1:
                with arcpy.da.UpdateCursor(dzialki, ["DZIALKAEWI", "pole", "pole_przydatne"]) as cursor2:
                    for row2 in cursor2:
                        if row[0] == row2[0]:
                            row2[2] += row[1]
                            cursor2.updateRow(row2)

    arcpy.management.AddField(dzialki, "przydatnosc", "DOUBLE")
    arcpy.management.CalculateField(dzialki, "przydatnosc", "(!pole_przydatne! / !pole!) * 100", "PYTHON3")

    dzialki_layer = "dzialki_layer"
    arcpy.management.MakeFeatureLayer(dzialki, dzialki_layer)
    arcpy.management.SelectLayerByAttribute(dzialki_layer, "NEW_SELECTION", f"przydatnosc > {prog_przydatnosci} AND shape_area > 20000 ")
    arcpy.management.CopyFeatures(dzialki_layer, f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_{prog_przydatnosci}")

# def stworz_przylacze(wariant, prog_przydatnosci):
#     pt_merged_layer = "pt_merged_layer"
#     arcpy.management.MakeFeatureLayer(pt_merged, pt_merged_layer)
#     arcpy.management.AddField(pt_merged_layer, "cost", "FLOAT")
#     arcpy.management.CalculateField(
#         in_table=pt_merged_layer,
#         field="cost",
#         expression="costs.get(!x_kod!, 0)",
#         expression_type="PYTHON3",
#         code_block="""costs = {
#         "PTWP01": 0, 
#         "PTWP02": 200,
#         "PTWP03": 0,
#         "PTZB02": 100,
#         "PTZB01": 200,
#         "PTZB05": 50,
#         "PTZB04": 200,
#         "PTZB03": 200,
#         "PTLZ01": 100,
#         "PTLZ02": 50,
#         "PTLZ03": 50,
#         "PTRK01": 15,
#         "PTRK02": 15,
#         "PTUT03": 100,
#         "PTUT02": 90,
#         "PTUT04": 20,
#         "PTUT05": 20,
#         "PTUT01": 0,
#         "PTTR02": 1,
#         "PTTR01": 20,
#         "PTKM02": 200,
#         "PTKM01": 100,
#         "PTKM03": 200,
#         "PTKM04": 0,
#         "PTGN01": 1,
#         "PTGN02": 1,
#         "PTGN03": 1,
#         "PTGN04": 1,
#         "PTPL01": 50,
#         "PTSO01": 0,
#         "PTSO02": 0,
#         "PTWZ01": 0,
#         "PTWZ02": 0,
#         "PTNZ01": 150,
#         "PTNZ02": 150
#         }"""
#     )

#     out_cost = arcpy.conversion.PolygonToRaster(
#         in_features=pt_merged_layer,
#         value_field="cost",
#         out_rasterdataset=f"{geobaza}\\{wariant}_cost_raster",
#         cell_assignment="CELL_CENTER",
#         cellsize=5
#     )

#     out_distance = arcpy.sa.CostDistance(
#         in_source_data=f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_{prog_przydatnosci}",
#         in_cost_raster=f"{geobaza}\\{wariant}_cost_raster",
#         maximum_distance=None,
#         out_backlink_raster=f"{geobaza}\\{wariant}_cost_backlink",
#         source_cost_multiplier=None,
#         source_start_cost=None,
#         source_resistance_rate=None,
#         source_capacity=None,
#         source_direction=""
#     )
#     out_distance.save(f"{geobaza}\\{wariant}_cost_distance")

#     out_path = arcpy.sa.CostPath(
#         in_destination_data=linie_elektroenergetyczne,
#         in_cost_distance_raster=f"{geobaza}\\{wariant}_cost_distance",
#         in_cost_backlink_raster=f"{geobaza}\\{wariant}_cost_backlink",
#         path_type="BEST_SINGLE",
#         force_flow_direction_convention="INPUT_RANGE"
#     )
#     out_path.save(f"{geobaza}\\{wariant}_cost_path")

#     path_vector = arcpy.conversion.RasterToPolyline(in_raster=out_path, out_polyline_features=f"{geobaza}\\{wariant}_cost_path_vector")

def licz(wariant, waga_woda, waga_budynki, waga_lasy, waga_drogi, waga_wysokosc, waga_aspect, waga_wezly, prog_przydatnosci_piksela, prog_przydatnosci_powierzchni):
    prog_przydatnosci_piksela = prog_przydatnosci_piksela / 100
    licz_przydatnosc(wariant, waga_woda, waga_budynki, waga_lasy, waga_drogi, waga_wysokosc, waga_aspect, waga_wezly, prog_przydatnosci_piksela)
    wybierz_przydatne_dzialki(wariant, prog_przydatnosci_powierzchni)
    # stworz_przylacze(wariant, prog_przydatnosci_powierzchni)

