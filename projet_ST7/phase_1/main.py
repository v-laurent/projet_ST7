##***************************** Modules

#Modules de structure
from classes import *
from utils import *
from reading_data import *
# Modules de base
import numpy as np
import matplotlib.pyplot as plt
import random
# Module relatif à Gurobi
from gurobipy import *

##***************************** Reading Data 

employees, tasks = readingData("Bordeaux")
number_of_employees = len(employees)
number_of_tasks = len(tasks)

##***************************** Model 

m=Model('PL_phase_1')

#Definition des variables de decision, en majuscules
DELTA={(i,j,k): m.addVar(vtype=GRB.BINARY,name=f'DELTA_{i}_{j}_{k}') 
    for i in range(0,number_of_tasks+1) 
    for j in range(0,number_of_tasks+1)
    for k in range(1,number_of_employees+1)}

T={(i,k): m.addVar(vtype=GRB.INTEGER,lb=480, ub=1440, name=f'T_{i}_{k}') 
    for i in range(1,number_of_tasks+1) 
    for k in range(1,number_of_employees+1)}

#Definition des variables utiles pour la modelisation du probleme
d={(i,j,k): distance(tasks[i-1],tasks[j-1]) for i in range(1,len(tasks)+1) for j in range(1,len(tasks)+1) for k in range(1,len(employees)+1)}

for k in range(1,len(employees)+1):
    for j in range(1,len(tasks)+1):
        d[0,j,k]=distance(employees[k-1],tasks[j-1])
        d[j,0,k]=distance(employees[k-1],tasks[j-1])
    d[0,0,k]=0


t={i: tasks[i-1].TaskDuration for i in range(1,len(tasks)+1)}

s_employees={i: employees[i-1].WorkingStartTime for i in range(1,len(employees)+1)}

e_employees={i: employees[i-1].WorkingEndTime for i in range(1,len(employees)+1)}

s_tasks={i: tasks[i-1].OpeningTime for i in range(1,len(tasks)+1)}

e_tasks={i: tasks[i-1].ClosingTime for i in range(1,len(tasks)+1)}

level_employee={i: employees[i-1].Level for i in range(1,len(employees)+1)}

level_task={i: tasks[i-1].Level for i in range(1,len(tasks)+1)}

# Definition des contraintes 
Realisation_constr=dict()

for task1 in range(1,number_of_tasks+1):
    Realisation_constr[task1]=m.addConstr(quicksum(DELTA[(task1,task2,employee)] 
                                        for task2 in range(0,len(tasks)+1) 
                                        for employee in range(1,len(employees)+1))==1, 
                                        name='DELTA_{}'.format(task1))
                      

Unique_task_constr=dict()
Start_task_constr=dict()
M=1440
for k in range(1,len(employees)+1):
    for j in range(1,len(tasks)+1):
        Start_task_constr[(j,k)]=m.addConstr(T[(j,k)]>=employees[k-1].WorkingStartTime+trajet(employees[k-1],tasks[j-1])-(1-DELTA[(0,j,k)])*M, name=f'Start_task_constr_{j}_{k}')
        for i in range(1,len(tasks)+1):
            print("trajet{}{}".format(i-1,j-1),trajet(tasks[i-1],tasks[j-1]))
            Unique_task_constr[(i,j,k)]=m.addConstr(T[(j,k)]>=T[(i,k)]+t[i]+trajet(tasks[i-1],tasks[j-1])-(1-DELTA[(i,j,k)])*M,name=f'Unique_{i}_{j}_{k}')

Available_task_constr_sup=dict()
Available_task_constr_inf=dict()
for i in range(1,len(tasks)+1):
    for k in range(1,len(employees)+1):
        Available_task_constr_sup[(i,k)]=m.addConstr(T[(i,k)]<=e_tasks[i]-t[i])
        Available_task_constr_inf[(i,k)]=m.addConstr(T[(i,k)]>=s_tasks[i])

Available_employee_constr_sup=dict()
Available_employee_constr_inf=dict()
for i in range(1,len(tasks)+1):
    for k in range(1,len(employees)+1):
        Available_employee_constr_sup[(i,k)]=m.addConstr(T[(i,k)]<=e_employees[k]-t[i]-trajet(employees[k-1],tasks[i-1]))
        Available_employee_constr_inf[(i,k)]=m.addConstr(T[(i,k)]>=s_employees[k])

Level_constr=dict()
for j in range(1,len(tasks)+1):
    Level_constr[j]=m.addConstr(quicksum(DELTA[(i,j,k)]*(level_employee[k]-level_task[j])
                                for i in range(1,len(tasks)+1)
                                for k in range(1,len(employees)+1))>=0)

Start_employee=dict()
for k in range(1,len(employees)+1):
    Start_employee[k]=m.addConstr(quicksum(DELTA[(0,j,k)]
                                    for j in range(1,len(tasks)+1))==1)
                                    
End_employee=dict()
for k in range(1,len(employees)+1):
    End_employee[k]=m.addConstr(    quicksum(DELTA[(i,0,k)] 
                                    for i in range(1,len(tasks)+1))==1)

Flow_constr=dict()
for k in range(1,len(employees)+1):
    for t in range(0,len(tasks)+1):
        Flow_constr[(k,t)]=m.addConstr(quicksum(DELTA[(i,t,k)]
                                        for i in range(0,len(tasks)+1))==
                                        quicksum(DELTA[(t,j,k)]
                                        for j in range(0,len(tasks)+1)))

m.setObjective(quicksum(DELTA[(i,j,k)]*d[(i,j,k)] for i in range(0, len(tasks)+1)
                                                for j in range(0,len(tasks)+1)
                                                for k in range(1,len(employees)+1)),GRB.MINIMIZE)

# -- Mise à jour du modèle  --
m.update()
m.optimize()
latitudes=[[] for employee in range(len(employees))]
longitudes=[[] for employee in range(len(employees))]
task_numbers=[[] for employee in range(len(employees))]
for k in range(1,len(employees)+1):
    latitudes[k-1].append(employees[k-1].Latitude)
    longitudes[k-1].append(employees[k-1].Longitude)
    task_numbers[k-1].append(0)
    for i in range(0,len(tasks)+1):
        for j in range(0,len(tasks)+1):
            if DELTA[(i,j,k)].x==1:
                if i!=0 and j!=0:
                    print("distance{}-{}".format(i,j),distance(tasks[i-1],tasks[j-1]))
                    latitudes[k-1].append(tasks[i-1].Latitude)
                    longitudes[k-1].append(tasks[i-1].Longitude)
                    task_numbers[k-1].append(i)
                elif i==0 and j!=0:
                    print("distance{}-{}".format(i,j),distance(employees[k-1],tasks[j-1]),"distance au depot")
                    latitudes[k-1].append(employees[k-1].Latitude)
                    longitudes[k-1].append(employees[k-1].Longitude)
                    task_numbers[k-1].append(i)
                elif j==0 and i!=0:
                    print("distance{}-{}".format(i,j),distance(tasks[i-1],employees[k-1]),"distance au depot")
                    latitudes[k-1].append(tasks[i-1].Latitude)
                    longitudes[k-1].append(tasks[i-1].Longitude)
                    task_numbers[k-1].append(i)
    latitudes[k-1].append(employees[k-1].Latitude)
    longitudes[k-1].append(employees[k-1].Longitude)
    task_numbers[k-1].append(0)
draw(latitudes,longitudes,task_numbers,'bordeauxtest',DELTA)
fichier_texte(DELTA,T,employees,number_of_tasks,'bordeaux')