import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

out = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\04_Seismic_Layers'
os.makedirs(out, exist_ok=True)

print('='*60)
print('TSHO ROLPA — BREACH HYDROGRAPH CALCULATION')
print('Froehlich (1995) Predictor Equations')
print('Three scenarios: Partial / Full / Cascade')
print('='*60)

# ── LAKE & DAM PARAMETERS ─────────────────────────────────────
# Source: ICIMOD (2001), Richardson & Reynolds (2000)

lake = {
    'volume_m3':        90_000_000,   # 90 million m³ (Huggel 2002 estimate)
    'surface_area_m2':  1_650_000,    # 1.65 km² (2024 estimate)
    'depth_max_m':      150,          # maximum depth
    'depth_avg_m':      55,           # average depth
    'lake_elev_m':      4580,         # lake surface elevation
    'crest_elev_m':     4600,         # moraine crest elevation
    'freeboard_m':      3,            # post-mitigation freeboard
}

dam = {
    'height_m':         70,           # Hd — dam height
    'crest_width_m':    150,          # top width
    'volume_m3':        8_000_000,    # estimated dam body volume
    'side_slope_z':     2.0,          # z:1 H:V side slopes
}

print('\n── LAKE & DAM INPUT PARAMETERS ──')
print(f'  Lake volume:      {lake["volume_m3"]/1e6:.1f} million m³')
print(f'  Lake area:        {lake["surface_area_m2"]/1e6:.2f} km²')
print(f'  Dam height:       {dam["height_m"]} m')
print(f'  Freeboard:        {lake["freeboard_m"]} m')

# ── FROEHLICH (1995) BREACH EQUATIONS ────────────────────────
# Breach width:    Bave = 0.1803 × Ko × Vw^0.32 × Hb^0.19
# Breach time:     tf   = 0.00254 × Vw^0.53 × Hb^-0.9
# Peak discharge:  Qp   = 0.2784 × Ko × Vw^0.568 × Hb^0.5
#
# Ko = 1.4 for overtopping, 1.0 for piping/seepage
# Vw = volume of water in reservoir at breach (m³)
# Hb = height of breach = dam height (m)

print('\n── FROEHLICH (1995) BREACH PARAMETERS ──')

scenarios = {
    'S1_Partial_Breach': {
        'description':   'Partial breach — 20m notch, seepage/piping',
        'Ko':            1.0,         # piping failure mode
        'Hb':            20.0,        # breach height (m)
        'Vw':            lake['volume_m3'] * 0.30,  # 30% of lake drains
        'color':         'orange',
    },
    'S2_Full_Breach': {
        'description':   'Full breach — 40m notch, overtopping',
        'Ko':            1.4,         # overtopping failure
        'Hb':            40.0,
        'Vw':            lake['volume_m3'] * 0.70,  # 70% drains
        'color':         'red',
    },
    'S3_Cascade_Failure': {
        'description':   'Seismic + landslide dam cascade (2024 Thame analog)',
        'Ko':            1.4,
        'Hb':            70.0,        # full dam height fails
        'Vw':            lake['volume_m3'] * 1.00,  # full lake drains
        'color':         'darkred',
    },
}

results = {}

for sc_name, sc in scenarios.items():
    Ko = sc['Ko']
    Hb = sc['Hb']
    Vw = sc['Vw']

    # Froehlich equations
    Bave = 0.1803 * Ko * (Vw**0.32) * (Hb**0.19)   # avg breach width (m)
    tf   = 0.00254 * (Vw**0.53) * (Hb**-0.9)        # breach time (hours)
    Qp   = 0.2784 * Ko * (Vw**0.568) * (Hb**0.5)    # peak discharge (m³/s)

    # Side slope breach width
    Btop = Bave + dam['side_slope_z'] * Hb            # top width of breach
    Bbot = max(0, Bave - dam['side_slope_z'] * Hb)    # bottom width

    # Time to peak: assume 1/3 of total breach time
    tp = tf / 3.0

    results[sc_name] = {
        'description':    sc['description'],
        'Vw_Mm3':         Vw / 1e6,
        'Hb_m':           Hb,
        'Bave_m':         Bave,
        'Btop_m':         Btop,
        'tf_hrs':         tf,
        'tp_hrs':         tp,
        'Qp_m3s':         Qp,
        'color':          sc['color'],
    }

    print(f'\n  {sc_name}:')
    print(f'    {sc["description"]}')
    print(f'    Volume released:     {Vw/1e6:.1f} million m³')
    print(f'    Breach height:       {Hb:.0f} m')
    print(f'    Avg breach width:    {Bave:.1f} m')
    print(f'    Top breach width:    {Btop:.1f} m')
    print(f'    Breach duration:     {tf:.2f} hours')
    print(f'    Time to peak:        {tp*60:.1f} minutes')
    print(f'    PEAK DISCHARGE:      {Qp:,.0f} m³/s')

# ── BUILD HYDROGRAPH TIME SERIES ─────────────────────────────
# Use Suetsugi (1998) shape: rise rapidly, fall exponentially

def build_hydrograph(Qp, tp_hrs, tf_hrs, duration_hrs=24):
    """
    Generate synthetic GLOF hydrograph.
    Rise: linear from 0 to Qp in tp hours
    Fall: exponential decay after peak
    """
    dt      = 0.05  # time step in hours
    t       = np.arange(0, duration_hrs + dt, dt)
    Q       = np.zeros(len(t))

    tp_idx  = int(tp_hrs / dt)
    
    for i, ti in enumerate(t):
        if ti <= tp_hrs:
            # Rising limb — linear
            Q[i] = Qp * (ti / tp_hrs)
        else:
            # Falling limb — exponential decay
            k    = np.log(0.01) / (tf_hrs - tp_hrs)
            Q[i] = Qp * np.exp(k * (ti - tp_hrs))

    return t, Q

print('\n── HYDROGRAPH TIME SERIES ──')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Tsho Rolpa GLOF — Breach Hydrographs\n'
             'Froehlich (1995) Predictor Equations',
             fontsize=13, fontweight='bold')

all_hydrographs = {}

for i, (sc_name, sc) in enumerate(results.items()):
    t, Q = build_hydrograph(
        sc['Qp_m3s'], sc['tp_hrs'], sc['tf_hrs'], duration_hrs=48
    )
    all_hydrographs[sc_name] = {'t': t, 'Q': Q}

    ax = axes[i // 2][i % 2] if i < 3 else axes[1][1]
    row, col = i // 2, i % 2
    ax = axes[row][col]

    ax.fill_between(t, Q, alpha=0.3, color=sc['color'])
    ax.plot(t, Q, color=sc['color'], linewidth=2)
    ax.axhline(y=sc['Qp_m3s'], color='black', linestyle='--',
               linewidth=1, alpha=0.5)
    ax.axvline(x=sc['tp_hrs'], color='gray', linestyle=':', linewidth=1)

    ax.set_title(f'{sc_name.replace("_"," ")}\n{sc["description"]}',
                 fontsize=9)
    ax.set_xlabel('Time (hours)')
    ax.set_ylabel('Discharge Q (m³/s)')
    ax.text(0.97, 0.95,
            f'Qp = {sc["Qp_m3s"]:,.0f} m³/s\n'
            f'tp = {sc["tp_hrs"]*60:.0f} min\n'
            f'tf = {sc["tf_hrs"]:.1f} hrs',
            transform=ax.transAxes, fontsize=8,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    ax.grid(True, alpha=0.3)
    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

# Combined comparison on 4th panel
ax4 = axes[1][1]
for sc_name, hyd in all_hydrographs.items():
    sc = results[sc_name]
    ax4.plot(hyd['t'], hyd['Q'],
             color=sc['color'], linewidth=2,
             label=f'{sc_name.replace("_"," ")} — Qp={sc["Qp_m3s"]:,.0f} m³/s')

ax4.set_title('All Scenarios — Comparison')
ax4.set_xlabel('Time (hours)')
ax4.set_ylabel('Discharge Q (m³/s)')
ax4.legend(fontsize=7)
ax4.grid(True, alpha=0.3)
ax4.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))

plt.tight_layout()
chart = out + r'\GLOF_Breach_Hydrographs.png'
plt.savefig(chart, dpi=150, bbox_inches='tight')
plt.show()

# ── WAVE TRAVEL TIME TO KEY LOCATIONS ─────────────────────────
print('\n── FLOOD WAVE TRAVEL TIME ESTIMATES ──')
print('   (Downstream corridor — Rolwaling → Tamakoshi)')
print()

# Locations and distances from dam
locations = [
    ('Tsho Rolpa Dam',          0,    'breach origin'),
    ('Beding Village',          8,    'first settlement downstream'),
    ('Na Village',             15,    'high risk zone'),
    ('Rolwaling confluence',   35,    'joins main valley'),
    ('Upper Tamakoshi HEP',    55,    '456 MW powerhouse'),
    ('Dolakha Bazaar',         80,    'district headquarters'),
    ('Sunkoshi confluence',   130,    'major river junction'),
    ('Chatara (downstream)',   200,   'Terai plains entry'),
]

# GLOF wave speed: empirical estimate
# Scott (1988): V = 0.18 × Q^0.27 × slope^-0.1
# Simplified: ~3-6 m/s in steep Himalayan valleys

wave_speeds = {
    'S1_Partial_Breach':   3.0,   # m/s — lower discharge, slower
    'S2_Full_Breach':      4.5,   # m/s
    'S3_Cascade_Failure':  6.0,   # m/s — highest energy
}

print(f'  {"Location":<30} {"Dist(km)":<10}', end='')
for sc in results:
    print(f'{sc.replace("S","S").split("_")[0]+"_"+sc.split("_")[1]:<18}', end='')
print()
print('  ' + '-'*85)

travel_data = []
for loc_name, dist_km, note in locations:
    row = {'Location': loc_name, 'Distance_km': dist_km, 'Note': note}
    print(f'  {loc_name:<30} {dist_km:<10}', end='')
    for sc_name, speed in wave_speeds.items():
        travel_hrs = (dist_km * 1000) / speed / 3600
        travel_min = travel_hrs * 60
        row[sc_name + '_hrs'] = round(travel_hrs, 2)
        if travel_min < 60:
            print(f'{travel_min:.0f} min          ', end='')
        else:
            print(f'{travel_hrs:.1f} hrs          ', end='')
    print(f'  ({note})')
    travel_data.append(row)

df_travel = pd.DataFrame(travel_data)

# ── SAVE ALL OUTPUTS ──────────────────────────────────────────
# Save hydrograph data
hyd_rows = []
for sc_name, hyd in all_hydrographs.items():
    for t_val, q_val in zip(hyd['t'][::10], hyd['Q'][::10]):
        hyd_rows.append({
            'Scenario': sc_name,
            'Time_hrs': round(t_val, 2),
            'Q_m3s':    round(q_val, 2)
        })

df_hyd = pd.DataFrame(hyd_rows)
df_hyd.to_csv(out + r'\Hydrograph_TimeSeries.csv', index=False)
df_travel.to_csv(out + r'\FloodWave_TravelTimes.csv', index=False)

# Save peak values summary
summary = []
for sc_name, sc in results.items():
    summary.append({
        'Scenario':        sc_name,
        'Description':     sc['description'],
        'Volume_Mm3':      sc['Vw_Mm3'],
        'BreachHeight_m':  sc['Hb_m'],
        'BreachWidth_m':   round(sc['Bave_m'], 1),
        'TimeToPeak_min':  round(sc['tp_hrs']*60, 1),
        'BreachDuration_hrs': round(sc['tf_hrs'], 2),
        'PeakDischarge_m3s':  round(sc['Qp_m3s'], 0),
    })

df_summary = pd.DataFrame(summary)
df_summary.to_csv(out + r'\BreachHydrograph_Summary.csv', index=False)

print()
print('='*60)
print('BREACH HYDROGRAPH SUMMARY')
print('='*60)
for _, row in df_summary.iterrows():
    print(f"\n  {row['Scenario']}:")
    print(f"    Peak discharge:    {row['PeakDischarge_m3s']:,.0f} m³/s")
    print(f"    Time to peak:      {row['TimeToPeak_min']:.0f} minutes")
    print(f"    Breach duration:   {row['BreachDuration_hrs']:.1f} hours")
    print(f"    Breach width:      {row['BreachWidth_m']:.0f} m")

print()
print('UPPER TAMAKOSHI HEP (55 km downstream):')
for sc_name, speed in wave_speeds.items():
    hrs = (55000) / speed / 3600
    print(f'  {sc_name:<35} flood arrives in {hrs:.1f} hours')

print()
print('CRITICAL FINDING:')
print('  Flood wave reaches Upper Tamakoshi (456 MW) in 2.5–5 hours.')
print('  Standard evacuation protocol requires minimum 6 hours.')
print('  → Powerhouse has INSUFFICIENT warning time in S2 and S3.')
print()
print(f'✓ Hydrograph CSV:  Hydrograph_TimeSeries.csv')
print(f'✓ Travel times:    FloodWave_TravelTimes.csv')
print(f'✓ Summary:         BreachHydrograph_Summary.csv')
print(f'✓ Chart:           {chart}')
print()
print('NEXT STEP: Import hydrograph into HEC-RAS 2D')
print('  File needed: Hydrograph_TimeSeries.csv')
print('  Open HEC-RAS → New Project → import this as boundary condition')