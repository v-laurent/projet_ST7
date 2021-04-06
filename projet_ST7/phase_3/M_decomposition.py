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
from clustering import *

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
time_limit = 10     # maximum resolution time per employee (in second)
cluster = True




if cluster:     # using clusters
    employees, tasks = subdivise_problem(country, instance=instance, plotting_solution = False)   
    print("--- Clustering done !")

else :          # with no cluster (ie one big cluster)
    employees, tasks = readingData(country, instance)


##***************************** Preparing data ##*********************************
if cluster:
    number_of_clusters = len(tasks)
    real_tasks = [[] for c in range(number_of_clusters)]
    for c in range(number_of_clusters):
        employees_c = [0] + employees[c]
        number_of_employees_c = len(employees_c)-1

        nb_unavailabilities = 0
        for employee_c in employees_c[1:]:
            nb_unavailabilities += len(employee_c.Unavailabilities)

        depots = [ TTask(0,employees_c[k].Latitude, employees_c[k].Longitude,0,"",0,480,1440,[],0,k) for k in range(1,number_of_employees_c+1) ]

        employees_c_unavailability=[]
        r=0
        employees_c_unavailability_rank={}
        for k in range(1,number_of_employees_c+1):
            if len(employees_c[k].Unavailabilities)!=0: #if the employee has unavailabilities
                employees_c_unavailability.append(TTask(-1,employees_c[k].Unavailabilities[0].Latitude, employees_c[k].Unavailabilities[0].Longitude, 
                                employees_c[k].Unavailabilities[0].End-employees_c[k].Unavailabilities[0].Start,
                                "",0,employees_c[k].Unavailabilities[0].Start, employees_c[k].Unavailabilities[0].End,
                                [],0,k))
                r += 1
                employees_c_unavailability_rank[k] = r

        number_of_fake_tasks = 1 + number_of_employees_c + nb_unavailabilities
        real_tasks[c] = tasks[c][number_of_fake_tasks-1:]

tasks = real_tasks



##***************************** Solving on each cluster ##*********************************

def solving_all_clusters(employees, tasks, time_limit_per_employee=10):
    number_of_clusters = len(employees)
    obj_val_final, nb_tasks_done_final, number_of_fake_tasks_final, resolution_time_final = 0,0,1,0
    employees_final, new_tasks_final = [0], [0]
    nb_of_employees_seen, nb_of_tasks_seen = 0,0
    DELTA_final, T_final, P_final = dict(), dict(), dict()

    for c in range(number_of_clusters):
        employees_c = [0] + employees[c]
        number_of_employees_c = len(employees_c)-1

        tasks_c = [0] + tasks[c]

        print(f"------------ Cluster {c} starting ------------")
        # preparing data
        depots_c = [ TTask(0,employees_c[k].Latitude, employees_c[k].Longitude,0,"",0,480,1440,[],0,k) for k in range(1,number_of_employees_c) ]
        print(f"Number of employees : {number_of_employees_c}")
        for k in range(1,number_of_employees_c+1):
            print(f"-- {employees_c[k].EmployeeName}")
        for i in range(1,len(tasks_c)):
            print(tasks_c[i].TaskId)

        # solving on one cluster
        (DELTA_c,T_c,P_c,new_tasks_c,nb_unavailabilities_c, obj_val_c,nb_tasks_done_c,number_of_fake_tasks_c,resolution_time_c) = solving_one_cluster(employees_c, tasks_c, time_limit_per_employee)

        # update final variable
        obj_val_final += obj_val_c
        nb_tasks_done_final += nb_tasks_done_c
        number_of_fake_tasks_final += number_of_fake_tasks_c-1
        resolution_time_final += resolution_time_c
        
        for k in range(1,number_of_employees_c+1):
            k_final = nb_of_employees_seen + k
            for i in range(1,len(new_tasks_c)):
                i_final = nb_of_tasks_seen + i
                for j in range(1,len(new_tasks_c)):
                    j_final = nb_of_tasks_seen + j
                    DELTA_final[(i_final,j_final,k_final)] = DELTA_c[(i,j,k)]
                    if DELTA_c[(i,j,k)]==1:
                        print((i,j,k))
                T_final[(k_final,i_final)] = T_c[(k,i)]
                P_final[(k_final,i_final)] = P_c[(k,i)]
        
        employees_final += employees_c[1:]
        new_tasks_final += new_tasks_c[1:]
        nb_of_employees_seen = len(employees_final)-1
        nb_of_tasks_seen = len(new_tasks_final)-1
        print(f"-------------- Cluster {c} done --------------")

    # fill variables
    for k in range(1,nb_of_employees_seen+1):
        for i in range(1,nb_of_tasks_seen+1):
            for j in range(1,nb_of_tasks_seen+1):
                if (i,j,k) not in DELTA_final.keys():
                    DELTA_final[(i,j,k)]=0
            if (k,i) not in T_final.keys():
                T_final[(k,i)] = 0
                P_final[(k,i)] = 0

    for k in range(1,nb_of_employees_seen+1):
        s=0
        for i in range(1,nb_of_tasks_seen+1):
            s += P_final[(k,i)]
        print(s)

    # print objective
    nb_total_real_tasks = 0
    for c in range(number_of_clusters):
        nb_total_real_tasks += len(tasks[c])
    print('---------------------------------------------------------')
    print('Profit value : ', round(obj_val_final,2))
    print('Pourcentage of tasks done : {} % ({} / {})'.format(round((nb_tasks_done_final-number_of_fake_tasks_final)/nb_total_real_tasks*100,2),int(nb_tasks_done_final-number_of_fake_tasks_final), nb_total_real_tasks))
    print('Resolution time : {}s'.format(round(resolution_time_final)))
    print('---------------------------------------------------------')

    return(employees_final,new_tasks_final,DELTA_final,T_final,P_final)




def solving_one_cluster(employees, tasks, time_limit_per_employee=10):
    # global problem
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
    

    # solving subproblems
    employee_to_rank = {}
    for k in range(1,number_of_employees+1):
        employee_to_rank[employees[k].EmployeeName] = k

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
                        elif (task.id_employee == employee_to_rank[chosen_employee.EmployeeName]) and (task.TaskId != -1):
                            task.id_employee = 1
                            chosen_subtasks.append(task)
                            chosen_subtasks_indices.append(i)

        chosen_depot = depots[k1]
        #chosen_depot = TTask(0,employees[k1].Latitude, employees[k1].Longitude,0,"",0,480,1440,[],0,k1)
        chosen_depot.id_employee = 1
        chosen_tasks = [0] + [chosen_depot] + employee_unavailability + chosen_subtasks
        chosen_number_of_fake_tasks = 1 + 1 + len(employee_unavailability)
        number_of_tasks = len(chosen_tasks)-1

        # subproblem exact resolution
        DELTA_k, T_k, P_k, obj_val_k, nb_task_done_k = best_solution([[],chosen_employee], chosen_tasks, chosen_number_of_fake_tasks, 0, TimeLimit=time_limit_per_employee)


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

    number_of_tasks=len(new_tasks)-1    # need all the tasks
    for k in range(1,number_of_employees+1):
        for i in range(1,number_of_tasks+1):
            for j in range(1,number_of_tasks+1):
                if (i,j,k) not in DELTA.keys():
                    DELTA[(i,j,k)]=0
            if (k,i) not in T.keys():
                T[(k,i)] = 0
                P[(k,i)] = 0

    resolution_time = time()-initial_time
    
    return(DELTA,T,P,new_tasks,nb_unavailabilities, obj_val, nb_task_done, number_of_fake_tasks, resolution_time)





if cluster:
    (employees_final,new_tasks_final,DELTA_final,T_final,P_final) = solving_all_clusters(employees, tasks, time_limit_per_employee=time_limit)
else:
    (DELTA_final,T_final,P_final,new_tasks_final) = solving_one_cluster(employees, tasks, time_limit_per_employee=time_limit)[:4]



##****************************   plot  ##************************
"""
input : employees, new_tasks, DELTA, T
"""
if cluster:
    tasks_final = [0]
    for c in range(len(tasks)):
        tasks_final += tasks[c]
else:
    employees_final = employees
    tasks_final = tasks


number_of_employees = len(employees_final)-1
number_of_tasks = len(new_tasks_final)-1

latitudes=[[] for employee in range(number_of_employees+1)]
longitudes=[[] for employee in range(number_of_employees+1)]
task_numbers=[[] for employee in range(number_of_employees+1)]

for k in range(1,number_of_employees+1):
    T_f = []
    for i in range(1,number_of_tasks+1):
        T_f.append(T_final[(k,i)]) #storing the start times of tasks
    T_indices = np.argsort(T_f)+1
    latitudes[k].append(employees_final[k].Latitude)
    longitudes[k].append(employees_final[k].Longitude)
    task_numbers[k].append(0)
    for i in T_indices:
        for j in T_indices:
            if int(DELTA_final[(i,j,k)])==1:
                if (new_tasks_final[i].TaskId != 0) and (new_tasks_final[i].TaskId != 0):
                    latitudes[k].append(new_tasks_final[i].Latitude)
                    longitudes[k].append(new_tasks_final[i].Longitude)
                    task_numbers[k].append(new_tasks_final[i].TaskId)
                elif (new_tasks_final[i].TaskId == 0) and (new_tasks_final[i].TaskId != 0):
                    latitudes[k].append(employees_final[k].Latitude)
                    longitudes[k].append(employees_final[k].Longitude)
                    task_numbers[k].append("D")
                elif (new_tasks_final[i].TaskId != 0) and (new_tasks_final[i].TaskId == 0):
                    latitudes[k].append(new_tasks_final[i].Latitude)
                    longitudes[k].append(new_tasks_final[i].Longitude)
                    task_numbers[k].append(new_tasks_final[i].TaskId)
    latitudes[k].append(employees_final[k].Latitude)
    longitudes[k].append(employees_final[k].Longitude)
    task_numbers[k].append(0)

draw(employees_final,tasks_final,latitudes,longitudes,task_numbers,country+'_gmplot.html',DELTA_final)
fichier_texte(DELTA_final,T_final,P_final,tasks_final,new_tasks_final,employees_final,country,phase=phase,instance=instance)
score(DELTA_final,T_final,P_final,tasks_final,new_tasks_final,employees_final,country,phase=phase,instance=instance)
