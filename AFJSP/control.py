from instance_gen import gen_instance
from dataparser import parse_afjsp
from model import create_model
import os
from gurobipy import Model, GRB, quicksum
import pandas as pd

num_jobs = [5]
num_machines = [5]
#Fixe Anzahl der Alternativen pro Job
alt_flex = [2]
#Intervallobergrenze möglicher Maschinen pro Operation
rout_flex = [2]
alternatives = 1

#generieren der Instanzen
for job in num_jobs:
    for machine in num_machines:
        for alt in alt_flex:
            for route in rout_flex:
                for a in range(alternatives):
                    path = os.path.join("data", "Analyse", f"{job}_{machine}_{alt}_{route}_A{a}.txt")
                    gen_instance(path,job,machine,alt,route)

path = os.path.join("data", "Analyse")
results_df = pd.DataFrame(columns=[
    "name", "num_jobs", "alt_flex", "rout_flex", "avg_op_j",
    "avg_ma_op", "avg_ptime", "time", "obj", "opt"
])
for datei_name in os.listdir(path):
    datei_pfad = os.path.join(path, datei_name)
    model, jobs, alternatives, operations, mivj, p, data = create_model(datei_pfad)
    model.setParam(GRB.Param.TimeLimit, 3600)
    model.optimize()

    if model.Status == GRB.OPTIMAL or model.Status == GRB.TIME_LIMIT:
            runtime = model.Runtime
            obj_val = model.ObjVal if model.SolCount > 0 else None
    
    if model.Status == GRB.OPTIMAL:
        optimal = 1
    else:
        optimal = 0



    machines_opeartion = []
    # Durch das äußere Dictionary iterieren
    for outer_key in mivj:
        # Durch das zweite Dictionary iterieren
        for middle_key in mivj[outer_key]:
            # Durch das innere Dictionary iterieren
            for inner_key in mivj[outer_key][middle_key]:
                # Länge der inneren Liste berechnen und zur Liste hinzufügen
                inner_list_length = len(mivj[outer_key][middle_key][inner_key])
                machines_opeartion.append(inner_list_length)
    # Durchschnitt der Längen berechnen
    average_machines_per_op = sum(machines_opeartion) / len(machines_opeartion) if machines_opeartion else 0

    job_operations = []

    # Durch das äußere Dictionary iterieren
    for outer_key in operations:
        # Durch das innere Dictionary iterieren
        for inner_key in operations[outer_key]:
            # Länge der inneren Liste berechnen und zur Liste hinzufügen
            inner_list_length = len(operations[outer_key][inner_key])
            job_operations.append(inner_list_length)

    average_operations_per_job = sum(job_operations ) / len(job_operations ) if job_operations  else 0


    row = {
        "name": datei_name,
        "num_jobs": max(jobs),
        "alt_flex": len(alternatives[1]),
        "rout_flex": 1,
        "avg_op_j": average_operations_per_job,
        "avg_ma_op": average_machines_per_op,
        "avg_ptime": 1,  # Stelle sicher, dass average_process_time definiert ist
        "time": runtime,
        "obj": obj_val,
        "opt": optimal
    }
    results_df = results_df._append(row, ignore_index=True)

print(results_df)
