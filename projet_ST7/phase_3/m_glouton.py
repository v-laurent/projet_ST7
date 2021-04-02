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

country = "Test"
employees, tasks = readingData(country)

number_of_employees,  number_of_tasks = len(employees), len(tasks)
nb_unavailabilities = 0
for employee in employees[1:]:
    nb_unavailabilities += len(employee.Unavailabilities)

depots = [ TTask(0,employees[k].Latitude, employees[k].Longitude,0,"",0,480,1440,[],0,k) for k in range(1,number_of_employees) ]


employees_unavailability=[]
for k in range(1,number_of_employees):
    if len(employees[k].Unavailabilities)!=0: #if the employee has unavailabilities
        employees_unavailability.append(TTask(-1,employees[k].Unavailabilities[0].Latitude, employees[k].Unavailabilities[0].Longitude, 
                        employees[k].Unavailabilities[0].End-employees[k].Unavailabilities[0].Start,
                        "",0,employees[k].Unavailabilities[0].Start, employees[k].Unavailabilities[0].End,
                        [],0,k))
 
    #     employees_unavailability.append(0)

new_tasks = [0]+ depots + employees_unavailability + sous_taches(tasks)
number_of_tasks=len(new_tasks)-1
number_of_employees=len(employees)-1
number_of_fake_tasks = 1 + len(depots) + len(employees_unavailability)
d = { (i,j,k) : distance(new_tasks[i], new_tasks[j])
            for i in range(1, number_of_tasks+1)  
            for j in range(1, number_of_tasks+1)  
            for k in range(1, number_of_employees+1) }
############################## Metaheuristic
for i in range(1,len(new_tasks)):
    print(new_tasks[i])

route=[(1,480),(2,600),(1,1080)]
def travels(route):
    res=[]
    for i in range(1,len(route)):
        res.append([route[i-1],route[i]])
    return res
print(travels(route))

def travel_time_possible(travel,i_task):
    i_depart=travel[0][0]
    i_arrivee=travel[1][0]
    t_depart=travel[0][1]
    t_arrivee=travel[1][1]
    if t_depart+ new_tasks[i_depart].TaskDuration + trajet(new_tasks[i_depart],new_tasks[i_task]) + new_tasks[i_task].TaskDuration + trajet(new_tasks[i_task],new_tasks[i_arrivee])<=t_arrivee:
        return True
    return False

liste_possibles=[]


