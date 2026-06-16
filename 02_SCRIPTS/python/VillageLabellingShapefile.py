import arcpy, os

out_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED'
sr_wgs = arcpy.SpatialReference(4326)
arcpy.env.overwriteOutput = True

# Create point feature class for village labels
fc = out_dir + r'\Villages_Labels.shp'
arcpy.management.CreateFeatureclass(out_dir, 'Villages_Labels.shp', 
                                     'POINT', spatial_reference=sr_wgs)
arcpy.management.AddField(fc, 'Name', 'TEXT')
arcpy.management.AddField(fc, 'Population', 'LONG')
arcpy.management.AddField(fc, 'Elevation_m', 'DOUBLE')

villages = [
    (86.4198, 27.8838, 'Na Village',     400,  4180),
    (86.3737, 27.9024, 'Beding Village', 800,  3690),
    (86.4595, 27.8722, 'Moraine Dam',    0,    4600),
    (86.3197, 27.9035, 'Downstream BC',  0,    3200),
]

with arcpy.da.InsertCursor(fc, ['SHAPE@XY', 'Name', 'Population', 'Elevation_m']) as cur:
    for lon, lat, name, pop, elev in villages:
        cur.insertRow([(lon, lat), name, pop, elev])

print('✓ Village labels created')
print('Drag Villages_Labels.shp onto ArcGIS Pro map')
print('Then: right-click layer → Label → use Name field')