##***************************** Modules

#Modules de structure
from classes import *
from utils import *
from reading_data import *
from model import *
import operator
import random

# Modules de base
import numpy as np
import matplotlib.pyplot as plt
import random
from gurobipy import *

##***************************** Reading Data  ##*********************************

country = "Austria"
employees, tasks = readingData(country)
phase='3'

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
d = { (i,j,k) : distance(new_tasks[i], new_tasks[j])
            for i in range(1, number_of_tasks+1)  
            for j in range(1, number_of_tasks+1)  
            for k in range(1, number_of_employees+1) }
############################## Metaheuristic
## The travels will be reprensented as follows:
## route =[(location1,start_time),(location2,start_time),(location3,start_time), ...]


routes_init=[0,[(1,480),(4,600),(1,1080)],[(2,480),(2,1080)]] 
def travels_in_route(route): 
    '''# allows to create couples of origin-destination 
    #example: with route=[(1,480),(2,600),(1,1080)]
    # travels(route) will return [[(1,480),(2,600)],[(2,600),(1,1080)]]'''
    res=[]
    for i in range(1,len(route)):
        res.append([route[i-1],route[i]])
    return res

def ending_time(travel,i_task):
    '''# takes arguments the travel (origin-destination) and the index of the task we want to add
    #returns the minimal time it will take to reach the destination by going through the task i_task'''
    i_depart=travel[0][0]
    i_arrivee=travel[1][0]
    t_depart=travel[0][1]
    return t_depart+ new_tasks[i_depart].TaskDuration + trajet(new_tasks[i_depart],new_tasks[i_task]) + new_tasks[i_task].TaskDuration + trajet(new_tasks[i_task],new_tasks[i_arrivee])

def ending_time_of_task(travel,i_task):
    '''
    takes arguments the travel (origin-destination) and the index of the task we want to add
    returns the minimal time the task i_task will end 
    '''
    i_depart=travel[0][0]
    i_arrivee=travel[1][0]
    t_depart=travel[0][1]
    return t_depart+ new_tasks[i_depart].TaskDuration + trajet(new_tasks[i_depart],new_tasks[i_task]) + new_tasks[i_task].TaskDuration

def starting_time(travel,i_task):
    '''# takes arguments the travel (origin-destination) and the index of the task we want to add
    #returns the minimal time the task i_task will start '''
    i_depart=travel[0][0]
    t_depart=travel[0][1]
    return int(t_depart+ new_tasks[i_depart].TaskDuration + trajet(new_tasks[i_depart],new_tasks[i_task])+1)


def travel_time_possible(travel,i_task):
    '''#takes as an argument the index i_task of a task
    #verifies if adding the task i_task to the travel (origin-destination) is possible'''
    t_arrivee=travel[1][1]
    if ending_time(travel,i_task)<=t_arrivee:
        if starting_time(travel,i_task)>=new_tasks[i_task].OpeningTime:
            if ending_time_of_task(travel,i_task)<=new_tasks[i_task].ClosingTime:
                return True
    return False
def travel_time_possible_lunch(travel,i_task):
    '''#takes as an argument the index i_task of a task
    verifies if adding the task i_task to the travel (origin-destination) and taking a lunch 
    break there is possible is possible'''
    t_arrivee=travel[1][1]
    if ending_time(travel,i_task) + 60 <=t_arrivee:
        if starting_time(travel,i_task)>=new_tasks[i_task].OpeningTime:
            if ending_time_of_task(travel,i_task)<=new_tasks[i_task].ClosingTime:
                return True
    return False

    

def level_possible(employee,i_task):
    '''
    takes as arguments the index of an employee and the index of a task
    returns True or False if the employee is skilled enough to do the task
    '''
    if employees[employee].Level >= new_tasks[i_task].Level:
        return True
    return False

def closest_task(i_departure,i_tasks,k,need_to_eat=False):
    '''takes as an argument the indices i_departure and i_tasks of the departure task and of the tasks 
    from which we want to get a linear combination of the closest one and the ones for which the 
    employee is not too much over-capable'''
    distances={i:trajet(new_tasks[i_departure],new_tasks[i]) for i in i_tasks}
    somme=0
    for i in distances:
        somme+=distances[i]
    moyenne=somme/len(distances)
    delta_levels={i:employees[k].Level-new_tasks[i].Level for i in i_tasks}
    if need_to_eat:
        return 2
    else:
        choice={i: distances[i] + delta_levels[i] for i in i_tasks }
        sorted_d = sorted(choice.items(), key=operator.itemgetter(1))
        return (sorted_d)[0][0]

def add_task_to_route(route,i_task,travel,to_eat):
    ''' adds the task i_task to the route just after the task travel[0][0] (the index of the deparature) '''
    new_route=[]
    added=False
    for location in route:
        new_route.append(location)
        if location[0]==travel[0][0] and not added:
            new_route.append((i_task,starting_time(travel,i_task)))
            if to_eat:
                new_tasks[i_task].TaskDuration+=60 
            added=True
    return new_route

def tasks_to_do_list(): 
    '''to be modified in the future (adapted to each worker)'''
    return list(range(number_of_fake_tasks+1,number_of_tasks+1))

def remove_associated_tasks(tasks_to_do,i_task):
    '''
     takes as arguments the list of tasks_to_do and the index of the task to remove
     modifies by the list tasks_to_do in place ('effet de bord')
     '''
    id_of_task=new_tasks[i_task].TaskId
    id_of_task=new_tasks[i_task].TaskId
    tasks_to_remove=[]
    for indices in range(1,number_of_tasks+1):
        if new_tasks[indices].TaskId==id_of_task:
            tasks_to_remove.append(indices)
    for task in tasks_to_remove:
        tasks_to_do.remove(task)

def choose_employee(routes,excluded_employees=[]):
    '''
    take as arguments the routes of all the employees and a list containing all the employees to
     whom we cannot affect tasks anymore
    '''  
    worked_times_dict=dict()
    possible_employees=list(range(1,number_of_employees+1))
    for element in excluded_employees:
        possible_employees.remove(element)
    if len(possible_employees)==0:
        return False
    for employee in possible_employees:
        sum_employee=0
        for task_done in routes[employee]:
            sum_employee+=new_tasks[task_done[0]].TaskDuration
            worked_times_dict[employee]=sum_employee
    sorted_wtd=sorted(worked_times_dict.items(),key=operator.itemgetter(1))
    return sorted_wtd[0][0]

def duree_max_tache(new_tasks):
    durees=[]
    for task in range(1,number_of_tasks+1):
        durees.append(new_tasks[task].TaskDuration)
    return max(durees)
def initialize_routes():
    res=[0]+[[] for employee in range(number_of_employees)]
    number_of_unavailabilities=[]
    for employee in range(1,number_of_employees+1):
        res[employee].append((employee,employees[employee].WorkingStartTime))
        number_of_unavailabilities_k=len(employees[employee].Unavailabilities)
        number_of_unavailabilities.append(number_of_unavailabilities_k)
        if number_of_unavailabilities_k!=0: #if the employee has unavailabilities
            for i_unavailability in range(number_of_unavailabilities_k):
                res[employee].append((number_of_employees+sum(number_of_unavailabilities),employees[employee].Unavailabilities[i_unavailability].Start))
        res[employee].append((employee,employees[employee].WorkingEndTime))
    return res
def populate_routes(routes):
    '''
    deprecated first version non adapted to the sub-tasks, the levels, the lunch break, and to the clustering
    '''
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
                    closest_possible_task=closest_task(travel[0][0],possible_tasks,k)
                    route=add_task_to_route(route,closest_possible_task,travel)
            number_of_travels_end=len(route)
        routes[k]=route
    return routes

def populate_routes_V2(routes):
    tasks_to_do=tasks_to_do_list()
    excluded_employees=[]
    k=choose_employee(routes,excluded_employees)
    P=[0]+[False for i in range(number_of_employees)]
    while k != False:
        route=routes[k]
        init_nb_of_travels=len(route)
        travels=travels_in_route(route)
        nb_travels=len(travels)
        travels_indexlist=list(range(nb_travels))
        random.shuffle(travels_indexlist)
        for i_travel in travels_indexlist:
            travel=travels[i_travel]
            possible_tasks=[]
            for i_task in tasks_to_do:
                #end_time_of_task=ending_time_of_task(travel, i_task)
                if level_possible(k,i_task):
                    if travel_time_possible(travel,i_task):
                            possible_tasks.append(i_task)
            if len(possible_tasks)!=0:
                closest_possible_task=closest_task(travel[0][0],possible_tasks,k)
                #to_eat= P[k]==closest_possible_task
                route=add_task_to_route(route,closest_possible_task,travel,False)
                remove_associated_tasks(tasks_to_do,closest_possible_task)
                #end_time_of_task=ending_time_of_task(travel,closest_possible_task)
        routes[k]=route
        if init_nb_of_travels == len(route):
            excluded_employees.append(k) 
        k=choose_employee(routes,excluded_employees)           
    return routes,P

# routes=populate_routes(routes_init)
routes_init=initialize_routes()
print('--------------------------------------------------------------------------------')
print(routes_init)
routes,P_brut=populate_routes_V2(routes_init)
print('Route 2:', routes)
print('P_brut: ', P_brut)

def distances():
    res=[0 for k in range(number_of_employees+1)]
    for k in range(1,len(routes)):
        travels=travels_in_route(routes[k])
        for j in travels:
            res[k]+=distance(new_tasks[j[0][0]],new_tasks[j[1][0]])
    return res
def nb_of_real_tasks_done():
    res=[0 for k in range(number_of_employees+1)]
    routes_init=initialize_routes()
    for k in range(1,len(routes)):
        res[k]=len(routes[k])-len(routes_init[k])
    return res
l1= 0.0002 
l2= 0.5

def objective_function():
    somme=0
    distances_tab=distances()
    nb_of_tasks_done_tab=nb_of_real_tasks_done()
    for k in range(1,number_of_employees):
        somme-=l1*distances_tab[k]
        somme+=l2*nb_of_tasks_done_tab[k]
    return somme



print('------------------------------Calcul de la fonction objectif-------------------')
print(distances())
print(nb_of_real_tasks_done())
print(objective_function())


##**************************** adapt our result into previous forms ************************
# creating couples of (origin-destination) tasks in the variable tasks_done 
# (it is useful for creating DELTA)
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

def P_func(k,i):
    if P_brut[k]==i:
            return True
    return False

DELTA={(i,j,k): DELTA_func(i,j,k) for i in range(1,number_of_tasks+1)
                                for j in range(1,number_of_tasks+1)
                                for k in range(1,number_of_employees+1)}

T={(k,i): T_func(k,i) for i in range(1,number_of_tasks+1)
                        for k in range(1,number_of_employees+1)}

P={(k,i): P_func(k,i) for i in range(1,number_of_tasks+1)
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

draw(employees,tasks,latitudes,longitudes,task_numbers,country+'_gmplot_glouton.html',DELTA,phase)
fichier_texte(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance)
