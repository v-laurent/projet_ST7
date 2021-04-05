# Structure modules
from classes import *
from utils import *
from reading_data import *
from model import *

# Basic modules
import numpy as np
import matplotlib.pyplot as plt
import random


"""
Definition of some useful fonctions to enhance an existing solution
"""

def fill(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance):
    number_of_tasks = len(new_tasks)-1
    number_of_employees = len(employees)-1
    # storing indices of tasks done, and in the right order
    T_f = []
    for i in range(1,number_of_tasks+1):
        for j in range(1,number_of_tasks+1):
            if DELTA[(i,j,k)]==1:
                T_f.append(T[(k,i)])    #storing the start times of tasks
    sorted_indices = np.argsort(T_f)+1

    for k in range(1, number_of_employees+1):
        # calculate the inactivity time of employee k
        tasks_time_k, travel_time_k, unavailability_time_k = 0, 0, 0
        for i in sorted_indices:
            for j in sorted_indices:
                if type(new_tasks[i].TaskId) != int:
                    tasks_time_k += new_tasks[i].TaskDuration
                travel_time_k += trajet(new_tasks[i],new_tasks[j])
        for l in range(len(employees[k].Unavailabilities)):
            unavailability_time_k += employees[k].Unavailabilities[l].End - employees[k].Unavailabilities[l].Start
        inactivity_time_k = employees[k].WorkingEndTime - employees[k].WorkingStartTime - tasks_time_k - travel_time_k - unavailability_time_k
        
        # search a tasks close enought to be done during inactivity time
        possible_tasks = []
        for t in range(1, len(tasks)):
            for i in sorted_indices:
                for j in sorted_indices:
                    if (tasks[t].TaskId != new_tasks[i].TaskId) and (tasks[t].TaskId != new_tasks[j].TaskId)
                        if trajet(new_tasks[i],tasks[t]) + tasks[t] + trajet(tasks[t], new_tasks[j]):
                            possible_tasks.append((t,i,j))
        
        # if the schedule is already full
        if len(possible_tasks)==0:
            return (DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance)

        # else, we try to add a task
        updated_DELTA, updated_T, updated_P = DELTA, T, P
        for (t,i0,j0) in possible_tasks:
            for l in range(1,len(sorted_indices)):
                i1 = sorted_indices[l-1]
                j1 = sorted_indices[l]
                if i1==0:
                    updated_T[i] = employees[k].WorkingStartTime
                elif j1 < i0:
                    if new_tasks[j1].TaskId != -1:
                        updated_T[j1] = updated_T[i1] + new_tasks[j1].TaskDuration + trajet(new_tasks[i1],new_tasks[j1]) + 60*P[i1] 
                        for l in range(len(new_tasks[j1].Unavailabilities)):
                            if (updated_T[j1] > new_tasks[j1].Unavailabilities[l].Start) and (updated_T[j1] < new_tasks[j1].Unavailabilities[l].End):
                                updated_T[j1] = T[j1]







#fichier_texte(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance)
