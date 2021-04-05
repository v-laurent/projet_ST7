import matplotlib.pyplot as plt
from classes import *
from utils import *
from reading_data import *
from model import *
import numpy as np
from sklearn.cluster import KMeans
import math
import random
from gurobipy import *

""" idées

rajouter niveau et temps de travail disponible : done


"""

#parameters
d_max_between_clusters = 50E3
lambda_1 = 0.7
lambda_2 = 0.3
average_duration_task_done = 100
show_levels = True

#reading data
country = "Poland"
employees, tasks = readingData(country)
number_of_employees = len(employees)-1
depots = [ TTask(0,employees[k].Latitude, employees[k].Longitude,0,"",employees[k].Level,480,1440,[],0,k) for k in range(1,number_of_employees+1) ]
employees_unavailabilities = [ TTask(-1,unavailability.Latitude, unavailability.Longitude, unavailability.End-unavailability.Start,"",0,unavailability.Start, unavailability.End,[],0,k)
                                for k,employee in enumerate(employees) if k != 0
                                for unavailability in employee.Unavailabilities ]

tasks = depots + employees_unavailabilities + tasks[1:]

level_max = max(tasks, key = lambda task:task.Level).Level

#clustering
data_set = np.dstack( (np.array( [task.X for task in tasks] ), np.array( [task.Y for task in tasks] )) )
data_set = data_set[0]
labels = dict()
score = dict()

for nb_clusters in range( math.ceil(number_of_employees / 2), number_of_employees * 2 ):
    model = KMeans(nb_clusters, n_init=10).fit(data_set)

    #post treatment
    labels[nb_clusters] = model.labels_
    cluster_centers = model.cluster_centers_
    useful_clusters = []

    nb_tasks_per_cluster = [ (labels[nb_clusters] == cluster).sum() for cluster in range(nb_clusters) ]
    nb_levels_per_cluster = [ [sum([1 for i,task in enumerate(tasks) if labels[nb_clusters][i] == c and task.Level == l]) for l in range(1, level_max+1)] 
                                for c in range(nb_clusters) ]
            

    for cluster in range(nb_clusters):
        if not cluster in labels[nb_clusters][:number_of_employees]:
            id_nearest_depot = np.argmin( [ np.linalg.norm(model.cluster_centers_[cluster] - depot.coord,axis=0) for depot in depots]  )
            d_min = np.linalg.norm(model.cluster_centers_[cluster] - depots[id_nearest_depot].coord,axis=0)
            if d_min <= d_max_between_clusters:
                useful_clusters.append(cluster)
        else:
            useful_clusters.append(cluster)

    #model
    m = Model('clustering_{}'.format(nb_clusters))
    m.setParam('OutputFlag', 0)

    DELTA = { (e,c) : m.addVar(vtype=GRB.BINARY, name=f'DELTA_{e}_{c}') 
                for e in range(1, number_of_employees+1)
                for c in useful_clusters }

    V = { (c,l) : m.addVar(vtype=GRB.CONTINUOUS, name=f'V_{c}_{l}')
                for l in range(1, level_max+1) 
                for c in useful_clusters }

    d = { (e,c) : np.linalg.norm(model.cluster_centers_[c] - depots[e-1].coord,axis=0)
                for e in range(1, number_of_employees+1)
                for c in useful_clusters }   

    d_max = max([dist for key,dist in d.items()]) 

    for e in range(1, number_of_employees+1):
        for c in useful_clusters:
            for l in range(1,level_max+1):
                a = quicksum([ DELTA[(e,c)]*(employees[e].Max_working_duration/average_duration_task_done) - sum(nb_levels_per_cluster[c][l2-1] for l2 in range(l,level_max+1))                                            
                                for e in range(1, number_of_employees+1) if employees[e].Level >= l ])            
                m.addConstr( -V[(c,l)] <= a )
                m.addConstr( a <= V[(c,l)] )        

    for e in range(1, number_of_employees+1):
        m.addConstr( quicksum( [ DELTA[(e,c)]*d[(e,c)] for c in useful_clusters]) <= d_max_between_clusters)
        m.addConstr( quicksum( [ DELTA[(e,c)] for c in useful_clusters]) == 1)

    for c in useful_clusters:
        m.addConstr( quicksum( [ DELTA[(e,c)] for e in range(1, number_of_employees+1)]) >= 1) 

    m.setObjective(quicksum([ lambda_1 * quicksum([ V[(c,l)] / max(1, nb_levels_per_cluster[c][l-1]) for l in range(1, level_max+1) ]) +
                              lambda_2 * quicksum([ d[(e,c)]*DELTA[(e,c)] / d_max for e in range(1, number_of_employees+1) ])
                                for c in useful_clusters ]), GRB.MINIMIZE)
    m.update()
    m.optimize()

    if m.status == GRB.INFEASIBLE:
        score[nb_clusters] = math.inf
        continue

    for e in range(1,number_of_employees+1):
        labels[nb_clusters][e-1] = np.argmax( np.array( [DELTA[(e,c)].x for c in useful_clusters] )  ) 

    average_nb_employee_per_cluster = np.mean(np.array([ (labels[nb_clusters][:number_of_employees+1] == c).sum() - 1 for c in useful_clusters ]))
    balancing = {c : abs( sum([ DELTA[(e,c)].x * employees[e].Max_working_duration / average_duration_task_done  
                                for e in range(1, number_of_employees+1)]) - (labels[nb_clusters] == c).sum() )
                    for c in useful_clusters}

    score[nb_clusters] = 0.3 * average_nb_employee_per_cluster + 0.7*sum([ balancing[c] for c in useful_clusters] )
    """
    print("nb_cluster = {}".format(nb_clusters))
    print(" average_nb_employee_per_cluster : {}".format(average_nb_employee_per_cluster))
    print(" balancing : {}".format(balancing))
    print(" score : {}".format(score[nb_clusters]))
    """
#best cluster
best_cluster = min(score, key=score.get)


#plot
colors = ['red','green','blue','violet','gray','magenta']

fig, ax = plt.subplots()

for i,task in enumerate(tasks):
    if i >= number_of_employees + len(employees_unavailabilities):
        ax.scatter(task.X,task.Y,color = colors[labels[best_cluster][i] ])  
        if show_levels:
            ax.annotate(task.Level, (task.X, task.Y))     

for i,task in enumerate(employees_unavailabilities):
        ax.scatter(task.X,task.Y,marker = 'D',color = colors[labels[best_cluster][i + number_of_employees] ]) 


for i,depot in enumerate(depots):
    ax.scatter(depot.X,depot.Y,marker='x',color = colors[labels[best_cluster][i] ])
    if show_levels:
        ax.annotate(employees[depot.id_employee].EmployeeName, (depot.X, depot.Y))  

plt.axis("equal")
plt.show()