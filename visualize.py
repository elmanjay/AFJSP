import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# CSV-Datei einlesen
file_path = 'solution.csv'
data = pd.read_csv(file_path)

jobs = data["Values"]

# for column, value in data.iloc[0].items():
#     new_columns[column] = f'New_{value}' 
# print(data)
#data["Variable"].head()

# Parameter einlesen
# num_jobs = 10
# num_machines = 20

# Variablen herausfiltern
# t_vars = data[data['Variable'].str.startswith('t_')]
# a_vars = data[data['Variable'].str.startswith('a_')]