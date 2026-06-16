ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

def fmt_int(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8g}' for v in chunk))
    return '\n'.join(lines)

# Real S1 Partial Breach hydrograph — 20,419 m3/s peak
inflow = [0, 2000, 4000, 6000, 8000, 10000, 12000, 14000, 16000, 18000,
          20419, 18000, 14000, 10000, 6000, 3000, 1500, 700, 300, 100,
          50, 20, 5, 1, 0] + [0]*75

downstream = [1.0]*100

u01 = f"""Flow Title=S1 Partial Breach REAL
Program Version=6.70
Use Restart= 0 
Boundary Location=                ,                ,        ,        ,                ,Rolwaling River ,                ,Downstream                      ,                                
Interval=1HOUR
Flow Hydrograph= 100 
{fmt_int(downstream)}
Stage Hydrograph TW Check=0
DSS Path=
Use DSS=False
Use Fixed Start Time=False
Fixed Start Date/Time=01JAN2026,0000
Is Critical Boundary=False
Critical Boundary Flow=
EG Slope for Distributing Flow Along BC Line=0.001
Boundary Location=                ,                ,        ,        ,                ,Rolwaling River ,                ,Inflow                          ,                                
Interval=4MIN
Flow Hydrograph= 100 
{fmt_int(inflow)}
Stage Hydrograph TW Check=0
DSS Path=
Use DSS=False
Use Fixed Start Time=False
Fixed Start Date/Time=01JAN2026,0000
Is Critical Boundary=False
Critical Boundary Flow=
EG Slope for Distributing Flow Along BC Line=0.001
"""

with open(ras_dir + r'\tshorolpa.u01', 'w') as f:
    f.write(u01)

print('✓ Real S1 hydrograph loaded — peak 20,419 m3/s')
print('Now → Compute')