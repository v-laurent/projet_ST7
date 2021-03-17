##***************************** Modules

#Modules de structure
from classes import *
from utils import *
from reading_data import *
from model import *

# Modules de base
import numpy as np
import matplotlib.pyplot as plt
import random

from gurobipy import *

##***************************** Reading Data 

country = "Bordeaux"
employees, tasks = readingData(country)
number_of_employees,  number_of_tasks = len(employees), len(tasks)
depots = [TTask(0,employees[k].Latitude, employees[k].Longitude, 0, 0,"",480,1440,[],0,k)
        for k in range(1,number_of_employees+1)]
def sous_taches(Tasks):
    NewTasks=[]
    
employees_unavailability=[]
for k in range(1,number_of_employees+1):
    if len(employees[k].Unavalaibilities)!=0: #if the employee has unavailabilities
        employees_unavailability.append(TTask(-1,employees[k].Unavalaibilities[0].Latitude, employees[k].Unavailabilies[0].Longitude, 
                        employees[k].Unavalaibilities[0].ClosingTime-employees[k].Unavalaibilities[0].ClosingTime,
                        0,"",employees[k].Unavalaibilities[0].OpeningTime, employees[k].Unavalaibilities[0].ClosingTime,
                        [],k))

new_tasks = [None]+ [depots] + tasks

##***************************** Model 

DELTA, T = best_solution(employees,new_tasks)

##****************************   plot 

latitudes=[[] for employee in range(number_of_employees+1)]
longitudes=[[] for employee in range(number_of_employees+1)]
task_numbers=[[] for employee in range(number_of_employees+1)]

for k in range(1,number_of_employees+1):
    T_f = []
    for i in range(number_of_tasks+1):
        T_f.append(T[(k,i)])
    T_indices = np.argsort(T_f)

    for i in T_indices:
        for j in T_indices:
            if DELTA[(i,j,k)]==1:
                if i!=0 and j!=0:
                    #print("distance{}-{}".format(i,j),int(distance(tasks[i],tasks[j])))
                    latitudes[k].append(tasks[i].Latitude)
                    longitudes[k].append(tasks[i].Longitude)
                    task_numbers[k].append(i)
                elif i==0 and j!=0:
                    #print("distance{}-{}".format(i,j),int(distance(employees[k],tasks[j])),"distance au depot")
                    latitudes[k].append(employees[k].Latitude)
                    longitudes[k].append(employees[k].Longitude)
                    task_numbers[k].append(i)
                elif j==0 and i!=0:
                    #print("distance{}-{}".format(i,j),int(distance(tasks[i],employees[k])),"distance au depot")
                    latitudes[k].append(tasks[i].Latitude)
                    longitudes[k].append(tasks[i].Longitude)
                    task_numbers[k].append(i)
    latitudes[k].append(employees[k].Latitude)
    longitudes[k].append(employees[k].Longitude)
    task_numbers[k].append(0)

draw(latitudes,longitudes,task_numbers,country+'_gmplot.html',DELTA)
fichier_texte(DELTA,T,employees,number_of_tasks,country,phase=phase,instance=instance)