ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

def fmt_int(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8g}' for v in chunk))
    return '\n'.join(lines)

# S2 Full Breach — 66,352 m3/s peak
inflow_s2 = [0, 6000, 12000, 18000, 24000, 30000, 36000, 42000, 48000, 54000,
             60000, 66352, 58000, 48000, 36000, 24000, 14000, 7000, 3000, 1000,
             400, 100, 20, 5, 0] + [0]*75

downstream = [1.0]*100
area = 'Rolwaling River '

def fmt_int(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8g}' for v in chunk))
    return '\n'.join(lines)

u01_s2 = f"""Flow Title=S2 Full Breach
Program Version=6.70
Use Restart= 0 
Boundary Location=                ,                ,        ,        ,                ,{area},                ,Downstream                      ,                                
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
Boundary Location=                ,                ,        ,        ,                ,{area},                ,Inflow                          ,                                
Interval=4MIN
Flow Hydrograph= 100 
{fmt_int(inflow_s2)}
Stage Hydrograph TW Check=0
DSS Path=
Use DSS=False
Use Fixed Start Time=False
Fixed Start Date/Time=01JAN2026,0000
Is Critical Boundary=False
Critical Boundary Flow=
EG Slope for Distributing Flow Along BC Line=0.001
"""

# Save as new flow file
s2_file = ras_dir + r'\tshorolpa_S2.u01'
with open(s2_file, 'w') as f:
    f.write(u01_s2)

print(f'✓ S2 flow file created: {s2_file}')
print('Peak: 66,352 m3/s')
print()
print('In HEC-RAS:')
print('1. File → Save Plan As → name it S2_Full_Breach')
print('2. Change Unsteady Flow File → browse to tshorolpa_S2.u01')
print('3. Compute')