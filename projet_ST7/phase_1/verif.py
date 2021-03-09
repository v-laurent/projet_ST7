import pandas as pd
import numpy as np
from classes import *
from utils import *
from reading_data import *


def verification(country):
    employees,tasks = readingData(country)          # le dépôt n'est pas dans les tâches
    number_of_employees = len(employees)
    number_of_tasks = len(tasks)

    decision = pd.read_csv(f"{country}.txt", sep=';')
    decision = decision[['taskId','performed','employeeName','startTime']]

    # Pourcentage de tâches réalisées
    print("Pourcentage de tâches réalisées : {} %".format(decision['performed'].sum()/number_of_tasks*100))

    # Contraintes
    for i in range(0, number_of_tasks):
        task_id = tasks[i].TaskId
        T_i_startTime = decision[decision['taskId']==task_id].loc[:,'startTime'].values
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
        sorted_indices = np.argsort(tasks_startTime)        # indices uniquement des tâches effectuées par le technicien k
        sorted_indices_bis = []                             # utilisables sur tasks (ensemble de toutes les tâches)
        for i in sorted_indices:
            for j in range(number_of_tasks):
                if tasks[j].TaskId == tasks_id[i]:
                    sorted_indices_bis.append(j)

        # 4- trajet dépôt / première tâche
        i0 = sorted_indices[0]
        i0_bis = sorted_indices_bis[0]
        if tasks_startTime[i0] < employees[k].WorkingStartTime + trajet(employees[k], tasks[i0_bis]):
            print(f"ERREUR 4.1 : {employee_name} part du dépôt trop tôt")
        else:
            eps = tasks_startTime[i0] - (employees[k].WorkingStartTime + trajet(employees[k], tasks[i0_bis]))
            if eps > 0:
                print(f"ERREUR 4.2 : {employee_name} part du dépôt {round(eps,2)}min trop tard")
        
        # 5- temporalité des tâches
        for i in range(1,len(sorted_indices)):
            i1 = sorted_indices[i-1]
            i2 = sorted_indices[i]
            i1_bis = sorted_indices_bis[i-1]
            i2_bis = sorted_indices_bis[i]
            if tasks_startTime[i2] < tasks_startTime[i1] + tasks[i1_bis].TaskDuration + trajet(tasks[i1_bis],tasks[i2_bis]):
                print(f"ERREUR 5.1 : {employee_name} commence la tâche {tasks_id[i2]} trop tôt par rapport à la tâche précédente {tasks_id[i1]}")            
            else:
                eps = tasks_startTime[i2] - (tasks_startTime[i1] + tasks[i1_bis].TaskDuration + trajet(tasks[i1_bis],tasks[i2_bis]))
                if eps !=0:
                    print(f"ERREUR 5.2 : {employee_name} met {round(eps,2)}min de trop pour aller de la tâche {tasks_id[i2]} à la tâche {tasks_id[i1]}")

        # 6- trajet dernièrer tâche / dépôt
        iN = sorted_indices[-1]
        iN_bis = sorted_indices_bis[-1]
        if tasks_startTime[iN] > employees[k].WorkingEndTime - trajet(tasks[iN_bis], employees[k]):
            print(f"ERREUR 6.1 : {employee_name} revient au dépôt trop tard")
        


verification("bordeaux")