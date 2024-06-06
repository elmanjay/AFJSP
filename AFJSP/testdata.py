def parse_fjsp(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Parse number of jobs and machines
    first_line = lines[0].strip().split()
    num_jobs = int(first_line[0])
    num_machines = int(first_line[1])
    num_alternatives = [int(i) for i in first_line[2:]]

    jobs = {}

    current_line_index = 1

    for job_id in range(1, num_jobs + 1):
        jobs[f'job_{job_id}'] = {}

        for alternative_id in range(1, num_alternatives[job_id-1] + 1):
            line = lines[current_line_index].strip().split()
            current_line_index += 1

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

                operations[f'operation_{op_id + 1}'] = options

            jobs[f'job_{job_id}'][f'alternative_{alternative_id}'] = operations

    fjsp_instance = {
        'num_jobs': num_jobs,
        'num_machines': num_machines,
        'num_alternatives': num_alternatives,
        'jobs': jobs
    }

    return fjsp_instance

# Beispielnutzung
filename = 'data/afjsp/sm01_1.txt'
fjsp_instance = parse_fjsp(filename)

# Ausgabe zur Überprüfung
from pprint import pprint
pprint(fjsp_instance)
