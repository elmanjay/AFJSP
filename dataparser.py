def parse_fjsp(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Parse number of jobs and machines
    first_line = lines[0].strip().split()
    num_jobs = int(first_line[0])
    num_machines = int(first_line[1])

    jobs = {}
    machines = {}  # Maschinen-IDs
    processing_times = {}  # Verarbeitungszeiten

    # Parse each job's operations
    for i in range(1, num_jobs + 1):
        line = lines[i].strip().split()
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
        
        jobs[f'job_{i}'] = operations

        # Extrahiere Maschinen-IDs für jede Operation in jedem Job
        machines[f'job_{i}'] = {}
        for j, ops in operations.items():
            machines[f'job_{i}'][j] = [op['machine_id'] for op in ops]
            
        # Extrahiere Verarbeitungszeiten für jede Operation in jedem Job
        processing_times[f'job_{i}'] = {}
        for j, ops in operations.items():
            processing_times[f'job_{i}'][j] = {op['machine_id']: op['processing_time'] for op in ops}

    fjsp_instance = {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'jobs': jobs
    }

    jobs = [i for i in range(1, fjsp_instance["num_jobs"] + 1)]
    
    test = []
    for job_id in jobs:
        job_operations = fjsp_instance['jobs'][f'job_{job_id}']
        job_op = list(job_operations.keys())
        test.append(job_op)
    
    

    return fjsp_instance, machines, processing_times

def print_jobs(fjsp_instance):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(fjsp_instance)

if __name__ == "__main__":
    # Specify the filename
    filename = 'data/fjsp-instances-main 2/dauzere/01a.txt'

    # Parse the FJSP instance from the file
    fjsp_instance,machines,processtimes = parse_fjsp(filename)

    # Print the parsed information
    print_jobs(fjsp_instance) 