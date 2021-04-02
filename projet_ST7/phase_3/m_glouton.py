##***************************** Modules

#Modules de structure
from classes import *
from utils import *
from reading_data import *
from model import *
import operator

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
## The travels will be reprensented as follows:
## route =[(location1,start_time),(location2,start_time),(location3,start_time), ...]

for i in range(1,len(new_tasks)):
    print(new_tasks[i])

routes=[0,[(1,480),(4,600),(1,1080)],[(2,480),(2,1080)]] 
def travels_in_route(route): 
    # allows to create couples of origin-destination 
    #example: with route=[(1,480),(2,600),(1,1080)]
    # travels(route) will return [[(1,480),(2,600)],[(2,600),(1,1080)]]
    res=[]
    for i in range(1,len(route)):
        res.append([route[i-1],route[i]])
    return res

def ending_time(travel,i_task):
    # takes arguments the travel (origin-destination) and the index of the task we want to add
    #return the minimal time it will take to reach the destination by going through the task i_task
    i_depart=travel[0][0]
    i_arrivee=travel[1][0]
    t_depart=travel[0][1]
    return t_depart+ new_tasks[i_depart].TaskDuration + trajet(new_tasks[i_depart],new_tasks[i_task]) + new_tasks[i_task].TaskDuration + trajet(new_tasks[i_task],new_tasks[i_arrivee])

def starting_time(travel,i_task):
    # takes arguments the travel (origin-destination) and the index of the task we want to add
    #return the minimal time the task i_task will start 
    i_depart=travel[0][0]
    t_depart=travel[0][1]
    return int(t_depart+ new_tasks[i_depart].TaskDuration + trajet(new_tasks[i_depart],new_tasks[i_task])+1)


def travel_time_possible(travel,i_task):
    #takes as an argument the index i_task of a task
    #verifies if adding the task i_task to the travel (origin-destination) is possible
    t_arrivee=travel[1][1]
    if ending_time(travel,i_task)<=t_arrivee:
        return True
    return False

def closest_task(i_departure,i_tasks):
    #takes as an argument the indices i_departure and i_tasks of the departure task and of the tasks 
    #from which we want to get the closest one
    distances={i:trajet(new_tasks[i_departure],new_tasks[i]) for i in i_tasks}
    sorted_d = sorted(distances.items(), key=operator.itemgetter(1))
    return (sorted_d)[0][0]

def add_task_to_route(route,i_task,travel):
    # adds the task i_task to the route just after i_departure
    new_route=[]
    added=False
    for location in route:
        new_route.append(location)
        if location[0]==travel[0][0] and not added:
            new_route.append((i_task,starting_time(travel,i_task))) 
            added=True
    return new_route

def tasks_to_do_list(): #to be modified in the future (adapted to each worker)
    return list(range(number_of_fake_tasks,number_of_tasks+1))

def remove_associated_tasks(tasks_to_do,i_task):
    # to be modified for taking into account the subtasks
    tasks_to_do.remove(i_task)  # modifies the list tasks_to_do by 'effet de bord'

def choose_employee(routes):
    

def populate_routes(routes):
    tasks_to_do=tasks_to_do_list()
    for k in range(1,len(routes)):
        route=routes[k]
        number_of_travels_init=len(route)
        number_of_travels_end=500000 #an arbitrary giant number
        while number_of_travels_end != number_of_travels_init: #while our loop adds travels to our route, we continue it
            number_of_travels_init=len(route)
            travels=travels_in_route(route)
            for travel in travels:
                possible_tasks=[]
                for i_task in tasks_to_do:
                    if travel_time_possible(travel,i_task):
                        possible_tasks.append(i_task)
                        remove_associated_tasks(tasks_to_do,i_task)
                if len(possible_tasks)!=0:
                    closest_possible_task=closest_task(travel[0][0],possible_tasks)
                    route=add_task_to_route(route,closest_possible_task,travel)
            number_of_travels_end=len(route)
        routes[k]=route
    return routes

    
routes=populate_routes(routes)
print('Route: ', routes)

##**************************** adapt our result into previous forms ************************
for i in range(1,number_of_tasks+1):
    for j in range(1,number_of_tasks+1):
        tasks_done=[[] for _ in range(number_of_employees+1)] 
        tasks_done[0]=0
        # we create a list of list, in each 'interior' list,
        #we have the indices of the tasks done by employee k 
        for k in range(1,number_of_employees+1):
            travels_done=travels_in_route(routes[k]) 
            tasks_done[k]=[(travels_done[travel][0][0],travels_done[travel][1][0]) for travel in range(len(travels_done))]
#example for route=[[(1, 480), (13, 482)], [(13, 482), (2, 600)], [(2, 600), (22, 730)], [(22, 730), (28, 795)], [(28, 795), (1, 1080)]]
#tasks_done=[0,[(1, 13), (13, 2), (2, 22), (22, 28), (28, 1)]]

def DELTA_func(i,j,k):
    if (i,j) in tasks_done[k]:
        return 1
    return 0

def T_func(k,i):
    for j in range(1,number_of_tasks+1):
        if DELTA_func(i,j,k)==1:
            index=tasks_done[k].index((i,j))
            return routes[k][index][1]
    return 480

DELTA={(i,j,k): DELTA_func(i,j,k) for i in range(1,number_of_tasks+1)
                                for j in range(1,number_of_tasks+1)
                                for k in range(1,number_of_employees+1)}

T={(k,i): T_func(k,i) for i in range(1,number_of_tasks+1)
                        for k in range(1,number_of_employees+1)}


#****************************   plot  ##************************

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

