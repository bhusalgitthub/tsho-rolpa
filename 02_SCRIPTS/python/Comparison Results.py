import h5py, numpy as np, pandas as pd

ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

# Na Village coordinates (UTM Zone 45N approximate)
# 86.4198E, 27.8838N
NA_VILLAGE_LON = 86.4198
NA_VILLAGE_LAT = 27.8838

scenarios = {
    'S2_Full_66352':     ('tshorolpa.p04.hdf', 'Rolwaling River'),
    'S3_Cascade_107487': ('tshorolpa.p05.hdf', 'Rolwaling River'),
}

results = []

for sc_name, (hdf_file, area) in scenarios.items():
    path = ras_dir + '\\' + hdf_file
    
    with h5py.File(path, 'r') as f:
        base = f'Results/Unsteady/Output/Output Blocks/Base Output'
        
        # Cell coordinates
        coords = f[f'Geometry/2D Flow Areas/{area}/Cells Center Coordinate'][:]
        
        # Max water surface per cell
        max_wse = f[f'{base}/Summary Output/2D Flow Areas/{area}/Maximum Water Surface'][0, :]
        
        # Min elevation per cell  
        min_elev = f[f'Geometry/2D Flow Areas/{area}/Cells Minimum Elevation'][:]
        
        # Max depth = max WSE - cell elevation
        max_depth = max_wse - min_elev
        max_depth = np.where(max_depth < 0, 0, max_depth)
        
        # Time series water surface (481 or 121 timesteps x cells)
        wse_ts = f[f'{base}/Unsteady Time Series/2D Flow Areas/{area}/Water Surface'][:]
        times  = f[f'{base}/Unsteady Time Series/Time'][:]
        
        # Max velocity
        max_vel = f[f'{base}/Summary Output/2D Flow Areas/{area}/Maximum Face Velocity'][0, :]
        
        # Find cell nearest to Na Village
        # coords are in UTM — convert Na Village to UTM approx
        # UTM 45N: lon 86.42 ≈ 447000E, lat 27.88 ≈ 3083000N
        na_utm_e = 447000
        na_utm_n = 3083000
        
        distances = np.sqrt((coords[:, 0] - na_utm_e)**2 + 
                           (coords[:, 1] - na_utm_n)**2)
        na_cell = np.argmin(distances)
        na_dist_m = distances[na_cell]
        
        # Water surface at Na Village cell over time
        na_wse_ts = wse_ts[:, na_cell]
        na_elev    = min_elev[na_cell]
        na_depth_ts = np.maximum(0, na_wse_ts - na_elev)
        
        # Find flood arrival time at Na Village
        # First timestep where depth > 0.1m
        arrival_idx = np.where(na_depth_ts > 0.1)[0]
        if len(arrival_idx) > 0:
            arrival_time_hrs = times[arrival_idx[0]]
            arrival_min = arrival_time_hrs * 60
        else:
            arrival_min = None
        
        # Overall stats
        flooded_cells = np.sum(max_depth > 0.1)
        total_cells   = len(max_depth)
        flood_area_km2 = flooded_cells * (200*200) / 1e6  # 200m cells
        
        print(f'\n{"="*55}')
        print(f'SCENARIO: {sc_name}')
        print(f'{"="*55}')
        print(f'  Total cells:          {total_cells}')
        print(f'  Flooded cells (>0.1m):{flooded_cells}')
        print(f'  Flood area:           {flood_area_km2:.2f} km²')
        print(f'  Max depth anywhere:   {max_depth.max():.1f} m')
        print(f'  Max velocity:         {max_vel.max():.1f} m/s')
        print()
        print(f'  NA VILLAGE (nearest cell {na_dist_m:.0f}m away):')
        print(f'    Ground elevation:   {na_elev:.0f} m')
        print(f'    Max flood depth:    {na_depth_ts.max():.1f} m')
        print(f'    Arrival time:       {arrival_min:.0f} min' if arrival_min else '    No flood detected')
        
        results.append({
            'Scenario': sc_name,
            'Flood_Area_km2': round(flood_area_km2, 2),
            'Max_Depth_m': round(float(max_depth.max()), 1),
            'Max_Velocity_ms': round(float(max_vel.max()), 1),
            'Na_Village_MaxDepth_m': round(float(na_depth_ts.max()), 1),
            'Na_Village_Arrival_min': round(float(arrival_min), 0) if arrival_min else 'No flood'
        })

# Save results
df = pd.DataFrame(results)
out = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\04_OUTPUTS\Tables\Flood_Comparison.csv'
import os; os.makedirs(os.path.dirname(out), exist_ok=True)
df.to_csv(out, index=False)
print(f'\n✓ Results saved: {out}')
print(df.to_string(index=False))