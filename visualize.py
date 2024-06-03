import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# CSV-Datei einlesen
file_path = 'solution.csv'
data = pd.read_csv(file_path)

#Parameter einlesen
num_jobs = int(data[data['Variable'] == 'Anzahl Jobs:']["Value"].iloc[0])
num_machines = int(data[data['Variable'] == 'Anzahl Maschinen:']["Value"].iloc[0])

# Variablen herausfiltern
#t_werte
start_times = data[data['Variable'].str.startswith('t_')].copy()
assignments = data[data['Variable'].str.startswith('a_')].copy()
processing_times = data[data['Variable'].str.startswith('p_')].copy()
B_Vars = data[data['Variable'].str.startswith('B_')].copy()

start_times['Job'] = start_times['Variable'].str.split('_').str[1].astype(int)
start_times['Operation'] = start_times['Variable'].str.split('_').str[2].astype(int)
start_times = start_times.sort_values(by=['Job', 'Operation'])
start_times = start_times.rename(columns={'Value': 'Start'})

assignments['Job'] = assignments['Variable'].str.split('_').str[1].astype(int)
assignments['Operation'] = assignments['Variable'].str.split('_').str[2].astype(int)
assignments['Machine'] = assignments['Variable'].str.split('_').str[3].astype(int)
assignments = assignments.sort_values(by=['Job', 'Operation'])

merged_df = pd.merge(start_times, assignments[['Job', 'Operation', 'Machine']], on=['Job', 'Operation'])
#print(merged_df.head())

processing_times['Job'] = processing_times['Variable'].str.split('_').str[1].astype(int)
processing_times['Operation'] = processing_times['Variable'].str.split('_').str[2].astype(int)
processing_times['Machine'] = processing_times['Variable'].str.split('_').str[3].astype(int)
processing_times = processing_times.sort_values(by=['Job', 'Operation'])
processing_times = processing_times.rename(columns={'Value': 'Processing Time'})

final_df = pd.merge(merged_df, processing_times[['Job', 'Operation', 'Machine', 'Processing Time']], on=['Job', 'Operation', 'Machine'])
final_df.drop("Variable", axis=1, inplace=True)
final_df["End"] = final_df["Start"] + final_df["Processing Time"]
final_df = final_df.astype(int)
print(final_df.head())

G = nx.DiGraph()
for index, row in final_df.iterrows():
    job = row['Job']
    operation = row['Operation']
    start_time = row['Start']
    end_time = row['End']  # Nehmen wir an, dass die Spalte 'End' die Endzeit enthält
    machine = row['Machine']  # Nehmen wir an, dass die Spalte 'Machine' die Maschine enthält

    # Das Attribut 'start_time' zum Datenattribut des Knotens hinzufügen
    G.add_node(f"J{job}_O{operation}", start_time=start_time, end_time=end_time, machine=machine)
    G.nodes[f"J{job}_O{operation}"]['job'] = job

# Kanten hinzufügen, um die Operationen eines Jobs in Reihenfolge zu verbinden
jobs = final_df['Job'].unique()
for job in jobs:
    job_operations = final_df[final_df['Job'] == job]
    for i in range(len(job_operations) - 1):
        current_operation = job_operations.iloc[i]['Operation']
        next_operation = job_operations.iloc[i + 1]['Operation']
        G.add_edge(f"J{job}_O{current_operation}", f"J{job}_O{next_operation}")

# Knotenpositionen für Visualisierung
print(G.nodes)
pos = {}
for node in G.nodes():
    job = G.nodes[node]['job']
    operation = int(node.split('_')[1].replace('.', '')[1:])
    y = job * 0.5  # x-Position basierend auf dem Job
    x = operation * 2  # y-Position basierend auf der Maschine und der Operation
    pos[node] = (x, y)

# Labels extrahieren
labels = {node: f"{node}\n S:{G.nodes[node]['start_time']} E:{G.nodes[node]['end_time']} \n M:{G.nodes[node]['machine']}" for node in G.nodes()}



# Graph visualisieren
plt.figure(figsize=(20, 17))
nx.draw_networkx(G, pos, labels=labels, node_size=3000, node_color='lightblue', font_size=10, arrows=True)

plt.title("Start Times Visualization with Directed Edges")
plt.show()


