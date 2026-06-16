import arcpy
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension('Spatial')

dem = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\00_RAW_DATA\02_DEM\ALOS_PALSAR\AW3D30_UTM45N.tif'
out = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\02_DEM_Conditioned'

import os
os.makedirs(out, exist_ok=True)

# Step 1: Fill sinks
print('Filling sinks...')
filled = arcpy.sa.Fill(dem)
filled.save(out + r'\DEM_Filled.tif')
print('  ✓ Sinks filled')

# Step 2: Flow direction
print('Computing flow direction...')
flow_dir = arcpy.sa.FlowDirection(filled, 'NORMAL')
flow_dir.save(out + r'\FlowDirection.tif')
print('  ✓ Flow direction done')

# Step 3: Flow accumulation
print('Computing flow accumulation...')
flow_acc = arcpy.sa.FlowAccumulation(flow_dir)
flow_acc.save(out + r'\FlowAccumulation.tif')
print('  ✓ Flow accumulation done')

print('\n✓ All three layers created. Drag them onto the map to verify.')