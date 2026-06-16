ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

flows = [0, 7084.2, 14168.5, 18920.2, 5798.7, 1777.2,
         544.7, 166.9, 51.2, 15.7, 4.8, 1.5, 0.5, 0.1, 0.0]

def fmt(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8.2f}' for v in chunk))
    return '\n'.join(lines)

# Use Simulation Time=1 means no fixed date needed
# HEC-RAS uses the plan simulation window dates instead
u01 = f"""Flow Title=S1 Partial Breach
Program Version=6.70
Use Simulation Time= 1 

Boundary Location=Rolwaling River,,,,BCLine: Inflow,,,,,
Interval=10MIN
Flow Hydrograph= {len(flows)}
{fmt(flows)}

Boundary Location=Rolwaling River,,,,BCLine: Downstream,,,,,
Interval=1HOUR
Flow Hydrograph= 49
{fmt([1.0]*49)}
"""

with open(ras_dir + r'\tshorolpa.u01', 'w') as f:
    f.write(u01)
print('✓ Fixed — Use Simulation Time=1')
print('Now in HEC-RAS → Compute')