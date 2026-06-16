import pandas as pd

dem_path = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\00_RAW_DATA\02_DEM\ALOS_PALSAR\AW3D30_UTM45N.tif'

# Read elevation at Tsho Rolpa using rasterio
try:
    import rasterio
    from rasterio.transform import rowcol
except ImportError:
    print("Error: rasterio is not installed. Install it using: pip install rasterio")
    exit(1)

with rasterio.open(dem_path) as src:
    # Convert lat/lon to pixel row/col
    row, col = rowcol(src.transform, 86.47, 27.88)
    value = list(src.sample([(86.47, 27.88)]))[0][0]
    print(f'Elevation at Tsho Rolpa (86.47E, 27.88N): {value:.0f} m')
    print(f'Expected: ~4580m')
    print(f'CRS: {src.crs}')
