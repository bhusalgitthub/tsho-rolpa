import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

out = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\01_PROCESSED\04_Seismic_Layers'
os.makedirs(out, exist_ok=True)

print('='*60)
print('NEWMARK SLIDING BLOCK ANALYSIS')
print('Tsho Rolpa Moraine Dam — Seismic Stability Assessment')
print('='*60)

# ── STEP 1: MORAINE GEOTECHNICAL PROPERTIES ──────────────────
# Source: Richardson & Reynolds (2000), Kodama et al. (2008)
# Ice-cored moraine, poorly sorted glacial till

props = {
    'cohesion_kPa':         10.0,   # c — low, ice-cored moraine
    'friction_angle_deg':   30.0,   # φ — internal friction angle
    'unit_weight_kNm3':     18.0,   # γ — bulk unit weight of till
    'slope_angle_deg':      25.0,   # α — downstream face slope
    'slope_height_m':       70.0,   # H — dam height
    'saturation':           0.8,    # partial saturation (ice core)
    'pore_pressure_ratio':  0.2,    # ru — pore pressure ratio
}

c    = props['cohesion_kPa']
phi  = np.radians(props['friction_angle_deg'])
gamma= props['unit_weight_kNm3']
alpha= np.radians(props['slope_angle_deg'])
H    = props['slope_height_m']
ru   = props['pore_pressure_ratio']
g    = 9.81  # m/s²

print('\n── GEOTECHNICAL INPUT PARAMETERS ──')
for k, v in props.items():
    print(f'  {k:<28} {v}')

# ── STEP 2: STATIC FACTOR OF SAFETY ─────────────────────────
# Infinite slope model with pore pressure
# FS = (c + γH·cos²α·(1-ru)·tanφ) / (γH·sinα·cosα)

numerator   = c + gamma * H * (np.cos(alpha)**2) * (1 - ru) * np.tan(phi)
denominator = gamma * H * np.sin(alpha) * np.cos(alpha)
FS_static   = numerator / denominator

print(f'\n── STATIC STABILITY ──')
print(f'  Factor of Safety (static):  {FS_static:.3f}')
if FS_static > 1.5:
    print(f'  STATUS: STABLE under static conditions (FS > 1.5)')
elif FS_static > 1.0:
    print(f'  STATUS: MARGINALLY STABLE (1.0 < FS < 1.5) — vulnerable')
else:
    print(f'  STATUS: UNSTABLE even without earthquake')

# ── STEP 3: CRITICAL ACCELERATION ────────────────────────────
# ac = (FS - 1) × g × sin(α)
# This is the minimum ground acceleration to initiate sliding

ac = (FS_static - 1) * g * np.sin(alpha)
ac_g = ac / g  # express as fraction of g

print(f'\n── CRITICAL ACCELERATION ──')
print(f'  ac = {ac:.3f} m/s²')
print(f'  ac = {ac_g:.4f} g')
print(f'  Interpretation: Any earthquake producing PGA > {ac_g:.3f}g')
print(f'  at the dam site will initiate slope movement')

# ── STEP 4: NEWMARK DISPLACEMENT ─────────────────────────────
# Empirical equation: Jibson (2007)
# log(Dn) = 0.215 + log[(1 - ac/PGA)^2.341 × (ac/PGA)^-1.438]
# Valid when PGA > ac

# Test across range of PGA values
PGA_values = np.arange(0.05, 1.05, 0.05)  # 0.05g to 1.0g

results = []
for pga in PGA_values:
    if pga > ac_g:
        ratio = ac_g / pga
        log_Dn = (0.215 +
                  np.log10((1 - ratio)**2.341 * ratio**-1.438))
        Dn_cm = 10**log_Dn
    else:
        Dn_cm = 0.0  # no movement below critical acceleration

    # Failure threshold: >100cm displacement = dam breach
    status = ('NO MOVEMENT'  if Dn_cm == 0 else
              'MINOR'        if Dn_cm < 5  else
              'MODERATE'     if Dn_cm < 30 else
              'SEVERE'       if Dn_cm < 100 else
              '⚠ BREACH LIKELY')

    results.append({
        'PGA_g':       round(pga, 2),
        'Dn_cm':       round(Dn_cm, 2),
        'Status':      status
    })

df_newmark = pd.DataFrame(results)

print(f'\n── NEWMARK DISPLACEMENT vs PGA ──')
print(f'  Critical acceleration: {ac_g:.4f} g')
print()
print(f'  {"PGA (g)":<10} {"Displacement (cm)":<22} {"Status"}')
print(f'  {"-"*50}')
for _, row in df_newmark.iterrows():
    marker = ' ←' if row['Status'] == '⚠ BREACH LIKELY' else ''
    print(f'  {row["PGA_g"]:<10} {row["Dn_cm"]:<22} {row["Status"]}{marker}')

# ── STEP 5: SEISMIC HAZARD COMPARISON ────────────────────────
# Regional PGA values for Tsho Rolpa site
# Source: GEM OpenQuake / USGS PSHA for Nepal Himalaya

seismic_hazard = {
    '10% in 50 years (475yr return)':  0.40,  # g
    '5% in 50 years (975yr return)':   0.55,  # g
    '2% in 50 years (2475yr return)':  0.75,  # g
}

print(f'\n── SEISMIC HAZARD AT TSHO ROLPA ──')
print(f'  (GEM OpenQuake — Nepal Himalaya region)')
print()

for label, pga in seismic_hazard.items():
    if pga > ac_g:
        ratio = ac_g / pga
        log_Dn = (0.215 +
                  np.log10((1 - ratio)**2.341 * ratio**-1.438))
        Dn = round(10**log_Dn, 1)
        breach = '⚠ BREACH LIKELY' if Dn > 100 else f'{Dn} cm displacement'
    else:
        Dn = 0
        breach = 'No movement'

    exceeds = 'EXCEEDS ac' if pga > ac_g else 'below ac'
    print(f'  {label}')
    print(f'    PGA = {pga}g  [{exceeds}]  →  {breach}')
    print()

# ── STEP 6: PLOT ─────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle('Newmark Sliding Block Analysis — Tsho Rolpa Moraine Dam',
             fontsize=13, fontweight='bold')

# Plot 1: Displacement vs PGA
pga_vals = df_newmark['PGA_g'].values
dn_vals  = df_newmark['Dn_cm'].values

ax1.plot(pga_vals, dn_vals, 'b-o', markersize=4, linewidth=2)
ax1.axvline(x=ac_g, color='orange', linestyle='--',
            linewidth=2, label=f'Critical acceleration ac = {ac_g:.3f}g')
ax1.axhline(y=100, color='red', linestyle='--',
            linewidth=2, label='Breach threshold (100 cm)')

for label, pga in seismic_hazard.items():
    ax1.axvline(x=pga, color='purple', linestyle=':',
                linewidth=1.2, alpha=0.7)
    ax1.text(pga+0.01, ax1.get_ylim()[1]*0.5,
             label[:6], fontsize=7, color='purple', rotation=90)

ax1.set_xlabel('Peak Ground Acceleration (g)')
ax1.set_ylabel('Newmark Displacement (cm)')
ax1.set_title('Coseismic Displacement vs PGA')
ax1.legend(fontsize=9)
ax1.set_yscale('log')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=0.01)

# Plot 2: Factor of Safety vs slope angle
angles = np.linspace(10, 45, 100)
fs_vals = []
ac_vals = []
for a_deg in angles:
    a = np.radians(a_deg)
    num = c + gamma * H * (np.cos(a)**2) * (1-ru) * np.tan(phi)
    den = gamma * H * np.sin(a) * np.cos(a)
    fs  = num / den
    ac_val = max(0, (fs - 1) * g * np.sin(a) / g)
    fs_vals.append(fs)
    ac_vals.append(ac_val)

ax2.plot(angles, fs_vals, 'g-', linewidth=2, label='Factor of Safety')
ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=1.5,
            label='FS = 1.0 (failure)')
ax2.axhline(y=1.5, color='orange', linestyle='--', linewidth=1.5,
            label='FS = 1.5 (minimum safe)')
ax2.axvline(x=props['slope_angle_deg'], color='blue', linestyle=':',
            linewidth=2, label=f'Current slope = {props["slope_angle_deg"]}°')
ax2.set_xlabel('Downstream Slope Angle (degrees)')
ax2.set_ylabel('Factor of Safety')
ax2.set_title('Static Stability vs Slope Angle')
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
chart = out + r'\Newmark_Analysis.png'
plt.savefig(chart, dpi=150, bbox_inches='tight')
plt.show()

# ── STEP 7: SAVE RESULTS ─────────────────────────────────────
df_newmark.to_csv(out + r'\Newmark_Displacement_Table.csv', index=False)

print('='*60)
print('SUMMARY')
print('='*60)
print(f'  Static FS:              {FS_static:.3f}  (marginally stable)')
print(f'  Critical acceleration:  {ac_g:.4f} g')
print(f'  475yr return PGA:       0.40g  → exceeds ac by {0.40-ac_g:.3f}g')
print(f'  975yr return PGA:       0.55g  → exceeds ac by {0.55-ac_g:.3f}g')
print(f'  2475yr return PGA:      0.75g  → exceeds ac by {0.75-ac_g:.3f}g')
print()
print('  CONCLUSION: A 475-year return earthquake (10% in 50yr)')
print('  is sufficient to initiate moraine slope failure.')
print('  A 2475-year event produces displacement well above')
print('  the 100cm breach threshold.')
print()
print(f'✓ Chart saved: {chart}')
print(f'✓ Table saved: Newmark_Displacement_Table.csv')