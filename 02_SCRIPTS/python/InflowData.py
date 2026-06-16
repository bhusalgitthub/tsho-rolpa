ras_dir = r'C:\Users\bhusa\Desktop\TSHO-ROLPA-GLOF\03_MODELS\HEC_RAS'

# Inflow: flood hydrograph padded to 6 hours (360 min) at 1MIN interval
# Downstream: constant 1 m3/s for 6 hours at 1MIN interval

inflow = [0,0,0,472.8,945.6,1418.5,1891.3,2364.1,2836.9,3309.7,
          3782.6,4255.4,4728.2,5201.0,5673.8,6146.7,6619.5,7084.2,
          7557.0,8029.8,8502.6,8975.5,9448.3,9921.1,10393.9,10866.7,
          11339.6,11812.4,12285.2,13230.8,14168.5,15553.5,16938.4,
          18323.4,18920.2,17535.3,12000.0,7000.0,3500.0,1777.2,
          900.0,544.7,300.0,166.9,100.0,51.2,30.0,15.7,8.0,4.8,
          2.5,1.5,0.8,0.5,0.2,0.1,0.05,0.0,0.0,0.0] + [0.0]*300

# Pad to exactly 361 points (0 to 360 min)
inflow = inflow[:361]
downstream = [1.0] * 361

def fmt(vals):
    lines = []
    for i in range(0, len(vals), 10):
        chunk = vals[i:i+10]
        lines.append(''.join(f'{v:8.2f}' for v in chunk))
    return '\n'.join(lines)

u01 = f"""Flow Title=S1 Partial Breach
Program Version=6.70
Use Simulation Time= 1 

Boundary Location=Rolwaling River,,,,BCLine: Inflow,,,,,
Interval=1MIN
Flow Hydrograph= {len(inflow)}
{fmt(inflow)}

Boundary Location=Rolwaling River,,,,BCLine: Downstream,,,,,
Interval=1MIN
Flow Hydrograph= {len(downstream)}
{fmt(downstream)}
"""

with open(ras_dir + r'\tshorolpa.u01', 'w') as f:
    f.write(u01)
print('Done')