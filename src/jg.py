arcpy.management.CalculateField(
    in_table=dzialki_przydatne_rozne_wagi,
    field="pow_przyd",
    expression="100*!sum_Area_H!/(!Shape_Area! / 10000)",
    expression_type="PYTHON3",
    code_block="",
    field_type="FLOAT",
    enforce_domains="NO_ENFORCE_DOMAINS"
)

#wybranie tych działek, których min. 60% powierzchni stanowią obszary przydatne i zapisanie ich do nowej warstwy
dzialki_przydatne_rozne_wagi_60 = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=dzialki_przydatne_rozne_wagi,
    selection_type="NEW_SELECTION",
    where_clause="pow_przyd >= 60"
)
arcpy.management.CopyFeatures(dzialki_przydatne_rozne_wagi_60, 'dzialki_przydatne_rozne_wagi_60')

#połączenie sąsiadujących działek w jeden obiekt 
arcpy.management.Dissolve(
    in_features="dzialki_przydatne_rozne_wagi_60",
    out_feature_class="dzialki_rozne_wagi_dissolve",
    dissolve_field=None,
    statistics_fields=None,
    multi_part="SINGLE_PART",
    unsplit_lines="DISSOLVE_LINES",
    concatenation_separator=""
)

#obliczenie powierzchni (w m2) i obwodu (w m) działek po połączeniu 
arcpy.management.CalculateGeometryAttributes(
    in_features="dzialki_rozne_wagi_dissolve",
    geometry_property="area AREA;obw PERIMETER_LENGTH",
    length_unit="METERS",
    area_unit="SQUARE_METERS",
    coordinate_system='PROJCS["ETRF2000-PL_CS92",GEOGCS["ETRF2000-PL",DATUM["ETRF2000_Poland",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",-5300000.0],PARAMETER["Central_Meridian",19.0],PARAMETER["Scale_Factor",0.9993],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]',
    coordinate_format="SAME_AS_INPUT"
)
    
#wybranie działek/grup działek które mają powierzchnię minimum 2ha i zapisanie ich do nowej warstwy
dzialki_rozne_wagi_2ha = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="dzialki_rozne_wagi_dissolve",
    selection_type="NEW_SELECTION",
    where_clause="area >= 20000"
)
arcpy.management.CopyFeatures(dzialki_rozne_wagi_2ha, 'dzialki_rozne_wagi_2ha')

#stworzenie otoczki wypukłej dla działek by otrzymać atrubuty geometrii dla grup działek
arcpy.management.MinimumBoundingGeometry(
    in_features="dzialki_rozne_wagi_2ha",
    out_feature_class="dzialki_rozne_wagi_otoczka",
    geometry_type="RECTANGLE_BY_WIDTH",
    group_option="NONE",
    group_field=None,
    mbg_fields_option="MBG_FIELDS"
)
arcpy.management.JoinField(
    in_data="dzialki_rozne_wagi_2ha",
    in_field="FID",
    join_table="dzialki_rozne_wagi_otoczka",
    join_field="FID",
    fields="MBG_Width",
    fm_option="NOT_USE_FM",
    field_mapping=None,
    index_join_fields="NO_INDEXES"
)
#wybranie grup działek, które mają szerokośc min. 50 metrów i zapisanie ich do nowej warstwy
dzialki_rozne_wagi_szerokosc50 = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="dzialki_rozne_wagi_2ha",
    selection_type="NEW_SELECTION",
    where_clause="MBG_Width >= 50"
)
arcpy.management.CopyFeatures(dzialki_rozne_wagi_szerokosc50, 'dzialki_rozne_wagi_szerokosc50')