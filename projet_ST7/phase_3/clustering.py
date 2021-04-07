import matplotlib.pyplot as plt
from  matplotlib.colors import cnames
import numpy as np
from sklearn.cluster import KMeans
import math
import random

from classes import *
from utils import *
from reading_data import *
from model import *

from gurobipy import *

#parameters  which depends on the instance
lambda_1 = 0.3
lambda_2 = 0.7
lambda_3 = 0.3
lambda_4 = 0.7
normalization_factor = 200 #in order to have the same order of magnitude in the objective function of the model
#to find a pertinent value, you have to plot a and b in the code, look at their value and find the best value for normalization_factor

#global parameters
d_max_between_clusters = 50E3
average_duration_task_done = 100
show_levels = True
show_employees_name = True


def subdivise_problem(country, instance, reduce_unbalancing = True, plotting_solution = False):
    """
    Input :
        country : name of the instance we are considerated (string)
        instance : number of the instance (string)
        reduce_unbalancing : apply the unbalancing algorithm if True (boolean)
        plotting_solution : plot the cluster if True (boolean)

    Output :
        new_employees : tensor of employees affected to the cluster c (new_employees[c] : list of TEmployee)
        new_tasks : tensor of tasks affected to the cluster c (new_tasks[c] : list of TTask)
    """

    #getting the data
    employees, real_tasks = readingData(country,instance)

    number_of_employees = len(employees)-1
    depots = [ TTask(0,employees[k].Latitude, employees[k].Longitude,0,"",employees[k].Level,480,1440,[],0,k) for k in range(1,number_of_employees+1) ]
    employees_unavailabilities = [ TTask(-1,unavailability.Latitude, unavailability.Longitude, unavailability.End-unavailability.Start,"",0,unavailability.Start, unavailability.End,[],0,k)
                                    for k,employee in enumerate(employees) if k != 0
                                    for unavailability in employee.Unavailabilities ]

    tasks = depots + employees_unavailabilities + real_tasks[1:]
    level_max = max(tasks, key = lambda task:task.Level).Level
    data_set = np.dstack( (np.array( [task.X for task in tasks] ), np.array( [task.Y for task in tasks] )) )
    data_set = data_set[0]

    #clustering
    labels, score = dict(), dict()

    for nb_clusters in range( max(1,number_of_employees // 2), number_of_employees * 2 ):
        #k-means
        model = KMeans(nb_clusters, n_init=10).fit(data_set)

        labels[nb_clusters] = model.labels_
        cluster_centers = model.cluster_centers_
        nb_tasks_per_cluster = [ (labels[nb_clusters] == cluster).sum() for cluster in range(nb_clusters) ]
        duration_levels_per_cluster = [ [sum([task.TaskDuration for i,task in enumerate(tasks) if labels[nb_clusters][i] == c and task.Level == l]) for l in range(1, level_max+1)] 
                                    for c in range(nb_clusters) ]
                
        #finding all the useful clusters
        useful_clusters = []
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
                    a = quicksum([ DELTA[(e,c)]*employees[e].Max_working_duration - sum(duration_levels_per_cluster[c][l2-1] for l2 in range(l,level_max+1))                                            
                                    for e in range(1, number_of_employees+1) if employees[e].Level >= l ])            
                    m.addConstr( -V[(c,l)] <= a / (level_max * average_duration_task_done) )
                    m.addConstr( a / (level_max * average_duration_task_done) <= V[(c,l)] )        

        for e in range(1, number_of_employees+1):
            m.addConstr( quicksum( [ DELTA[(e,c)] for c in useful_clusters]) == 1)

        for c in useful_clusters:
            m.addConstr( quicksum( [ DELTA[(e,c)] for e in range(1, number_of_employees+1)]) >= 1) 

        a = quicksum([ V[(c,l)] for l in range(1, level_max+1) ])
        b = quicksum([ d[(e,c)]*DELTA[(e,c)] / normalization_factor for e in range(1, number_of_employees+1) ])

        m.setObjective(quicksum([ lambda_1 * quicksum([ V[(c,l)] for l in range(1, level_max+1) ]) +
                                  lambda_2 * quicksum([ d[(e,c)]*DELTA[(e,c)] / normalization_factor for e in range(1, number_of_employees+1) ])
                                    for c in useful_clusters ]), GRB.MINIMIZE)
        m.update()
        m.optimize()

        if m.status == GRB.INFEASIBLE:
            score[nb_clusters] = math.inf
            continue

        #for normalization_factor
        #print(a.getValue(), b.getValue() )

        for e in range(1,number_of_employees+1):
            labels[nb_clusters][e-1] = np.argmax( np.array( [DELTA[(e,c)].x if c in useful_clusters else 0 for c in range(nb_clusters) ] )  ) 
    
        #reduce unbalancing
        if reduce_unbalancing:
            balancing = {c : sum([ DELTA[(e,c)].x * employees[e].Max_working_duration / average_duration_task_done  
                                        for e in range(1, number_of_employees+1)]) - (labels[nb_clusters] == c).sum() 
                            for c in useful_clusters}  #< 0 : cluster c can provide tasks to others clusters, > 0 : cluster needs somes tasks
            mean_balancing = np.mean(np.array([balance for c,balance in balancing.items() ]))
            balancing = {c : balancing[c] - mean_balancing for c in useful_clusters}  #centered balancing

            for c in useful_clusters:
                #if the cluster c needs some tasks
                if balancing[c] > 0:       
                    #we look for a task in all the tasks 
                    for i,task in enumerate(tasks):
                        #if the task is available 
                        if task.id_employee == 0 and labels[nb_clusters][i] in useful_clusters and balancing[ labels[nb_clusters][i] ] < 0:
                            task_cluster = labels[nb_clusters][i]
                            #distance between the task and the cluster c
                            d_c = min([np.Inf] + [ np.linalg.norm(depots[k].coord - task.coord,axis=0) 
                                            for k,employee in enumerate(employees[1:]) if labels[nb_clusters][k] == c ])
                            #distance between the task and the cluster task_cluster
                            d_task_cluster = min([np.Inf] + [ np.linalg.norm(depots[k].coord - task.coord,axis=0) 
                                                for k,employee in enumerate(employees[1:]) if labels[nb_clusters][k] == task_cluster ])
                            #if the task is better in cluster c than in cluster task_cluster, we change its cluster to c 
                            if d_c < d_task_cluster and d_c < d_max_between_clusters//2:
                                labels[nb_clusters][i] = c
                                balancing[c] -= 1
                                balancing[task_cluster] += 1
            
        #scoring the set of cluster
        balancing = {c : abs( sum([ DELTA[(e,c)].x * employees[e].Max_working_duration / average_duration_task_done  
                                    for e in range(1, number_of_employees+1)]) - (labels[nb_clusters] == c).sum() )
                        for c in useful_clusters }
        average_nb_employee_per_cluster = np.mean(np.array([ (labels[nb_clusters][:number_of_employees+1] == c).sum() - 1 for c in useful_clusters ]))
        score[nb_clusters] = 0.3 * average_nb_employee_per_cluster + 0.7*sum([ balancing[c] for c in useful_clusters] )
        
    #choosing the best set of cluster 
    best_cluster = min(score, key=score.get)

    #we must have the unavaibilities of an employee in his cluster
    for i,task in enumerate(tasks):
        if task.id_employee != 0:
            labels[best_cluster][i] = labels[best_cluster][task.id_employee-1] 

    #plot
    if plotting_solution:
        colors = ['red','green','blue','violet','gray','magenta'] + [key for key,c in cnames.items()]
        fig, ax = plt.subplots()

        for i,task in enumerate(tasks):
            if i >= number_of_employees + len(employees_unavailabilities) :
                ax.scatter(task.X,task.Y,color = colors[ labels[best_cluster][i] ])  
                if show_levels:
                    ax.annotate(task.TaskDuration, (task.X, task.Y))   

        for i,task in enumerate(employees_unavailabilities):
                ax.scatter(task.X,task.Y,marker = 'D',color = colors[labels[best_cluster][i + number_of_employees] ]) 

        for i,depot in enumerate(depots):
            ax.scatter(depot.X,depot.Y,marker='X',color = colors[ labels[best_cluster][i] ])
            if show_employees_name:
                ax.annotate( employees[i+1].EmployeeName, (depot.X, depot.Y))  

        plt.axis("equal")
        plt.show()   

    #return the results    
    new_employees = [ [] for cluster in range(best_cluster) ]
    new_tasks = [ [] for cluster in range(best_cluster) ]
    for cluster in range(best_cluster):
        new_tasks[cluster] = [None] + [ task for i,task in enumerate(tasks) if labels[best_cluster][i] == cluster]
        new_employees[cluster] = [None] + [employee for k,employee in enumerate(employees[1:]) if labels[best_cluster][k] == cluster]

    return new_employees, new_tasks

#example of utilisation

#employees, tasks = subdivise_problem("Columbia", instance = "3", reduce_unbalancing=True, plotting_solution=True)


