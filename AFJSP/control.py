from instance_gen import gen_instance
from dataparser import parse_afjsp
from model import create_model
import os
from gurobipy import Model, GRB, quicksum

num_jobs = [5,10,20]
num_machines = [5,10]
alt_flex = [2,3]
rout_flex = [2,3]
alternatives = 4

#generieren der Instanzen
for job in num_jobs:
    for machine in num_machines:
        for alt in alt_flex:
            for route in rout_flex:
                for a in range(alternatives):
                    path = os.path.join("data", "Analyse", f"{job}_{machine}_{alt}_{route}_A{a}.txt")
                    gen_instance(path,job,machine,alt,route)

path = os.path.join("data", "Analyse")

for datei_name in os.listdir(path):
    datei_pfad = os.path.join(path, datei_name)
    model, jobs, alternatives, operations, mivj, p, data = create_model(path)
    model.setParam(GRB.Param.TimeLimit, 3600)
    model.optimize()
    

