import arcpy

dem = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\00_RAW_DATA\02_DEM\ALOS_PALSAR\AW3D30_UTM45N.tif'
out = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\02_DEM_Conditioned\Hillshade_AW3D30.tif'

import os
os.makedirs(os.path.dirname(out), exist_ok=True)

arcpy.ddd.HillShade(
    in_raster       = dem,
    out_raster      = out,
    azimuth         = 315,   # light from northwest — standard
    altitude        = 45,    # sun angle
    model_shadows   = 'SHADOWS',
    z_factor        = 1
)
print('✓ Hillshade created')