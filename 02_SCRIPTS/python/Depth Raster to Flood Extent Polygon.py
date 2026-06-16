import arcpy, os

arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')

out_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\04_OUTPUTS\Maps\03_Flood_Inundation'

for scenario, raster in [('S2', 'S2_FloodExtent_Max.tif'),
                          ('S3', 'S3_FloodExtent_Max.tif')]:
    ras_path = os.path.join(out_dir, raster)
    if not os.path.exists(ras_path):
        print(f'{scenario}: file not found — export from RAS Mapper first')
        continue
    
    # Convert depth raster to flood extent polygon
    ras = arcpy.sa.Raster(ras_path)
    
    # Threshold: cells with depth > 0.5m = flooded
    flood_mask = arcpy.sa.Con(ras > 0.5, 1)
    flood_mask.save(out_dir + f'\\{scenario}_FloodMask.tif')
    
    # Convert to polygon
    arcpy.conversion.RasterToPolygon(
        flood_mask,
        out_dir + f'\\{scenario}_FloodPolygon.shp',
        'SIMPLIFY', 'Value'
    )
    
    # Calculate area
    arcpy.management.AddGeometryAttributes(
        out_dir + f'\\{scenario}_FloodPolygon.shp',
        'AREA', Area_Unit='SQUARE_KILOMETERS'
    )
    
    total_area = sum([row[0] for row in 
                      arcpy.da.SearchCursor(
                          out_dir + f'\\{scenario}_FloodPolygon.shp', 
                          ['POLY_AREA'])])
    
    print(f'{scenario}: {total_area:.1f} km² inundated')

print('✓ Flood polygons ready for mapping')