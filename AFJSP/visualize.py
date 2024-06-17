import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os

def read_solution(file_path="solution.csv"):
    try:
        data = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading the CSV file: {e}")
        return None

    # Parameter einlesen
    try:
        num_jobs = int(data[data['Variable'] == 'NUM_JOBS']["Value"].iloc[0])
        num_machines = int(data[data['Variable'] == 'NUM_MACHINES']["Value"].iloc[0])
    except Exception as e:
        print(f"Error extracting parameters: {e}")
        return None

    # Variablen herausfiltern
    
    start_times = data[data['Variable'].str.startswith('t_')].copy()
    assignments = data[data['Variable'].str.startswith('a_')].copy()
    processing_times = data[data['Variable'].str.startswith('p_')].copy()
    B_Vars = data[data['Variable'].str.startswith('B_')].copy()
    active_alternatives = data[data['Variable'].str.startswith('x_')].copy()

    # Überprüfen und ungültige Einträge herausfiltern
    processing_times = processing_times[processing_times['Variable'].str.count('_') == 4]
    if processing_times.empty:
        print("No valid processing time entries found.")
        return None

    try:
        processing_times['Job'] = processing_times['Variable'].str.split('_').str[1].astype(int)
        processing_times["Alternative"] = processing_times['Variable'].str.split('_').str[2].astype(int)
        processing_times['Operation'] = processing_times['Variable'].str.split('_').str[3].astype(int)
        processing_times['Machine'] = processing_times['Variable'].str.split('_').str[4].astype(int)
        processing_times['Processing Time'] = processing_times['Value'].astype(float)  # Sicherstellen, dass die Werte numerisch sind
    except ValueError as e:
        print(f"Error converting values: {e}")
        print(processing_times['Variable'].str.split('_').str[2])
        return None

    processing_times = processing_times.sort_values(by=['Job', "Alternative", 'Operation'])

    try:
        start_times['Job'] = start_times['Variable'].str.split('_').str[1].astype(int)
        start_times["Alternative"] = start_times['Variable'].str.split('_').str[2].astype(int)
        start_times['Operation'] = start_times['Variable'].str.split('_').str[3].astype(int)
        start_times['Start'] = start_times['Value'].astype(float)  # Sicherstellen, dass die Werte numerisch sind
        start_times = start_times.sort_values(by=['Job', "Alternative", 'Operation'])

        assignments['Job'] = assignments['Variable'].str.split('_').str[1].astype(int)
        assignments["Alternative"] = assignments["Variable"].str.split('_').str[2].astype(int)
        assignments['Operation'] = assignments['Variable'].str.split('_').str[3].astype(int)
        assignments['Machine'] = assignments['Variable'].str.split('_').str[4].astype(int)
        assignments = assignments.sort_values(by=['Job', "Alternative", 'Operation'])

        merged_df = pd.merge(start_times, assignments[['Job', "Alternative", 'Operation', 'Machine']], on=['Job', "Alternative", 'Operation'])

        B_Vars['Job'] = B_Vars['Variable'].str.split('_').str[1].astype(int)
        B_Vars["Alternative"] = B_Vars['Variable'].str.split('_').str[2].astype(int)
        B_Vars['Operation'] = B_Vars['Variable'].str.split('_').str[3].astype(int)
        B_Vars['Next Job'] = B_Vars['Variable'].str.split('_').str[4].astype(int)
        B_Vars['Next Job Alternative'] = B_Vars['Variable'].str.split('_').str[5].astype(int)
        B_Vars['Next Job Operation'] = B_Vars['Variable'].str.split('_').str[6].astype(int)

        active_alternatives["Job"] = active_alternatives['Variable'].str.split('_').str[1].astype(int)
        active_alternatives["Alternative"] = active_alternatives['Variable'].str.split('_').str[2].astype(int)

    except ValueError as e:
        print(f"Error converting values: {e}")
        return None
    
    

    final_df = pd.merge(merged_df, processing_times[['Job', "Alternative", 'Operation', 'Machine', 'Processing Time']], on=['Job', "Alternative", 'Operation', 'Machine'])
    final_df.drop("Variable", axis=1, inplace=True)
    final_df["End"] = final_df["Start"] + final_df["Processing Time"]

    # Rundung der Werte auf Ganzzahlen und Umwandlung in Integer
    final_df["Start"] = final_df["Start"].round().astype(int)
    final_df["Processing Time"] = final_df["Processing Time"].round().astype(int)
    final_df["End"] = final_df["End"].round().astype(int)
    
    return final_df, active_alternatives


def plot_gantt(df, selected_machine):

    # Gantt-Diagramme für jede Maschine erstellen
    machine_df = df[df['Machine'] == selected_machine]

    plt.figure(figsize=(20, 5))

    for index, row in machine_df.iterrows():
        plt.barh(row['Job'], row['Processing Time'], left=row['Start'], edgecolor='black', align='center')

    # Ermitteln der maximalen x-Position der Balken
    max_x_position = machine_df['Start'].max() + machine_df['Processing Time'].max()

    for index, row in machine_df.iterrows():
        # Platzieren des Textes innerhalb des Balkens
        text_x_position = row['Start'] + row['Processing Time'] / 2  # Mittelpunkt des Balkens
        plt.text(text_x_position, row['Job'], f"Job {row['Job']} ALT {row['Alternative']} OP {row['Operation']}", 
                va='center', ha='center', color='white', fontsize=8)

    plt.title(f'Gantt Diagramm für Maschine {selected_machine}')
    plt.ylabel('Job')
    plt.xlabel('Time')
    plt.grid(True)

    # Festlegen der y-Achsenticks auf ganzzahlige Werte
    plt.yticks(range(int(machine_df['Job'].max()) + 1))

    plt.tight_layout()
    plt.show()


def plot_graph(df, active_alternatives):
    G = nx.DiGraph()
    for index, row in df.iterrows():
        job = row['Job']
        operation = row['Operation']
        alternative = row["Alternative"]
        start_time = row['Start']
        end_time = row['End']  # Nehmen wir an, dass die Spalte 'End' die Endzeit enthält
        machine = row['Machine']  # Nehmen wir an, dass die Spalte 'Machine' die Maschine enthält

        # Das Attribut 'start_time' zum Datenattribut des Knotens hinzufügen
        G.add_node(f"J{job}_A{alternative}_O{operation}", start_time=start_time, end_time=end_time, machine=machine)
        G.nodes[f"J{job}_A{alternative}_O{operation}"]['job'] = job

    # Erstelle eine Liste eindeutiger Job-Alternative-Kombinationen
    job_alternative_combinations = df[['Job', 'Alternative']].drop_duplicates()

    # Iteriere über die eindeutigen Kombinationen
    for job, alternative in job_alternative_combinations.itertuples(index=False):
        # Filtere die Operationen für den aktuellen Job und die aktuelle Alternative
        job_alternative_operations = df[(df['Job'] == job) & (df['Alternative'] == alternative)]
        job_alternative_operations = job_alternative_operations.sort_values(by='Operation')

        # Füge Kanten zwischen den Operationen hinzu
        for i in range(len(job_alternative_operations) - 1):
            current_operation = job_alternative_operations.iloc[i]['Operation']
            next_operation = job_alternative_operations.iloc[i + 1]['Operation']
            G.add_edge(f"J{job}_A{alternative}_O{current_operation}", f"J{job}_A{alternative}_O{next_operation}")

    # Knotenpositionen für Visualisierung
    pos = {}
    for node in G.nodes():
        job = G.nodes[node]['job']
        alternative = int(node.split('_')[1].replace('.', '')[1:])
        operation = int(node.split('_')[2].replace('.', '')[1:])
        y = job * 0.5  # x-Position basierend auf dem Job
        x = operation * 2  # y-Position basierend auf der Maschine und der Operation
        pos[node] = (x, y)

    # Labels extrahieren
    labels = {node: f"{node}\n S:{G.nodes[node]['start_time']} E:{G.nodes[node]['end_time']} \n M:{G.nodes[node]['machine']}" for node in G.nodes()}
    
    # Plot und Legende in derselben Figur anzeigen
    fig, ax = plt.subplots(figsize=(20, 17))
    nx.draw_networkx(G, pos, labels=labels, node_size=3000, node_color='lightblue', font_size=10, arrows=True, ax=ax)
    
    # Legende erstellen
    legend_elements = [plt.bar(0, 0, color='lightgreen', label=f'Job {job} Alternative {alternative}') for job, alternative in zip(active_alternatives['Job'], active_alternatives['Alternative'])]
    ax.legend(handles=legend_elements, title='Aktive Alternativen', bbox_to_anchor=(1, 1), loc='upper left')
    
    plt.title("Visualisierung des AFJSP")
    plt.show()

if __name__ == "__main__":
    instance, active = read_solution(file_path="AFJSP\solution.csv")
    #print(instance.head())
    plot_graph(instance,active)
    plot_gantt(instance, 2)


