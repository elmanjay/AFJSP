import random
import os

num_jobs = 5
num_machines = 5
alt_flex = 2
rout_flex = 2

instance = {}

for i in range(1, num_jobs + 1):
    instance[i] = {}
    for v in range(1, alt_flex+1):
        instance[i][v] = {}
        for j in range(1, num_machines + 1):  # Ganzzahldivision verwendet
            instance[i][v][j] = {}
            for z in range(rout_flex):
                instance[i][v][j][random.randint(1, num_machines)] = random.randint(1,99)

print(instance)
print(len(instance[1]))

with open("instance.txt", "w") as file:
    # Schreiben der ersten Zeile mit num_jobs und num_machines und Anzahl der Alternativen
    first_line = f"{num_jobs} {num_machines} " + " ".join(str(len(instance[i])) for i in range(1, num_jobs + 1))
    file.write(first_line + "\n")

    for i in range(1, num_jobs + 1):
        for v in range(1, len(instance[i]) + 1):
            alternative_line = [str(len(instance[i]))]  # Anzahl der Operationen für die Alternative
            for j in instance[i][v]:
                num_machines_for_operation = len(instance[i][v])
                alternative_line.append(f"{num_machines_for_operation} {j} {instance[i][v][j]}")
            alternative_line_str = " ".join(alternative_line)
            file.write(alternative_line_str + "\n")

