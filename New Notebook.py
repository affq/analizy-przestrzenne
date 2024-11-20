import arcpy

arcpy.env.workspace = "C:/Users/adria/OneDrive/Dokumenty/ArcGIS/Projects/MyProject12/MyProject12.gdb"
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("ETRS_1989_Poland_CS92")
arcpy.env.extent = "A03_Granice_gmin_Proj_Buffer"
arcpy.env.mask = "A03_Granice_gmin_Proj_Buffer"
arcpy.env.cellSize = 5
arcpy.env.overwriteOutput = True

swrs_0210_buffer = arcpy.analysis.Buffer('SWRS_L_0210', 'SWRS_L_0210_buffer', '1 Centimeter')
swrs_0212_buffer = arcpy.analysis.Buffer('SWRS_L_0212', 'SWRS_L_0212_buffer', '1 Centimeter')
water = arcpy.management.Merge([swrs_0210_buffer, swrs_0212_buffer, 'PTWP_A_0210', 'PTWP_A_0212'], 'water')

import arcpy.management
from arcpy.sa import *

out_distance_accumulation_raster = arcpy.sa.DistanceAccumulation(
    in_source_data=water,
    vertical_factor="BINARY 1 -30 30",
    horizontal_factor="BINARY 1 45",
    source_direction="",
    distance_method="PLANAR"
)

woda_rosnaca = FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 100 102")
woda_malejaca = FuzzyMembership(out_distance_accumulation_raster, fuzzy_function="LINEAR 400 200")
woda_mapa = FuzzyOverlay([woda_rosnaca, woda_malejaca], 'AND')


#kryterium 2
budynki = arcpy.management.Merge(['BUBD_A_0210', 'BUBD_A_0212'], 'budynki')
query = "FOBUD = 'budynki mieszkalne'"
arcpy.MakeFeatureLayer_management(budynki, "temp_layer", query)
arcpy.CopyFeatures_management("temp_layer", 'budynki_mieszkalne')
arcpy.Delete_management("temp_layer")
budynki_mieszkalne = "budynki_mieszkalne"

out_distance_accumulation_buildings = arcpy.sa.DistanceAccumulation(
    in_source_data=budynki_mieszkalne,
    vertical_factor="BINARY 1 -30 30",
    horizontal_factor="BINARY 1 45",
    source_direction="",
    distance_method="PLANAR"
)

budynki_mieszkalne = FuzzyMembership(out_distance_accumulation_buildings, fuzzy_function="LINEAR 150 1000")

#kryterium 3
ptlz = arcpy.management.Merge(['PTLZ_A_0210', 'PTLZ_A_0212'], 'ptlz')
query = "RODZAJ = 'las'"
arcpy.MakeFeatureLayer_management(ptlz, "temp_layer", query)
arcpy.CopyFeatures_management("temp_layer", 'ptlz_las')
arcpy.Delete_management("temp_layer")
ptlz_las = "ptlz_las"

out_distance_accumulation_ptlz = arcpy.sa.DistanceAccumulation(
    in_source_data=ptlz_las,
    vertical_factor="BINARY 1 -30 30",
    horizontal_factor="BINARY 1 45",
    source_direction="",
    distance_method="PLANAR"
)

lasy_fuzzy = FuzzyMembership(out_distance_accumulation_ptlz, fuzzy_function="LINEAR 15 100")

#kryterium 4 dostęp do dróg utwardzonych - jak największe zagęszczenie - ??
#kryterium 5 nachylenie stoków - optymalnie płasko; maksymalnie 10%

arcpy.ddd.Slope(
    in_raster="nmt",
    out_raster=r"slope",
    output_measurement="DEGREE",
    z_factor=1,
    method="PLANAR",
    z_unit="METER",
    analysis_target_device="GPU_THEN_CPU"
)

slope_fuzzy = FuzzyMembership("slope", fuzzy_function="LINEAR 10 1")

#kryterium 6

aspect = Aspect("nmt")

#135-225
aspect_fuzzy = FuzzyMembership(aspect, fuzzy_function="LINEAR 135 180")
aspect_fuzzy_1 = FuzzyMembership(aspect, fuzzy_function="LINEAR 225 181")
aspect_overlay = FuzzyOverlay([aspect_fuzzy, aspect_fuzzy_1], 'OR')

