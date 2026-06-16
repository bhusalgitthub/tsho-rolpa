import arcpy

arcpy.env.workspace = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\00_RAW_DATA\02_DEM'

# Reproject ALOS DEM to UTM Zone 45N (EPSG:32645)
arcpy.management.ProjectRaster(
    in_raster   = r'ALOS_PALSAR\output_AW3D30.tif',
    out_raster  = r'ALOS_PALSAR\AW3D30_UTM45N.tif',
    out_coor_system = arcpy.SpatialReference(32645),
    resampling_type = 'BILINEAR'
)
print('✓ Reprojected to UTM Zone 45N')