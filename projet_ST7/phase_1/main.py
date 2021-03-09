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
task_depot = [TTask(0, employees[0].Latitude, employees[0].Longitude, 0, 0, 0, 480, 1440)] 
tasks = task_depot + tasks
employees = [None] + employees
number_of_employees = len(employees)
number_of_tasks = len(tasks)

##***************************** Model 

m=Model('PL_phase_1')

#Definition des variables de decision, en majuscules
DELTA={(i,j,k): m.addVar(vtype=GRB.BINARY,name=f'DELTA_{i}_{j}_{k}') 
    for i in range(0,number_of_tasks)
    for j in range(0,number_of_tasks)
    for k in range(1,number_of_employees+1)}

T={(i,k): m.addVar(vtype=GRB.INTEGER,lb=480, ub=1440, name=f'T_{i}_{k}') 
    for i in range(0,number_of_tasks) 
    for k in range(1,number_of_employees+1)}

#Definition des variables utiles pour la modelisation du probleme
d={(i,j,k): distance(tasks[i],tasks[j]) for i in range(0,number_of_tasks) for j in range(0,number_of_tasks) for k in range(1,number_of_employees)}

t={i: tasks[i].TaskDuration for i in range(0,number_of_tasks)}

s_employees={i: employees[i].WorkingStartTime for i in range(1,number_of_employees)}

e_employees={i: employees[i].WorkingEndTime for i in range(1,number_of_employees)}

s_tasks={i: tasks[i].OpeningTime for i in range(0,number_of_tasks)}

e_tasks={i: tasks[i].ClosingTime for i in range(0,number_of_tasks)}

level_employee={i: employees[i].Level for i in range(1,number_of_employees)}

level_task={i: tasks[i].Level for i in range(0,number_of_tasks)}

# Definition des contraintes 
Realisation_constr=dict()

for task1 in range(1,number_of_tasks):
    Realisation_constr[task1]=m.addConstr(quicksum(DELTA[(task1,task2,employee)] 
                                        for task2 in range(0,number_of_tasks) 
                                        for employee in range(1,number_of_employees))==1, 
                                        name='DELTA_{}'.format(task1))
                      

Unique_task_constr=dict()
Start_task_constr=dict()
M=1440
for k in range(1,number_of_employees):
    for j in range(1,number_of_tasks):
        for i in range(0,number_of_tasks):
            #print("trajet{}{}".format(i,j),trajet(tasks[i],tasks[j]))
            Unique_task_constr[(i,j,k)]=m.addConstr(T[(j,k)]>=T[(i,k)]+t[i]+trajet(tasks[i],tasks[j])-(1-DELTA[(i,j,k)])*M,name=f'Unique_{i}_{j}_{k}')

Available_task_constr_sup=dict()
Available_task_constr_inf=dict()
for i in range(0,number_of_tasks):
    for k in range(1,number_of_employees):
        Available_task_constr_sup[(i,k)]=m.addConstr(T[(i,k)]<=e_tasks[i]-t[i])
        Available_task_constr_inf[(i,k)]=m.addConstr(T[(i,k)]>=s_tasks[i])

Available_employee_constr_sup=dict()
Available_employee_constr_inf=dict()
for i in range(0,number_of_tasks):
    for k in range(1,number_of_employees):
        Available_employee_constr_sup[(i,k)]=m.addConstr(T[(i,k)]<=e_employees[k]-t[i]-trajet(employees[k],tasks[i]))
        Available_employee_constr_inf[(i,k)]=m.addConstr(T[(i,k)]>=s_employees[k])

Level_constr=dict()
for j in range(0,number_of_tasks):
    Level_constr[j]=m.addConstr(quicksum(DELTA[(i,j,k)]*(level_employee[k]-level_task[j])
                                for i in range(0,number_of_tasks)
                                for k in range(1,number_of_employees))>=0)

Start_employee=dict()
for k in range(1,number_of_employees):
    Start_employee[k]=m.addConstr(quicksum(DELTA[(0,j,k)]
                                    for j in range(0,number_of_tasks))==1)
                                    
End_employee=dict()
for k in range(1,number_of_employees):
    End_employee[k]=m.addConstr(    quicksum(DELTA[(i,0,k)] 
                                    for i in range(0,number_of_tasks))==1)

Flow_constr=dict()
for k in range(1,number_of_employees):
    for t in range(0,number_of_tasks):
        Flow_constr[(k,t)]=m.addConstr(quicksum(DELTA[(i,t,k)]
                                        for i in range(0,number_of_tasks))==
                                        quicksum(DELTA[(t,j,k)]
                                        for j in range(0,number_of_tasks)))

m.setObjective(quicksum(DELTA[(i,j,k)]*d[(i,j,k)] for i in range(0, number_of_tasks)
                                                for j in range(0,number_of_tasks)
                                                for k in range(1,number_of_employees)),GRB.MINIMIZE)

# -- Mise à jour du modèle  --
m.update()
m.optimize()

latitudes=[[] for employee in range(0,number_of_employees)]
longitudes=[[] for employee in range(0,number_of_employees)]
task_numbers=[[] for employee in range(0,number_of_employees)]
for k in range(1,number_of_employees):
    T_f = []
    for i in range(0,number_of_tasks):
        T_f.append(T[i,k].x)
    T_indices = np.argsort(T_f)

    for i in T_indices:
        for j in T_indices:
            if DELTA[(i,j,k)].x==1:
                if i!=0 and j!=0:
                    print("distance{}-{}".format(i,j),int(distance(tasks[i],tasks[j])))
                    latitudes[k].append(tasks[i].Latitude)
                    longitudes[k].append(tasks[i].Longitude)
                    task_numbers[k].append(i)
                elif i==0 and j!=0:
                    print("distance{}-{}".format(i,j),int(distance(employees[k],tasks[j])),"distance au depot")
                    latitudes[k].append(employees[k].Latitude)
                    longitudes[k].append(employees[k].Longitude)
                    task_numbers[k].append(i)
                elif j==0 and i!=0:
                    print("distance{}-{}".format(i,j),int(distance(tasks[i],employees[k])),"distance au depot")
                    latitudes[k].append(tasks[i].Latitude)
                    longitudes[k].append(tasks[i].Longitude)
                    task_numbers[k].append(i)
    latitudes[k].append(employees[k].Latitude)
    longitudes[k].append(employees[k].Longitude)
    task_numbers[k].append(0)

draw(latitudes,longitudes,task_numbers,'bordeauxtest',DELTA)
fichier_texte(DELTA,T,employees,number_of_tasks,'bordeaux')