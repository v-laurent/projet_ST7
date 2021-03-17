import pandas as pd
import numpy as np
from classes import *
from utils import *
from reading_data import *
import matplotlib.pyplot as plt

######################################
country = 'Bordeaux'
dossier_txt = 'utils.py_phase1'
######################################


def verification(country, epsilon=0.05):
    employees,tasks = readingData(country)          # le dépôt n'est pas dans les tâches
    number_of_employees = len(employees)
    number_of_tasks = len(tasks)
    fig1,gnt=plt.subplots()
    gnt.set_yticks([10*(y+1) for y in range(len(employees))])
    gnt.set_ylim(0,10*len(employees)+7)
    gnt.set_xlim(475, 1085)
    gnt.set_xlabel('Temporal evolution')
    
    gnt.set_yticklabels(['{}'.format(employee.EmployeeName) for employee in employees])
    
    gnt.grid(True)
    
    task_times=[[] for _ in range(len(employees))]
    travel_times=[[] for _ in range(len(employees))]
    decision = pd.read_csv(f"{dossier_txt}/{country}.txt", sep=';')
    decision = decision[['taskId','performed','employeeName','startTime']]

    # Pourcentage de tâches réalisées
    print("Pourcentage de tâches réalisées : {} %".format(decision['performed'].sum()/number_of_tasks*100))

    # Contraintes
    for i in range(0, number_of_tasks):
        task_id = tasks[i].TaskId
        T_i_startTime = decision[decision['taskId']==task_id].loc[:,'startTime'].values
        # vérification que la tâche Ti est faite
        if len(decision[decision['taskId']==task_id].loc[:,'performed'].values) == 0:
            print(f"ERREUR : ligne de la tâche {task_id} manquante")
            break
        if decision[decision['taskId']==task_id].loc[:,'performed'].values == 0:
            print(f"Tâche {task_id} non réalisée")
            break
        employee_name = decision[decision['taskId']==task_id].loc[:,'employeeName'].values[0]
        k=0
        while employees[k].EmployeeName != employee_name:
            k+=1
        # 1- disponibilité des tâches
        if T_i_startTime < tasks[i].OpeningTime:
            print(f"ERREUR 1.1 : tâche {task_id} réalisée par {employee_name} avant l'ouverture de la tâche.")
        if T_i_startTime > tasks[i].ClosingTime:
            print(f"ERREUR 1.2 : tâche {task_id} réalisée par {employee_name} après la fermeture de la tâche.")
        if T_i_startTime > tasks[i].ClosingTime - tasks[i].TaskDuration:
            print(f"ERREUR 1.3 : tâche {task_id} réalisée par {employee_name} trop proche de la fermeture de la tâche.")
        
        # 2- disponibilité des employés
        if T_i_startTime < employees[k].WorkingStartTime:
            print(f"ERREUR 2.1 : tâche {task_id} réalisée par {employee_name} avant le début de son service.")
        if T_i_startTime > employees[k].WorkingEndTime:
            print(f"ERREUR 2.2 : tâche {task_id} réalisée par {employee_name} après la fin de son service.")
        if T_i_startTime > employees[k].WorkingEndTime - tasks[i].TaskDuration - trajet(tasks[i],employees[k]):
            print(f"ERREUR 2.3 : tâche {task_id} réalisée par {employee_name} trop proche de la fin de son service.")

        # 3- compétences
        if employees[k].Skill != tasks[i].Skill:
            print(f"ERREUR 3.1 : compétence {employees[k].Skill} manquante")
        else :
            if employees[k].Level < tasks[i].Level:
                print(f"ERREUR 3.2 : compétence n°{tasks[k].Skill} de niveau {tasks[i].Level} requis par {employee_name} (niveau {employees[k].Level} appris)")

    # Vérification du trajet des employés
    for k in range(number_of_employees):
        employee_name = employees[k].EmployeeName
        tasks_id = decision[decision['employeeName']==employee_name].loc[:,'taskId'].values
        tasks_startTime = decision[decision['employeeName']==employee_name].loc[:,'startTime'].values
    
        if len(tasks_startTime) == 0:
            print(f"{employee_name} n'effectue aucune tâche")
            break
        sorted_indices = np.argsort(tasks_startTime)        # indices uniquement des tâches effectuées par le technicien k
        sorted_indices_bis = []                             # utilisables sur tasks (ensemble de toutes les tâches)
        for i in sorted_indices:
            for j in range(number_of_tasks):
                if tasks[j].TaskId == tasks_id[i]:
                    sorted_indices_bis.append(j)
        end_times=[]
        for task in range(len(tasks_id)):
            task_times[k].append((tasks_startTime[task],tasks[int(tasks_id[task].strip('T'))-1].TaskDuration))
            gnt.annotate(tasks_id[task], (tasks_startTime[task], 10*(k+1)-1))
            end_times.append(tasks_startTime[task]+tasks[int(tasks_id[task].strip('T'))-1].TaskDuration)
        end_times=sorted(end_times)
        travel_times[k].append((employees[k].WorkingStartTime,trajet(employees[k],tasks[sorted_indices_bis[0]])))
        for i in range(len(sorted_indices_bis)-1):
            if i==len(sorted_indices_bis)-1:
                break
            print("{} vers {}".format(tasks[sorted_indices_bis[i]].TaskId,tasks[sorted_indices_bis[i+1]].TaskId))
            print("{}".format(trajet(tasks[sorted_indices_bis[i]],tasks[sorted_indices_bis[i+1]])))
            travel_times[k].append((end_times[i],trajet(tasks[sorted_indices_bis[i]],tasks[sorted_indices_bis[i+1]])))
            #print(end_times[i-1])
            #print(end_times[i]+trajet(tasks[sorted_indices_bis[i]],tasks[sorted_indices_bis[i+1]]))
        travel_times[k].append((end_times[-1],trajet(employees[k],tasks[sorted_indices_bis[-1]])))
        

        
        # 4- trajet dépôt / première tâche
        i0 = sorted_indices[0]
        i0_bis = sorted_indices_bis[0]
        eps = tasks_startTime[i0] - (employees[k].WorkingStartTime + trajet(employees[k], tasks[i0_bis]))
        if eps < 0:
            print(f"ERREUR 4.1 : {employee_name} part du dépôt trop tôt")
        else:
            if eps > epsilon:
                print(f"warning 4.2 : {employee_name} part du dépôt {round(eps,2)}min trop tard")
        
        # 5- temporalité des tâches
        for i in range(1,len(sorted_indices)):
            i1 = sorted_indices[i-1]
            i2 = sorted_indices[i]
            i1_bis = sorted_indices_bis[i-1]
            i2_bis = sorted_indices_bis[i]
            eps = tasks_startTime[i2] - (tasks_startTime[i1] + tasks[i1_bis].TaskDuration + trajet(tasks[i1_bis],tasks[i2_bis]))
            if eps < 0:
                print(f"ERREUR 5.1 : {employee_name} commence la tâche {tasks_id[i2]} trop tôt par rapport à la tâche précédente {tasks_id[i1]}")            
            else:
                if eps > epsilon:
                    print(f"warning 5.2 : {employee_name} met {round(eps,2)}min de trop pour aller de la tâche {tasks_id[i2]} à la tâche {tasks_id[i1]}")
        # 6- trajet dernièrer tâche / dépôt
        iN = sorted_indices[-1]
        iN_bis = sorted_indices_bis[-1]
        if tasks_startTime[iN] > employees[k].WorkingEndTime - trajet(tasks[iN_bis], employees[k]):
            print(f"ERREUR 6.1 : {employee_name} revient au dépôt trop tard")
    colors=['green','orange','blue']
    for i in range(len(employees)):
        gnt.broken_barh(task_times[i],(10*(i+1)-1,2), facecolors=('tab:{}'.format(colors[i])))
        gnt.broken_barh(travel_times[i],(10*(i+1)-2,0.5),facecolors=('tab:red'))
    
        #gnt.broken_barh([(tasks[task].OpeningTime,100)],(10*(len(employees)+(task+1))-1,0.5),facecolors=('tab:blue'))
    plt.savefig('{}.png'.format(country))
    fig2,blab=plt.subplots()
    blab.set_ylim(0,10*len(tasks)+10)
    fig2.suptitle('{}_tasks'.format(country))
    blab.set_xlim(475, 1085)
    blab.set_xlabel('Temporal evolution')
    blab.set_yticks([10*(y+1) for y in range(len(tasks))])
    blab.set_yticklabels(['{}'.format(task.TaskId) for task in tasks])
    blab.grid(True)
    for task in range(len(tasks)):
        print(tasks[task].OpeningTime)
        print(tasks[task].ClosingTime-tasks[task].OpeningTime)
        blab.broken_barh([(tasks[task].OpeningTime,tasks[task].ClosingTime-tasks[task].OpeningTime)],(10*(task+1)-1,2),facecolors=('tab:blue'))
    plt.savefig('{}_tasks.png'.format(country))

verification(country)