from gurobipy import Model, GRB, quicksum
from dataparser import parse_afjsp
import csv
import os

data, mivj,machines_oj, p, alternatives, units, H = parse_afjsp("data/AFJSP Test Instances/Test 3/test3.txt") 

jobs = [i for i in range(1, data["num_jobs"] + 1)]
machines = [i for i in range(0, data["num_machines"])] 

operations = {}
for job_id in jobs:
    operations[job_id] = {}
    for alt in alternatives[job_id]:
        operations[job_id][alt]= [i for i in data['jobs'][f'job_{job_id}'][f"alternative_{alt}"].keys()]


model = Model()

cmax = model.addVar(lb=0,vtype=GRB.CONTINUOUS, name=f'cmax')

x = {}
for i in jobs:
    for v in alternatives[i]:
        x[i, v] = model.addVar(vtype=GRB.BINARY, name=f'x_{i}_{v}')

a = {}
for i in jobs:
    for u in units[i]: 
            for k in machines_oj[i][u]:
                a[i,u,k] = model.addVar(vtype=GRB.BINARY, name=f'a_{i}_{v}_{j}_{k}')

B = {}
for i in jobs:
    for j in units[i]:
            for iz in jobs:
                if iz != i:
                    for jz in units[iz]:
                            B[i, j, iz, jz] = model.addVar(vtype=GRB.BINARY, name=f'B_{i}_{j}_{iz}_{jz}')

s = {}
for i in jobs:
    for j in units[i]:
            s[i, j] = model.addVar(lb=0,vtype=GRB.CONTINUOUS, name=f's_{i}_{j}')

c = {}
for i in jobs:
    for j in units[i]:
            s[i, j] = model.addVar(lb=0,vtype=GRB.CONTINUOUS, name=f'c_{i}_{j}')

ci = {}
for i in jobs:
            s[i, j] = model.addVar(lb=0,vtype=GRB.CONTINUOUS, name=f'ci_{i}_{j}')

model.setObjective(cmax, GRB.MINIMIZE)

model.addConstrs((quicksum(a[i,v, j, k] for k in mivj[i][v][j]) == x[i, v] for i in jobs for v in alternatives[i] for j in operations[i][v] ), name="NB2")

model.addConstrs((t[i,v,j] >= t[i,v,j-1] + quicksum(p[i][v][j-1][k]* a[i,v,j-1,k] for k in mivj[i][v][j-1]) for i in jobs for v in alternatives[i] for j in operations[i][v][1:]), name="NB3")

for i in jobs:
    for ip in jobs:
        if i < ip:
            for v in alternatives[i]:
                for vp in alternatives[ip]:
                    for j in operations[i][v]:
                        for jp in operations[ip][vp]:
                            kkp = [k for k in mivj[i][v][j] if k in mivj[ip][vp][jp]]
                            if len(kkp):
                                for iipk in kkp:
                                    model.addConstr(t[ip,vp, jp] >= t[i,v, j] + p[i][v][j][iipk] - H * (
                                                3 - B[i, v, j, ip, vp, jp] - a[i, v, j, iipk] - a[ip,vp, jp, iipk]),
                                                    name="NB4")
                                    model.addConstr(
                                        t[i,v,j] >= t[ip,vp, jp] +
                                        p[ip][vp][jp][iipk] - H *
                                        (2 + B[i, v, j, ip,vp, jp] - a[i,v, j, iipk] - a[ip,vp, jp, iipk]),
                                        name="NB5")

#model.addConstrs((cmax >= t[i,v,j] +quicksum(p[i][v][j][k]* a[i,v,j,k] for k in mivj[i][v][j]) for i in jobs for v in alternatives[i] for j in operations[i][v]), name="NB6")

#möglicher weiße effizienter
model.addConstrs((cmax >= t[i,v,operations[i][v][-1]] +quicksum(p[i][v][operations[i][v][-1]][k]* a[i,v,operations[i][v][-1],k] for k in mivj[i][v][operations[i][v][-1]]) for i in jobs for v in alternatives[i]) , name="NB6")

model.addConstrs((quicksum(x[i, v] for v in alternatives[i]) == 1 for i in jobs), name="NB7")

model.addConstrs((t[i,v,j]- H * x[i,v] <= 0 for i in jobs for v in alternatives[i] for j in operations[i][v]), name= "NB8")

model.write("AFJSP\model.lp")


model.optimize()

if model.status == GRB.OPTIMAL:
    # Öffnen einer CSV-Datei zum Schreiben
    with open('AFJSP\solution.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Schreiben der Kopfzeile mit zusätzlichen Informationen
        writer.writerow([])  # Leere Zeile zur Trennung
        writer.writerow(['Variable', 'Value'])
        
        # Schreiben der Werte der Entscheidungsvariablen, die nicht null sind
        for v in model.getVars():
            if v.varName.startswith('t_') or v.x != 0:  # Überprüfen, ob der Wert der Variable nicht null ist
                writer.writerow([v.varName, v.x])
        
        for i in jobs:
            for v in alternatives[i]:
                for j in operations[i][v]:
                    for k in mivj[i][v][j]:
                        writer.writerow([f"p_{i}_{v}_{j}_{k}", f"{p[i][v][j][k]}"])
        
        writer.writerow(["NUM_JOBS", f"{data['num_jobs']}"])
        writer.writerow(["NUM_ALTERNATIVES", f"{data['num_alternatives']}"])
        writer.writerow(["NUM_MACHINES", f"{data['num_machines']}"])  

    print("Lösung wurde erfolgreich in 'solution.csv' gespeichert.")
else:
    print("Es wurde keine optimale Lösung gefunden.")

model.write("Afjsp\solution.sol")










