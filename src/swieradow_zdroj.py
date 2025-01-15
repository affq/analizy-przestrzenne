import arcpy.analysis
import arcpy.management
import arcpy.sa

# geobaza = r"C:\Users\adria\Desktop\STUDIA_FOLDERY\analizy\Plesna\Plesna.gdb"
# arcpy.env.workspace = "in_memory"
# arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRF2000-PL_CS92")
# arcpy.env.extent = f"{geobaza}\\gmina_buffer"
# arcpy.env.mask = f"{geobaza}\\gmina_buffer"
# arcpy.env.cellSize = 5
# arcpy.env.overwriteOutput = True

# swrs = arcpy.analysis.Buffer(f"{geobaza}\\SWRS_L", f"{geobaza}\\SWRS_L_buffer", '1 Centimeter')
# ptwp = f"{geobaza}\\PTWP_A"
# water = arcpy.management.Merge([swrs, ptwp], 'water')
# buildings = f"{geobaza}\\BUBD_A"
# ptlz = f"{geobaza}\\PTLZ_A"
# nmt = f'{geobaza}\\nmt'
# drogi = f"{geobaza}\\SKDR_L"
# wezly = f"{geobaza}\\wezly"
# dzialki = f'{geobaza}\\dzialki'
# pt_merged = f'{geobaza}\\pokrycie_terenu'
# linie_elektroenergetyczne = f'{geobaza}\\SULN_L'


# geobaza = r"C:/Users/adria/OneDrive/Pulpit/analizy-przestrzenne/MyProject12/MyProject12.gdb"
geobaza = r"C:\Users\adria\Desktop\STUDIA_FOLDERY\analizy\MyProject12\MyProject12.gdb"
arcpy.env.workspace = "in_memory"
# arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRS_1989_Poland_CS92")
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRF2000-PL_CS92")
arcpy.env.extent = f"{geobaza}\\gmina_buffer"
arcpy.env.mask = f"{geobaza}\\gmina_buffer"
arcpy.env.cellSize = 5
arcpy.env.overwriteOutput = True

swrs_0210_buffer = arcpy.analysis.Buffer(f'{geobaza}\\SWRS_L_0210', f'{geobaza}\\SWRS_L_0210_buffer', '1 Centimeter')
swrs_0212_buffer = arcpy.analysis.Buffer(f'{geobaza}\\SWRS_L_0212', f'{geobaza}\\SWRS_L_0212_buffer', '1 Centimeter')
water = arcpy.management.Merge([swrs_0210_buffer, swrs_0212_buffer, f'{geobaza}\\PTWP_A_0210', f'{geobaza}\\PTWP_A_0212'], 'water')
buildings = arcpy.management.Merge([f'{geobaza}\\BUBD_A_0210', f'{geobaza}\\BUBD_A_0212'], 'buildings')
ptlz = arcpy.management.Merge([f'{geobaza}\\PTLZ_A_0210', f'{geobaza}\\PTLZ_A_0212'], 'ptlz')
nmt = f'{geobaza}\\nmt'
drogi = arcpy.management.Merge([f'{geobaza}\\SKDR_L_0210', f'{geobaza}\\SKDR_L_0212'], 'drogi')
wezly = f'{geobaza}\\wezly_raster'
dzialki = f'{geobaza}\\dzialki'
pt_merged = f'{geobaza}\\PT_merged'
linie_elektroenergetyczne = arcpy.management.Merge([f'{geobaza}\\SULN_L_0210', f'{geobaza}\\SULN_L_0212'], 'linie_elektroenergetyczne')

#kryterium 1
water_accumulation = arcpy.sa.DistanceAccumulation(in_source_data=water)
increasing_water = arcpy.sa.FuzzyMembership(water_accumulation, fuzzy_function="LINEAR 100 102")
decreasing_water = arcpy.sa.FuzzyMembership(water_accumulation, fuzzy_function="LINEAR 1000 500")
water_map = arcpy.sa.FuzzyOverlay([increasing_water, decreasing_water], 'AND')
water_map.save(f'{geobaza}\\kryterium_1')

#kryterium 2
query = "FOBUD = 'budynki mieszkalne'"
arcpy.analysis.Select(buildings, 'residential_buildings', query)
buildings_accumulation = arcpy.sa.DistanceAccumulation(in_source_data='residential_buildings')
residential_buildings = arcpy.sa.FuzzyMembership(buildings_accumulation, fuzzy_function="LINEAR 150 300")
residential_buildings.save(f'{geobaza}\\kryterium_2')

#kryterium 3
query = "RODZAJ = 'las'"
arcpy.analysis.Select(ptlz, 'ptlz_las', query)
out_distance_accumulation_ptlz = arcpy.sa.DistanceAccumulation(in_source_data="ptlz_las")
lasy_fuzzy = arcpy.sa.FuzzyMembership(out_distance_accumulation_ptlz, fuzzy_function="LINEAR 15 100")
lasy_fuzzy.save(f'{geobaza}\\kryterium_3')

#kryterium 4 
query = "MATE_NAWIE IN ('beton', 'bruk', 'kostka kamienna', 'kostka prefabrykowana', 'masa bitumiczna', 'płyty betonowe')"
drogi_utwardzone = arcpy.analysis.Select(drogi, 'drogi_utwardzone', query)

density = arcpy.sa.LineDensity(
    in_polyline_features=drogi_utwardzone,
    population_field=None,
    cell_size=5,
    search_radius=1000,
    area_unit_scale_factor="SQUARE_KILOMETERS",
)
density.save(f'{geobaza}\\drogi_density')

arcpy.management.CalculateStatistics(density)
max_value = density.maximum

kryterium_4 = arcpy.sa.RescaleByFunction(
    in_raster=density,
    transformation_function=f"LINEAR 0 {0.5 * max_value}",
    from_scale=0,
    to_scale=1   
)
kryterium_4.save(f'{geobaza}\\kryterium_4')

#kryterium 5
arcpy.ddd.Slope(nmt, "slope", "PERCENT_RISE", 1)
slope_fuzzy = arcpy.sa.FuzzyMembership("slope", fuzzy_function="LINEAR 10 7")
slope_fuzzy.save(f'{geobaza}\\kryterium_5')

#kryterium 6
aspect = arcpy.ddd.Aspect(nmt)
increasing_aspect = arcpy.sa.FuzzyMembership(aspect, fuzzy_function="LINEAR 90 113")
decreasing_aspect = arcpy.sa.FuzzyMembership(aspect, fuzzy_function="LINEAR 270 248")
aspect_overlay = arcpy.sa.FuzzyOverlay([increasing_aspect, decreasing_aspect], 'AND')
aspect_overlay.save(f'{geobaza}\\kryterium_6')

#kryterium 7 - wezly
wezly_max = float(arcpy.management.GetRasterProperties(wezly, "MAXIMUM")[0].replace(',', '.'))
wezly_fuzzy = arcpy.sa.FuzzyMembership(wezly, fuzzy_function=f"LINEAR {wezly_max} {0.5 * wezly_max}")
wezly_fuzzy.save(f'{geobaza}\\kryterium_7')

def licz_przydatnosc(wariant, waga_woda, waga_budynki, waga_lasy, waga_drogi, waga_wysokosc, waga_aspect, waga_wezly, prog_przydatnosci):
    tabela_kryteriow = arcpy.sa.WSTable([[f'{geobaza}\\kryterium_1', "VALUE", waga_woda], [f'{geobaza}\\kryterium_2', "VALUE", waga_budynki], [f'{geobaza}\\kryterium_3', "VALUE", waga_lasy], [f'{geobaza}\\kryterium_4', "VALUE", waga_drogi], [f'{geobaza}\\kryterium_5', "VALUE", waga_wysokosc], [f'{geobaza}\\kryterium_6', "VALUE", waga_aspect], [f'{geobaza}\\kryterium_7', "VALUE", waga_wezly]])
    weighted_sum = arcpy.sa.WeightedSum(tabela_kryteriow)
    weighted_sum.save(f'{geobaza}\\{wariant}_suma_rozmyte')

    kryteria_ostre = arcpy.sa.FuzzyOverlay([increasing_water, f"{geobaza}\\kryterium_2", f"{geobaza}\\kryterium_3"], 'AND')
    kryteria_ostre.save(f'{geobaza}\\kryteria_ostre')

    iloczyn = arcpy.sa.FuzzyOverlay([kryteria_ostre, weighted_sum], 'AND')
    iloczyn.save(f'{geobaza}\\{wariant}_wynik')
    arcpy.management.CalculateStatistics(iloczyn)
    max_przydatnosc = iloczyn.maximum

    wynik_reclassified = arcpy.sa.Reclassify(iloczyn, "VALUE", arcpy.sa.RemapRange([[0, prog_przydatnosci * max_przydatnosc, 0], [prog_przydatnosci * max_przydatnosc, 1, 1]]))
    wynik_reclassified.save(f'{geobaza}\\{wariant}_wynik_reclassified')

def wybierz_przydatne_dzialki(wariant, prog_przydatnosci, prog_powierzchni):
    arcpy.conversion.RasterToPolygon(f'{geobaza}\\{wariant}_wynik_reclassified', 'poligon_przydatnosci', "NO_SIMPLIFY", "VALUE")
    arcpy.management.MakeFeatureLayer('poligon_przydatnosci', "poligon_przydatnosci_layer")
    arcpy.management.SelectLayerByAttribute("poligon_przydatnosci_layer", "NEW_SELECTION", "gridcode = 1")
    arcpy.management.CopyFeatures("poligon_przydatnosci_layer", f"{geobaza}\\{wariant}_poligon_przydatnosci")
    
    arcpy.analysis.SummarizeWithin(
        in_polygons=dzialki,
        in_sum_features=f"{geobaza}\\{wariant}_poligon_przydatnosci",
        out_feature_class=f'{geobaza}\\{wariant}_summarized_within',
        keep_all_polygons="ONLY_INTERSECTING",
        shape_unit="SQUAREMETERS",
        add_group_percent="NO_PERCENT",
    )

    arcpy.management.CalculateField(
        in_table=f'{geobaza}\\{wariant}_summarized_within',
        field="pow_przyd",
        expression="100*!sum_Area_squaremeters!/!Shape_Area!",
        expression_type="PYTHON3",
        code_block="",
        field_type="FLOAT"
    )

    arcpy.management.MakeFeatureLayer(f'{geobaza}\\{wariant}_summarized_within', f'{geobaza}\\{wariant}_summarized_within_layer')
    dzialki_przydatne_powyzej_progu = arcpy.management.SelectLayerByAttribute(f'{geobaza}\\{wariant}_summarized_within_layer', "NEW_SELECTION", f"pow_przyd >= {prog_przydatnosci}")
    arcpy.management.CopyFeatures(dzialki_przydatne_powyzej_progu, f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej")

    arcpy.management.Dissolve(
        in_features=f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej",
        out_feature_class=f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_dissolve",
        multi_part="SINGLE_PART",
        unsplit_lines="DISSOLVE_LINES",
        concatenation_separator=""
    )

    arcpy.management.MakeFeatureLayer(f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_dissolve", f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_dissolve_layer")
    arcpy.management.SelectLayerByAttribute(f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_dissolve_layer", "NEW_SELECTION", "Shape_Area >= 20000")
    arcpy.management.CopyFeatures(f"{geobaza}\\{wariant}_dzialki_przydatne_powyzej_dissolve_layer", f"{geobaza}\\{wariant}_grupy_dzialek_przydatne_powyzej_{prog_powierzchni}")

def stworz_przylacze(wariant, prog_przydatnosci):
    pt_merged_layer = "pt_merged_layer"
    arcpy.management.MakeFeatureLayer(pt_merged, pt_merged_layer)
    arcpy.management.AddField(pt_merged_layer, "cost", "FLOAT")
    arcpy.management.CalculateField(
        in_table=pt_merged_layer,
        field="cost",
        expression="costs.get(!x_kod!, 0)",
        expression_type="PYTHON3",
        code_block="""costs = {
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

    arcpy.conversion.PolygonToRaster(
        in_features=pt_merged_layer,
        value_field="cost",
        out_rasterdataset=f"{geobaza}\\{wariant}_cost_raster",
        cell_assignment="CELL_CENTER",
        cellsize=5
    )

    out_distance = arcpy.sa.CostDistance(
        in_source_data=f"{geobaza}\\{wariant}_grupy_dzialek_przydatne_powyzej_{prog_przydatnosci}",
        in_cost_raster=f"{geobaza}\\{wariant}_cost_raster",
        out_backlink_raster=f"{geobaza}\\{wariant}_cost_backlink",
    )
    out_distance.save(f"{geobaza}\\{wariant}_cost_distance")

    out_path = arcpy.sa.CostPath(
        in_destination_data=linie_elektroenergetyczne,
        in_cost_distance_raster=f"{geobaza}\\{wariant}_cost_distance",
        in_cost_backlink_raster=f"{geobaza}\\{wariant}_cost_backlink",
        path_type="BEST_SINGLE",
        force_flow_direction_convention="INPUT_RANGE"
    )
    out_path.save(f"{geobaza}\\{wariant}_cost_path")
    arcpy.conversion.RasterToPolyline(in_raster=out_path, out_polyline_features=f"{geobaza}\\{wariant}_cost_path_vector")

def licz(wariant, waga_woda, waga_budynki, waga_lasy, waga_drogi, waga_wysokosc, waga_aspect, waga_wezly, prog_przydatnosci_piksela, prog_przydatnosci_powierzchni):
    prog_przydatnosci_piksela = prog_przydatnosci_piksela / 100
    licz_przydatnosc(wariant, waga_woda, waga_budynki, waga_lasy, waga_drogi, waga_wysokosc, waga_aspect, waga_wezly, prog_przydatnosci_piksela)
    wybierz_przydatne_dzialki(wariant, prog_przydatnosci_piksela, prog_przydatnosci_powierzchni)
    stworz_przylacze(wariant, prog_przydatnosci_powierzchni)
                     
