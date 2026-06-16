import arcpy
import pandas as pd

profiles_3d = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\03_Moraine_Profile\Moraine_Profiles_3D.shp'

data = []
with arcpy.da.SearchCursor(profiles_3d, ['Profile_ID', 'SHAPE@']) as cursor:
    for row in cursor:
        for part in row[1]:
            for i, pt in enumerate(part):
                if pt:
                    data.append({
                        'Profile_ID':  row[0],
                        'Point_No':    i,
                        'Elevation_m': round(pt.Z, 1)
                    })

df = pd.DataFrame(data)

# Correct approach:
# Lake surface = minimum elevation on NORTH side of profile (lake side = first half of points)
# Moraine crest = maximum elevation across full profile
# Freeboard = crest - lake surface

print('='*55)
print('CORRECTED MORAINE ANALYSIS')
print('='*55)

for pid in df['Profile_ID'].unique():
    sub        = df[df['Profile_ID'] == pid].reset_index(drop=True)
    half       = len(sub) // 2
    lake_side  = sub.iloc[:half]   # north half = lake side
    down_side  = sub.iloc[half:]   # south half = downstream side

    crest      = sub['Elevation_m'].max()
    lake_surf  = lake_side['Elevation_m'].min()   # lowest point on lake side
    downstream = down_side['Elevation_m'].min()   # toe on downstream face
    freeboard  = crest - lake_surf
    dam_height = crest - downstream

    print(f'\n{pid}:')
    print(f'  Lake surface (approx):     {lake_surf:.1f} m')
    print(f'  Moraine crest:             {crest:.1f} m')
    print(f'  Downstream toe:            {downstream:.1f} m')
    print(f'  Freeboard (crest-lake):    {freeboard:.1f} m')
    print(f'  Dam height (crest-toe):    {dam_height:.1f} m')

print()
print('PUBLISHED REFERENCE VALUES (Tsho Rolpa):')
print('  Lake surface:   ~4,580 m')
print('  Moraine crest:  ~4,600 m')
print('  Freeboard:      ~3 m (after year 2000 mitigation)')
print('  Dam height:     ~60-80 m')
print()
print('NOTE: 30m DEM resolution introduces ±15m vertical error')
print('on narrow moraine features. Values are indicative, not survey-grade.')
print('ICIMOD 2019 bathymetry data will correct this in Phase 3.')