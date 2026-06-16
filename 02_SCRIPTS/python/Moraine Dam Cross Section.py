import arcpy
arcpy.env.overwriteOutput = True

dem  = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\00_RAW_DATA\02_DEM\ALOS_PALSAR\AW3D30_UTM45N.tif'
out  = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\03_Moraine_Profile'

import os
os.makedirs(out, exist_ok=True)

# Draw 3 cross-section lines across the moraine dam
# These are real coordinates across the Tsho Rolpa terminal moraine
# Line goes from lake side → over moraine crest → downstream face

sr_utm = arcpy.SpatialReference(32645)  # UTM Zone 45N

# Convert moraine endpoints from WGS84 to UTM
# Moraine sits at approximately 86.475E, 27.868N
# Lines run north-south across the dam crest

moraine_lines = {
    'Profile_West':   [(86.472, 27.875), (86.472, 27.862)],
    'Profile_Center': [(86.475, 27.875), (86.475, 27.862)],
    'Profile_East':   [(86.478, 27.875), (86.478, 27.862)],
}

sr_wgs = arcpy.SpatialReference(4326)

# Create a line feature class
fc = out + r'\Moraine_CrossSections.shp'
arcpy.management.CreateFeatureclass(out, 'Moraine_CrossSections.shp', 'POLYLINE', spatial_reference=sr_wgs)
arcpy.management.AddField(fc, 'Profile_ID', 'TEXT')

with arcpy.da.InsertCursor(fc, ['SHAPE@', 'Profile_ID']) as cursor:
    for name, coords in moraine_lines.items():
        pts = arcpy.Array([arcpy.Point(x, y) for x, y in coords])
        line = arcpy.Polyline(pts, sr_wgs)
        cursor.insertRow([line, name])

print('✓ 3 cross-section lines created across moraine dam')

# Extract elevation profile along each line
arcpy.sa.InterpolateShape(
    in_surface          = dem,
    in_feature_class    = fc,
    out_feature_class   = out + r'\Moraine_Profiles_3D.shp',
    sample_distance     = 30
)
print('✓ Elevation profiles extracted — 30m sample spacing')
print('Drag Moraine_CrossSections.shp onto map to see the 3 profile lines across the dam')