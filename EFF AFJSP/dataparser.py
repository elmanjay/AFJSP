import os

def parse_afjsp(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Parse number of jobs and machines
    first_line = lines[0].strip().split()
    num_jobs = int(first_line[0])
    num_machines = int(first_line[1])
    num_alternatives = [int(i) for i in first_line[2:]]
    print(num_alternatives)

    jobs = {}
    alternatives = {}
    machines = {}  # Maschinen-IDs
    processing_times = {}  # Verarbeitungszeiten

    count = 1
    for i in range(1, num_jobs + 1):
        # Initialisiere das Dictionary für den aktuellen Job
        jobs[f'job_{i}'] = {}
        
        for j in range(1, num_alternatives[i-1] + 1):
            # Füge ein alternatives Dictionary hinzu
            jobs[f'job_{i}'][f'alternative_{j}'] = {}
            line = lines[count].strip().split()
            print(line)
            print(count)
            count = count + 1
            num_operations = int(line[0])
            operations = {}
            index = 1
            
            for op_id in range(num_operations):
                num_options = int(line[index])
                index += 1
                options = []
                
                for _ in range(num_options):
                    machine_id = int(line[index])
                    processing_time = int(line[index + 1])
                    options.append({'machine_id': machine_id, 'processing_time': processing_time})
                    index += 2
                
                operations[op_id + 1] = options
            
            jobs[f'job_{i}'][f'alternative_{j}'] = operations

    fjsp_instance = {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        "num_alternatives": num_alternatives,
        'jobs': jobs
    }

    machine = {}
    machines_oj = {} 
    processing_times = {}
    for i in range(1, num_jobs + 1):
        machine[i] = {}
        machines_oj[i] = {}
        processing_times[i] = {}
        for j in range(1, num_alternatives[i-1] + 1):
            machine[i][j] = {}
            #machines_oj[i][j] = set()
            processing_times[i][j] = {}
            for z in jobs[f"job_{i}"][f"alternative_{j}"]:
                machines_oj[i][z] = set()
                machine[i][j][z] = [item['machine_id'] for item in jobs[f"job_{i}"][f"alternative_{j}"][z]]
                # Hier wird die generator expression in eine Liste umgewandelt und dann Elemente hinzugefügt
                for item in jobs[f"job_{i}"][f"alternative_{j}"][z]:
                    machines_oj[i][z].add(item['machine_id'])
                processing_times[i][j][z] = {}
                for k in machine[i][j][z]:
                    for key in jobs[f"job_{i}"][f"alternative_{j}"][z]:
                        for item in jobs[f"job_{i}"][f"alternative_{j}"][z]:
                            if item['machine_id'] == k:
                                processing_times[i][j][z][k] = item['processing_time']




    joblist = [i for i in range(1, fjsp_instance["num_jobs"] + 1)]

    OP = {}
    for job_id in joblist:
        OP[job_id] = {}
        for v in range(1, num_alternatives[job_id -1] + 1):
            job_operations = fjsp_instance['jobs'][f'job_{job_id}'][f"alternative_{v}"]
            OP[job_id][v]= [i for i in range(1,len(job_operations)+1)]

    largeH=0
    units = {}
    for job in joblist:
        umaxj = 0
        units[job] = {}
        for alternative in range(1, num_alternatives[job-1] + 1):
            if len(OP[job][alternative]) > umaxj:
                umaxj = len(OP[job][alternative])
            for op in OP[job][alternative]:
                protimemax=0
                print(job,alternative,op)
                for k in machine[job][alternative][op]:
                    if protimemax<processing_times[job][alternative][op][k]:
                        protimemax=processing_times[job][alternative][op][k]
                largeH+=protimemax
        units[job] = umaxj
    
    for i in joblist: 
        alternatives[i] = list(range(1, num_alternatives[i-1] + 1))
    

    
    return fjsp_instance, machine, machines_oj, processing_times, alternatives, units, largeH

def print_jobs(fjsp_instance):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(fjsp_instance)

if __name__ == "__main__":
    # Specify the filename
    filename = "data/AFJSP Test Instances/Test 3/test3.txt"
    

    # Parse the FJSP instance from the file
    fjsp_instance,machines,machines_oj, processtimes, alternatives, units, H = parse_afjsp(filename)

    print(machines_oj[1][1])

    #print(H)


    # Print the parsed information
    print_jobs(fjsp_instance) 