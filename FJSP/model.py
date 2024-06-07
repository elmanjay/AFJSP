from gurobipy import Model, GRB, quicksum
from dataparser import parse_fjsp
import csv

data, mij, p, H = parse_fjsp("data/fjsp-instances-main 2/behnke/sm01_1.txt")

jobs = [i for i in range(1, data["num_jobs"] + 1)]
machines = [i for i in range(0, data["num_machines"])] 
operations = []
for job_id in jobs:
    job_operations = data['jobs'][f'job_{job_id}']
    operations.append( [i for i in range(1,len(job_operations)+1)])

print(p[f"job_{1}"])

model = Model()

cmax = model.addVar(lb=0,vtype=GRB.CONTINUOUS, name=f'cmax')

t = {}
for i in jobs:
    for j in operations[i-1]:
        t[i, j] = model.addVar(lb=0,vtype=GRB.CONTINUOUS, name=f't_{i}_{j}')

a = {}
for i in jobs:
    for j in operations[i-1]:
        for k in mij[f"job_{i}"][j]:
            a[i,j,k] = model.addVar(vtype=GRB.BINARY, name=f'a_{i}_{j}_{k}')

B = {}
for i in jobs:
    for j in operations[i-1]:
        for iz in jobs:
            for jz in operations[iz-1]:
                B[i, j, iz, jz] = model.addVar(vtype=GRB.BINARY, name=f'B_{i}_{j}_{iz}_{jz}')

model.setObjective(cmax, GRB.MINIMIZE)

model.addConstrs((quicksum(a[i, j, k] for k in mij[f"job_{i}"][j]) == 1 for i in jobs for j in operations[i-1] ), name="NB2")

model.addConstrs((t[i,j] >= t[i,j-1] + quicksum(p[f"job_{i}"][j-1][k]* a[i,j-1,k] for k in mij[f"job_{i}"][j-1]) for i in jobs for j in operations[i-1][1:]), name="NB3")

for i in jobs:
    for ip in jobs:
        if i < ip:
            for j in operations[i-1]:
                for jp in operations[ip-1]:
                    kkp = [k for k in mij[f"job_{i}"][j] if k in mij[f"job_{ip}"][jp]]
                    if len(kkp):
                        for iipk in kkp:
                            model.addConstr(t[ip, jp] >= t[i, j] + p[f"job_{i}"][j][iipk] - H * (
                                        3 - B[i, j, ip, jp] - a[i, j, iipk] - a[ip, jp, iipk]),
                                            name="NB4")
                            model.addConstr(
                                t[i, j] >= t[ip, jp] +
                                p[f"job_{ip}"][jp][iipk] - H *
                                (2 + B[i, j, ip, jp] - a[i, j, iipk] - a[ip, jp, iipk]),
                                name="NB5")

model.addConstrs((cmax >= t[i,j] +quicksum(p[f"job_{i}"][j][k]* a[i,j,k] for k in mij[f"job_{i}"][j]) for i in jobs for j in operations[i-1]), name="NB6")

#möglicher weiße effizienter
#model.addConstrs((cmax >= t[i,operations[i-1][-1]] +quicksum(p[f"job_{i}"][operations[i-1][-1]][k]* a[i,operations[i-1][-1],k] for k in mij[f"job_{i}"][operations[i-1][-1]]) for i in jobs), name="NB6")
model.write("model.lp")
model.optimize()

if model.status == GRB.OPTIMAL:
    # Öffnen einer CSV-Datei zum Schreiben
    with open('solution.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Schreiben der Kopfzeile mit zusätzlichen Informationen
        writer.writerow([])  # Leere Zeile zur Trennung
        writer.writerow(['Variable', 'Value'])
        
        # Schreiben der Werte der Entscheidungsvariablen, die nicht null sind
        for v in model.getVars():
            if v.varName.startswith('t_') or v.x != 0:  # Überprüfen, ob der Wert der Variable nicht null ist
                writer.writerow([v.varName, v.x])
        
        for i in jobs:
            for j in operations[i-1]:
                for k in mij[f"job_{i}"][j]:
                    writer.writerow([f"p_{i}_{j}_{k}", f"{p[f'job_{i}'][j][k]}"])
        
        writer.writerow(["Anzahl Jobs:", f"{data['num_jobs']}"])
        writer.writerow(["Anzahl Maschinen:", f"{data['num_machines']}"])  

    print("Lösung wurde erfolgreich in 'solution.csv' gespeichert.")
else:
    print("Es wurde keine optimale Lösung gefunden.")

model.write("solution.sol")
# model.write('iismodel.ilp')









