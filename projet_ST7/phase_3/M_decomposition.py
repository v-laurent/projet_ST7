"""
Métaheuristique basée sur des résolutions exactes de sous problèmes

Sous problème : problème initial avec un seul employé (en commençant par les moins qualifiés)
Entre chaque sous problème on retire les tâches déjà effectuées.
(On peut aussi retiré les tâches qui sont trop loin du dépôt de l'employé avant de lancer la résolution)
"""


##***************************** Modules

# Structure modules
from classes import *
from utils import *
from reading_data import *
from model import *

# Basic modules
import numpy as np
import matplotlib.pyplot as plt
import random
from gurobipy import *
from time import time

##***************************** Reading Data  ##*********************************

country = "Ukraine"
instance = '3'
phase = '3'
time_limit = 10     # max resolution time per employee (in seconds)

employees, tasks = readingData(country, instance)

number_of_employees = len(employees)-1
nb_unavailabilities = 0
for employee in employees[1:]:
    nb_unavailabilities += len(employee.Unavailabilities)

depots = [ TTask(0,employees[k].Latitude, employees[k].Longitude,0,"",0,480,1440,[],0,k) for k in range(1,number_of_employees+1) ]

employees_unavailability=[]
r=0
employees_unavailability_rank={}
for k in range(1,number_of_employees+1):
    if len(employees[k].Unavailabilities)!=0: #if the employee has unavailabilities
        employees_unavailability.append(TTask(-1,employees[k].Unavailabilities[0].Latitude, employees[k].Unavailabilities[0].Longitude, 
                        employees[k].Unavailabilities[0].End-employees[k].Unavailabilities[0].Start,
                        "",0,employees[k].Unavailabilities[0].Start, employees[k].Unavailabilities[0].End,
                        [],0,k))
        r += 1
        employees_unavailability_rank[k] = r
 
new_tasks = [0]+ depots + employees_unavailability + sous_taches(tasks)
number_of_fake_tasks = 1 + len(depots) + len(employees_unavailability)

employee_to_rank = {}
for k in range(1,number_of_employees+1):
    employee_to_rank[employees[k].EmployeeName] = k


##**************************** Solving subproblems ##******************************

initial_time = time()
DELTA, T, P = dict(), dict(), dict()
obj_val, nb_task_done = 0, 0

skill_level = []
for k in range(1,number_of_employees+1):
    skill_level.append(employees[k].Level)
employees_indices = np.argsort(skill_level)        # allow to sort employees by level


subtasks = sous_taches(tasks)
done_tasks = []             # tasks already done

for k1 in employees_indices:
    k = k1+1
    chosen_employee = employees[k]
    # choose tasks (depot and unavailability of the chosen employee)
    employee_unavailability = []
    if len(chosen_employee.Unavailabilities)!=0:
        employee_unavailability.append(TTask(-1,chosen_employee.Unavailabilities[0].Latitude, chosen_employee.Unavailabilities[0].Longitude, 
                        chosen_employee.Unavailabilities[0].End-chosen_employee.Unavailabilities[0].Start,
                        "",0,chosen_employee.Unavailabilities[0].Start, chosen_employee.Unavailabilities[0].End,
                        [],0,1))

    chosen_subtasks = []
    chosen_subtasks_indices = []
    for i in range(len(subtasks)):       # keep only subtasks that can be done (close enought, skill needed, ...)
        task = subtasks[i]
        if (task.TaskId not in done_tasks):
            if trajet(task, chosen_employee) <  (chosen_employee.WorkingEndTime-chosen_employee.WorkingStartTime)/2-60:
                if task.Level <= chosen_employee.Level:
                    if task.id_employee == 0:       # everyone can do this task
                        chosen_subtasks.append(task)
                        chosen_subtasks_indices.append(i)
                    elif task.id_employee == employee_to_rank[chosen_employee.EmployeeName]:
                        task.id_employee = 1
                        chosen_subtasks.append(task)
                        chosen_subtasks_indices.append(i)

    chosen_depot = depots[k1]
    chosen_depot.id_employee = 1
    chosen_tasks = [0] + [chosen_depot] + employee_unavailability + chosen_subtasks
    chosen_number_of_fake_tasks = 1 + 1 + len(employee_unavailability)
    number_of_tasks = len(chosen_tasks)-1

    # subproblem exact resolution
    DELTA_k, T_k, P_k, obj_val_k, nb_task_done_k = best_solution([[],chosen_employee], chosen_tasks, chosen_number_of_fake_tasks, 0, TimeLimit=time_limit)


    # update final variables
    obj_val += obj_val_k
    nb_task_done += nb_task_done_k
    for i in range(1,number_of_tasks+1):
        for j in range(1,number_of_tasks+1):
            if i==1:    #depot
                i_global = k
            elif i < chosen_number_of_fake_tasks:   #unavalability
                R = employees_unavailability_rank[employee_to_rank[chosen_employee.EmployeeName]]
                i_global = number_of_employees + R
            else:
                i_global = number_of_fake_tasks + chosen_subtasks_indices[i-chosen_number_of_fake_tasks]
            if j==1:
                j_global = k
            elif j < chosen_number_of_fake_tasks:
                R = employees_unavailability_rank[employee_to_rank[chosen_employee.EmployeeName]]
                j_global = number_of_employees + R
            else:
                j_global = number_of_fake_tasks + chosen_subtasks_indices[j-chosen_number_of_fake_tasks]
            DELTA[(i_global,j_global,k)] = DELTA_k[(i,j,1)]
            T[(k,i_global)] = T_k[(1,i)]
            P[(k,i_global)] = P_k[(1,i)]

            # remove tasks already done
            if int(DELTA_k[(i,j,1)]) == 1:
                if i >= chosen_number_of_fake_tasks:
                    done_tasks.append(chosen_tasks[i].TaskId)


##****************************  print objective  ##************************

number_of_tasks=len(new_tasks)-1    # need all the tasks
for k in range(1,number_of_employees+1):
    for i in range(1,number_of_tasks+1):
        for j in range(1,number_of_tasks+1):
            if (i,j,k) not in DELTA.keys():
                DELTA[(i,j,k)]=0
        if (k,i) not in T.keys():
            T[(k,i)] = 0
            P[(k,i)] = 0

print('---------------------------------------------------------')
print('Profit value : ', round(obj_val,2))
print('Pourcentage of tasks done : {} % ({} / {})'.format(round((nb_task_done-number_of_fake_tasks)/(len(tasks)-1)*100,2),int(nb_task_done-number_of_fake_tasks), len(tasks)-1))
print('Resolution time : {}s'.format(round(time()-initial_time)))
print('---------------------------------------------------------')


# for k in range(1,number_of_employees+1):
#     for i in range(1,number_of_tasks+1):
#         for j in range(1,number_of_tasks+1):
#             if int(DELTA[(i,j,k)])==1:
#                 print(new_tasks[i].TaskId, new_tasks[j].TaskId, k)


##****************************   plot  ##************************

latitudes=[[] for employee in range(number_of_employees+1)]
longitudes=[[] for employee in range(number_of_employees+1)]
task_numbers=[[] for employee in range(number_of_employees+1)]

for k in range(1,number_of_employees+1):
    T_f = []
    for i in range(1,number_of_tasks+1):
        T_f.append(T[(k,i)]) #storing the start times of tasks
    T_indices = np.argsort(T_f)+1
    for i in T_indices:
        for j in T_indices:
            if int(DELTA[(i,j,k)])==1:
                if i not in range(1,number_of_employees+1) and j not in range(1,number_of_employees+1):
                    #print("distance{}-{}".format(i,j),int(distance(tasks[i],tasks[j])))
                        latitudes[k].append(new_tasks[i].Latitude)
                        longitudes[k].append(new_tasks[i].Longitude)
                        task_numbers[k].append(new_tasks[i].TaskId)
                elif i in range(1,number_of_employees+1) and j not in range(1,number_of_employees+1):
                    #print("distance{}-{}".format(i,j),int(distance(employees[k],tasks[j])),"distance au depot")
                    latitudes[k].append(employees[k].Latitude)
                    longitudes[k].append(employees[k].Longitude)
                    task_numbers[k].append("D")
                elif j in range(1,number_of_employees+1) and i not in range(1,number_of_employees+1):
                    #print("distance{}-{}".format(i,j),int(distance(tasks[i],employees[k])),"distance au depot")
                    latitudes[k].append(new_tasks[i].Latitude)
                    longitudes[k].append(new_tasks[i].Longitude)
                    task_numbers[k].append(new_tasks[i].TaskId)
    latitudes[k].append(employees[k].Latitude)
    longitudes[k].append(employees[k].Longitude)
    task_numbers[k].append(0)

draw(employees,tasks,latitudes,longitudes,task_numbers,country+'_gmplot.html',DELTA)
fichier_texte(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance)
score(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance)
