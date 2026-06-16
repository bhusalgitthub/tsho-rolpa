import os

ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

# Fix plan file date format
p01_path = os.path.join(ras_dir, 'tshorolpa.p01')
with open(p01_path, 'r') as f:
    content = f.read()

content = content.replace(
    'Simulation Date=01JAN2026,0000,03JAN2026,0000',
    'Simulation Date=01Jan2026,0000,03Jan2026,0000'
)
with open(p01_path, 'w') as f:
    f.write(content)
print('✓ Plan file date fixed')

# Rewrite flow file with Use Simulation Time (no fixed date needed)
flows = [0, 7084.2, 14168.5, 18920.2, 5798.7, 1777.2,
         544.7, 166.9, 51.2, 15.7, 4.8, 1.5, 0.5, 0.1, 0.0]

def fmt(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8.2f}' for v in chunk))
    return '\n'.join(lines)

u01 = f"""Flow Title=S1 Partial Breach
Program Version=6.70
Use Simulation Time=0

Boundary Location=Rolwaling River,,,,BCLine: Inflow,,,,,
Interval=10MIN
Flow Hydrograph= {len(flows)}
{fmt(flows)}

Boundary Location=Rolwaling River,,,,BCLine: Downstream,,,,,
Interval=1HOUR
Flow Hydrograph= 49
{fmt([1.0]*49)}
"""

u01_path = os.path.join(ras_dir, 'tshorolpa.u01')
with open(u01_path, 'w') as f:
    f.write(u01)
print('✓ Flow file rewritten')
print()
print('Now in HEC-RAS:')
print('  File → Open Project → tshorolpa.prj')
print('  Run → Unsteady Flow Analysis → Compute')