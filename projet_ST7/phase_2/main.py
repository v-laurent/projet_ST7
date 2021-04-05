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

##***************************** Reading Data  ##*********************************

country = "Austria"
employees, tasks = readingData(country)

number_of_employees,  number_of_tasks = len(employees), len(tasks)
nb_unavailabilities = 0
for employee in employees[1:]:
    nb_unavailabilities += len(employee.Unavailabilities)

depots = [ TTask(0,employees[k].Latitude, employees[k].Longitude,0,"",0,480,1440,[],0,k) for k in range(1,number_of_employees) ]
            

employees_unavailability=[]
for k in range(1,number_of_employees):
    number_of_unavailabilities_k=len(employees[k].Unavailabilities)
    if number_of_unavailabilities_k!=0: #if the employee has unavailabilities
        for unavailability in range(number_of_unavailabilities_k):
            employees_unavailability.append(TTask(-1,employees[k].Unavailabilities[unavailability].Latitude, employees[k].Unavailabilities[unavailability].Longitude, 
                            employees[k].Unavailabilities[unavailability].End-employees[k].Unavailabilities[unavailability].Start,
                            "",0,employees[k].Unavailabilities[unavailability].Start, employees[k].Unavailabilities[unavailability].End,
                            [],0,k))
 
    #     employees_unavailability.append(0)

new_tasks = [0]+ depots + employees_unavailability + sous_taches(tasks)
number_of_tasks=len(new_tasks)-1
number_of_employees=len(employees)-1
number_of_fake_tasks = 1 + len(depots) + len(employees_unavailability)

##***************************** epsilon constraint  ##****************************
DELTA, T, P, traveled_distance, nb_task_done = best_solution(employees, new_tasks,number_of_employees+nb_unavailabilities,0)
'''
<<<<<<< HEAD
<<<<<<< HEAD
DELTA, T, P, traveled_distance, nb_task_done = best_solution(employees, new_tasks,10)
=======
DELTA, T, P, traveled_distance, nb_task_done = best_solution(employees, new_tasks,12)

>>>>>>> 5fc175c58e1a2bc94f6f81cdc8bd9f9d7143f406

"""
epsilon = 0.1
=======
""" To run the code with the first objective function """

#DELTA, T, P, traveled_distance, nb_task_done = best_solution(employees, new_tasks,12)

""" To run the code with the 2nd objective function """

DELTA, T, P, traveled_distance, nb_task_done = best_solution(employees, new_tasks, number_of_fake_tasks, 0)

""" To run the epsilon constraint method, and have the polt of the pareto front 

epsilon = 0.1  #the step of the epsilon constraint 
>>>>>>> b12d0d54500ce8ad9619c033362492b16d8c8296
X, Y = [], []
result = best_solution(employees,new_tasks,0)

it = 0

while result != None:
    DELTA, T, P, traveled_distance, nb_task_done = result
    X.append( round(traveled_distance / 1000,2) )
    Y.append( int(nb_task_done-number_of_employees-nb_unavailabilities) )
    print(it,traveled_distance,nb_task_done)
    it += 1
    result = best_solution(employees, new_tasks, nb_task_done + epsilon)
    
for k,(i, j) in enumerate( zip(X, Y) ):
    plt.scatter(i, j, marker='.', label=str((i,j)))
    plt.annotate(str(k), (i, j))

plt.grid(linestyle='--', color='gray')
plt.xlabel('Travel distance (km)')
plt.ylabel('number of accomplished tasks')
plt.legend()
plt.show()
"""
'''
##****************************   plot  ##************************

latitudes=[[] for employee in range(number_of_employees+1)]
longitudes=[[] for employee in range(number_of_employees+1)]
task_numbers=[[] for employee in range(number_of_employees+1)]

# for i in range(1,number_of_tasks+1):
#     for j in range(1,number_of_tasks+1):
#         for k in range(1,number_of_employees+1):
#             if DELTA[(i,j,k)]==1:
#                 print(i,j,k)
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

draw(employees,latitudes,longitudes,task_numbers,country+'_gmplot.html',DELTA)
fichier_texte(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance)
