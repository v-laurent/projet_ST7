import pandas as pd
import numpy as np
import plotly.express as px
from os.path import dirname
country = "Poland"

def gantt(country):
    #j'arrivais pas à utiliser correctement les fonctions importées de reading_data, j'ai donc recopié et raccourci
    current_dir = dirname(__file__)
    file = current_dir + "/" + country + ".txt"
    decision = pd.read_csv(file, sep=';')
    decision = decision[['taskId','performed','employeeName','startTime']]
    file_path = current_dir + "/InstancesV1/Instance" + country + "V1.xlsx"
    xls = pd.ExcelFile(file_path)

    #employees
    employees_sheet = pd.read_excel(xls, 'Employees')
    employees = []
    for index, row in employees_sheet.iterrows():
        employees.append(row["EmployeeName"])
        
    #tasks
    task_sheet = pd.read_excel(xls, 'Tasks')
    task_duration = []
    for index, row in task_sheet.iterrows():
        task_duration.append(row["TaskDuration"])
    
    contenu = []
    for employee in employees :
        for i in range(len(decision)):
            if decision.iloc[i][1] == 1 and employee == decision.iloc[i][2]:
                start = decision.iloc[i][3]
                taskduration = task_duration[i]
                s_hour = int(start//60)
                if s_hour < 10 :
                    s_hour = str(0)+str(s_hour)
                s_minute = int(start%60)
                if s_minute < 10 :
                    s_minute = str(0) + str(s_minute)
                e_hour = int((start+taskduration)//60)
                if e_hour < 10 :
                    e_hour = str(0) + str(e_hour)
                e_minute = int((start+taskduration)%60)
                if e_minute < 10 :
                    e_minute = str(0) + str(e_minute)
                taskname = decision.iloc[i][0]
                contenu.append(dict(Task="{}".format(taskname), Start='2020-03-10 {}:{}'.format(s_hour,s_minute), Finish='2020-03-10 {}:{}'.format(e_hour,e_minute), Resource = employee))
    tab = pd.DataFrame(contenu)
    fig = px.timeline(tab, x_start="Start", x_end="Finish", y="Resource", text = "Task", title = "Planning Journée")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title_font_size = 40, font_size= 20)
    fig.show()          

gantt(country)