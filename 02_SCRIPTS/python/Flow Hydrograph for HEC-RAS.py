import pandas as pd
import numpy as np
import os

# HEC-RAS requires flow hydrograph in DSS or fixed-column text format
# We export a clean DSS-ready text file for each scenario

hyd_csv = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\04_Seismic_Layers\Hydrograph_TimeSeries.csv'
out_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(hyd_csv)

scenarios = {
    'S1_Partial_Breach':   'Scenario_1_Partial',
    'S2_Full_Breach':      'Scenario_2_Full',
    'S3_Cascade_Failure':  'Scenario_3_Cascade',
}

for sc_name, folder_name in scenarios.items():
    sc_dir = os.path.join(out_dir, folder_name)
    os.makedirs(sc_dir, exist_ok=True)

    df_sc = df[df['Scenario'] == sc_name][['Time_hrs', 'Q_m3s']].copy()
    df_sc = df_sc.reset_index(drop=True)

    # Convert hours to minutes for HEC-RAS
    df_sc['Time_min'] = (df_sc['Time_hrs'] * 60).round(1)

    # ── Write HEC-RAS compatible flow hydrograph text ──────────
    out_file = os.path.join(sc_dir, f'Inflow_Hydrograph_{sc_name}.txt')

    with open(out_file, 'w') as f:
        f.write(f'# HEC-RAS 2D Boundary Condition — Inflow Hydrograph\n')
        f.write(f'# Project: Tsho Rolpa GLOF Risk Assessment\n')
        f.write(f'# Scenario: {sc_name}\n')
        f.write(f'# Generated: Python — Froehlich (1995) equations\n')
        f.write(f'# Units: Time = minutes, Flow = m3/s\n')
        f.write(f'# Breach location: 86.4639E 27.8714N\n')
        f.write(f'#\n')
        f.write(f'# Time(min)    Flow(m3/s)\n')
        f.write(f'#\n')
        for _, row in df_sc.iterrows():
            f.write(f'{row["Time_min"]:>12.1f}  {row["Q_m3s"]:>14.2f}\n')

    peak_q   = df_sc['Q_m3s'].max()
    peak_t   = df_sc.loc[df_sc['Q_m3s'].idxmax(), 'Time_min']
    duration = df_sc['Time_min'].max()

    print(f'{sc_name}:')
    print(f'  Output: {out_file}')
    print(f'  Points: {len(df_sc)} time steps')
    print(f'  Peak Q: {peak_q:,.0f} m³/s at t={peak_t:.0f} min')
    print(f'  Duration: {duration:.0f} min ({duration/60:.1f} hrs)')
    print()

# ── Also export DEM for HEC-RAS terrain ────────────────────────
print('='*55)
print('HEC-RAS SETUP CHECKLIST')
print('='*55)
print()
print('FILES READY:')
print(f'  ✓ S1 hydrograph: Scenario_1_Partial/')
print(f'  ✓ S2 hydrograph: Scenario_2_Full/')
print(f'  ✓ S3 hydrograph: Scenario_3_Cascade/')
print()
print('FILES NEEDED FROM ARCGIS:')
print(f'  → Export AW3D30_UTM45N.tif as HEC-RAS terrain')
print(f'    In ArcGIS: Analysis → Tools → search "RAS Terrain"')
print(f'    OR use the .tif directly — HEC-RAS 6.5 reads GeoTIFF')
print()
print('HEC-RAS SETUP STEPS:')
print('  1. Open HEC-RAS 6.5')
print('  2. File → New Project')
print('     Name: TSHO_ROLPA_GLOF')
print(f'    Save to: {out_dir}')
print('  3. Edit → Geometric Data → 2D Flow Areas')
print('  4. RAS Mapper → New Terrain → load AW3D30_UTM45N.tif')
print('  5. Draw 2D flow area from dam → Sunkoshi (180km)')
print('  6. Boundary Conditions → load hydrograph txt files')
print('  7. Run → Unsteady Flow → compute')
print()