import pandas as pd
import numpy as np
from classes import *
from utils import *
from reading_data import *
import matplotlib.pyplot as plt

#################################################
#confusion phase-instance à corrigier au cas par cas..
country = 'Ukraine'
phase = '3'
instance = '2'
version = f'V{instance}byV{phase}'
def solution_analysis(country):
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = directory + os.sep + "fichiers_txt_phase" + phase
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    
    titre = "AnalysisSolution"+country+"V"+instance+"ByV"+phase
    texte = open(f'{titre}.csv','w')

    employees,tasks = readingData(country)          # depot is not a task
    employees = employees[1:]
    tasks = tasks[1:]
    number_of_employees = len(employees)
    number_of_tasks = len(tasks) 

    decision = pd.read_csv(f"{directory}/Solution{country}{version}.txt", sep=';', nrows=number_of_tasks)
    decision = decision[['taskId','performed','employeeName','startTime']]

    work_time_per_employee = [0 for i in range(number_of_employees)]
    travel_time_per_employee = [0 for i in range(number_of_employees)]
    table = [['employeeName', 'timeWorking', 'timeTravelling', 'ratio', 'numberOfTasks']]

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
        table.append([employee_name, work_time_per_employee[k], travel_time_per_employee[k], ratio, len(tasks_id)])
    for line in table:
        texte.write("{};{};{};{};{};\n".format(line[0],line[1],line[2],line[3],line[4]))

          
solution_analysis(country)
            

