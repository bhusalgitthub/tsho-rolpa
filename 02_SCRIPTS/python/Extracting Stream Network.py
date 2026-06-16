import arcpy
arcpy.env.overwriteOutput = True

out = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\02_DEM_Conditioned'

# Correct Tsho Rolpa coordinates (more precise)
TSHO_LON = 86.4850
TSHO_LAT = 27.8742

# Extract stream network from flow accumulation
# Threshold: pixels with >500 upstream cells = stream
print('Extracting stream network...')
flow_acc = arcpy.sa.Raster(out + r'\FlowAccumulation.tif')
streams  = arcpy.sa.Con(flow_acc > 500, 1)
streams.save(out + r'\Streams_Raster.tif')

# Convert to vector lines
arcpy.sa.StreamToFeature(
    in_stream_raster    = out + r'\Streams_Raster.tif',
    in_flow_direction_raster = out + r'\FlowDirection.tif',
    out_polyline_features = out + r'\StreamNetwork.shp',
    simplify            = 'SIMPLIFY'
)
print('✓ Stream network extracted')
print('Drag StreamNetwork.shp onto the map — you should see river lines through the valley')