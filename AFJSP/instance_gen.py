import random
import os

#Instanzgenerator nach Vorbild C. Özgüven (2010)
def gen_instance(path,num_jobs,num_machines,alt_flex,rout_flex):
    instance = {}

    for i in range(1, num_jobs + 1):
        instance[i] = {}
        for v in range(1, alt_flex + 1):
            instance[i][v] = {}
            for j in range(random.randint(int(num_machines/2), num_machines + 1)):
                instance[i][v][j] = {}
                for z in range(rout_flex):
                    random_machine = random.randint(1, num_machines)
                    instance[i][v][j][random_machine] = None
                keys = list(instance[i][v][j].keys())
                instance[i][v][j][keys[0]] = random.randint(1, 99)
                for m in keys[1:]:
                    instance[i][v][j][m] = random.randint(instance[i][v][j][keys[0]], 3 * instance[i][v][j][keys[0]])

    with open(path, "w") as file:
        # Schreiben der ersten Zeile mit num_jobs und num_machines und Anzahl der Alternativen
        first_line = f"{num_jobs} {num_machines} " + " ".join(str(len(instance[i])) for i in range(1, num_jobs + 1))
        file.write(first_line + "\n")

        for i in range(1, num_jobs + 1):
            for v in range(1, len(instance[i]) + 1):
                alternative_line = [str(len(instance[i][v]))]  # Anzahl der Operationen für die Alternative
                for j in instance[i][v]:
                    num_machines_for_operation = len(instance[i][v][j])
                    alternative_line.append(f"{num_machines_for_operation}")
                    for m in instance[i][v][j].keys():
                        alternative_line.append(f"{m} {instance[i][v][j][m]}")   
                alternative_line_str = " ".join(alternative_line)
                file.write(alternative_line_str + "\n")
    
if __name__ == "__main__":

    num_jobs = 10
    num_machines = 10
    #Fixe Anzahl der Alternativen pro Job
    alt_flex = 3
    #Intervallobergrenze möglicher Maschinen pro Operation
    rout_flex = 3


    path = os.path.join("AFJSP", "instance.txt")
    gen_instance(path,num_jobs,num_machines,alt_flex,rout_flex)
