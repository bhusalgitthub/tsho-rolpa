import shutil, os

ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

def fmt_int(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8g}' for v in chunk))
    return '\n'.join(lines)

# S3 Cascade Failure — 107,487 m3/s peak
inflow_s3 = [0, 10000, 20000, 30000, 40000, 50000, 60000, 70000, 80000, 90000,
             100000, 107487, 95000, 80000, 65000, 50000, 35000, 20000, 10000, 5000,
             2000, 500, 100, 10, 0] + [0]*75

downstream = [1.0]*100
area = 'Rolwaling River '

u01_s3 = f"""Flow Title=S3 Cascade Failure
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
{fmt_int(inflow_s3)}
Stage Hydrograph TW Check=0
DSS Path=
Use DSS=False
Use Fixed Start Time=False
Fixed Start Date/Time=01JAN2026,0000
Is Critical Boundary=False
Critical Boundary Flow=
EG Slope for Distributing Flow Along BC Line=0.001
"""

# Save as u03
with open(ras_dir + r'\tshorolpa.u03', 'w') as f:
    f.write(u01_s3)

# Register in project file
prj_path = ras_dir + r'\tshorolpa.prj'
with open(prj_path, 'r') as f:
    content = f.read()

if 'Unsteady File=u03' not in content:
    content = content.replace(
        'Unsteady File=u02',
        'Unsteady File=u02\nUnsteady File=u03'
    )
    with open(prj_path, 'w') as f:
        f.write(content)

print('✓ S3 created: tshorolpa.u03')
print('  Peak: 107,487 m3/s')
print('  Seismic + landslide cascade scenario')
print()
print('Close and reopen HEC-RAS')
print('Run → Unsteady Flow Analysis → File → Save Plan As → S3_Cascade')
print('Select S3 Cascade Failure from dropdown → Compute')