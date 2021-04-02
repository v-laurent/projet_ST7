import pandas as pd
import numpy as np
from classes import *
from utils import *
from reading_data import *
import matplotlib.pyplot as plt

#################################################
country = 'Bordeaux'
dossier_txt = 'fichiers_txt_phase2'
version = 'V2ByV2'

def ratio_tache_trajet(country):
    employees,tasks = readingData(country)          # depot is not a task
    employees = employees[1:]
    tasks = tasks[1:]
    number_of_employees = len(employees)
    number_of_tasks = len(tasks) 

    decision = pd.read_csv(f"{dossier_txt}/Solution{country}{version}.txt", sep=';', nrows=number_of_tasks)
    decision = decision[['taskId','performed','employeeName','startTime']]

    work_time_per_employee = [0 for i in range(number_of_employees)]
    travel_time_per_employee = [0 for i in range(number_of_employees)]

    for k in range(number_of_employees):
        employee_name = employees[k].EmployeeName
        tasks_id = decision[decision['employeeName']==employee_name].loc[:,'taskId'].values
        T_i_startTime = decision[decision['employeeName']==employee_name].loc[:,'startTime'].values
        if len(T_i_startTime) == 0:
            continue
        sorted_indices = np.argsort(T_i_startTime)       # indexs of tasks accomplished only by employee k
        for i in range(len(tasks_id)):
            task_number = int(tasks_id[sorted_indices[i]][1:]) -1
            work_time_per_employee[k] += tasks[task_number].TaskDuration
            if i == 0 :
                travel_time_per_employee[k] += trajet(employees[k], tasks[task_number])
            else :
                travel_time_per_employee[k] += trajet(tasks[task_number_prec], tasks[task_number])

            task_number_prec = task_number  
        travel_time_per_employee[k] += trajet(tasks[task_number], employees[k]) 
        
        if travel_time_per_employee[k] == 0:
            ratio = 0
        else :
            ratio = work_time_per_employee[k]/travel_time_per_employee[k]
        print("le ratio temps tâches/temps trajet pour {} est de ".format(employee_name) + f"{ratio}")
        
    
ratio_tache_trajet(country)
            
