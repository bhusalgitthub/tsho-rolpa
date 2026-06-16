import pandas as pd
import numpy as np
import os

out_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

# Rebuild hydrographs at full resolution with correct peaks
scenarios = {
    'S1_Partial_Breach':  {'Qp': 20711, 'tp': 0.497, 'tf': 1.49, 'folder': 'Scenario_1_Partial'},
    'S2_Full_Breach':     {'Qp': 66352, 'tp': 0.417, 'tf': 1.25, 'folder': 'Scenario_2_Full'},
    'S3_Cascade_Failure': {'Qp': 107487,'tp': 0.303, 'tf': 0.91, 'folder': 'Scenario_3_Cascade'},
}

def build_hydrograph_full(Qp, tp_hrs, tf_hrs, duration_hrs=24, dt=0.01):
    t = np.arange(0, duration_hrs + dt, dt)
    Q = np.zeros(len(t))
    for i, ti in enumerate(t):
        if ti <= tp_hrs:
            Q[i] = Qp * (ti / tp_hrs)
        else:
            k    = np.log(0.001) / (tf_hrs - tp_hrs)
            Q[i] = Qp * np.exp(k * (ti - tp_hrs))
    return t, Q

for sc_name, sc in scenarios.items():
    sc_dir = os.path.join(out_dir, sc['folder'])
    os.makedirs(sc_dir, exist_ok=True)

    t, Q = build_hydrograph_full(sc['Qp'], sc['tp'], sc['tf'])

    out_file = os.path.join(sc_dir, f'Inflow_{sc_name}.txt')
    with open(out_file, 'w') as f:
        f.write(f'# HEC-RAS Inflow Hydrograph — {sc_name}\n')
        f.write(f'# Time(min)    Flow(m3/s)\n')
        for ti, qi in zip(t, Q):
            f.write(f'{ti*60:>12.2f}  {qi:>14.2f}\n')

    print(f'{sc_name}:')
    print(f'  Peak Q:    {Q.max():,.0f} m³/s at t={t[Q.argmax()]*60:.1f} min')
    print(f'  Points:    {len(t)}')
    print(f'  Saved:     {out_file}')
    print()

print('✓ All hydrographs rebuilt at full resolution')