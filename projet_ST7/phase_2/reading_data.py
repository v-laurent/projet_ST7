from os.path import dirname
import pandas as pd
from utils import *
from classes import *


def readingData(country):

    current_dir = dirname(__file__)
    file_path = current_dir + "/InstancesV2/Instance" + country + "V2.xlsx"
    xls = pd.ExcelFile(file_path)


    #employees
    employees_sheet = pd.read_excel(xls, 'Employees')
    skillToRank = {skill : i for i,skill in enumerate( set(employees_sheet["Skill"]) )}
    employee_to_rank = {employee_name : i+1 for i,employee_name in enumerate( set(employees_sheet["EmployeeName"]) )}
    skillToRank['other'] = len(skillToRank)
    employees = [None]  ## in order to begin index at 1, rather than 0
    
    for index, row in employees_sheet.iterrows():
        workingStartTime = dateToMinute( row["WorkingStartTime"] )
        workingEndTime = dateToMinute( row["WorkingEndTime"] )
        skill = skillToRank[ row["Skill"] ]
        employees.append( TEmployee(row["EmployeeName"], row["Latitude"], row["Longitude"], skill, row["Level"], workingStartTime, workingEndTime, [] ) )



     #employees_unavailabilities
    employees_unavailabilities_sheet = pd.read_excel(xls, 'Employees Unavailabilities')
    
    for index, row in employees_unavailabilities_sheet.iterrows():
        Start = dateToMinute( row["Start"] )
        End = dateToMinute( row["End"] )
        unavailability = TUnavailability(row["Latitude"], row["Longitude"], Start, End)
        employees[ employee_to_rank[ row["EmployeeName"] ]].Unavailabilities.append(unavailability)



    #tasks
    task_sheet = pd.read_excel(xls, 'Tasks')
    task_to_rank = {task : i+1 for i,task in enumerate( set(task_sheet["TaskId"]) )}
    tasks = [None]  ## in order to begin index at 1, rather than 0
    for index, row in task_sheet.iterrows():
        openingTime = dateToMinute( row["OpeningTime"] )
        closingTime = dateToMinute( row["ClosingTime"] )
        if row["Skill"] in skillToRank.keys(): 
            skill = skillToRank[ row["Skill"] ] 
        else: 
            skill = skillToRank["other"]
        tasks.append( TTask(row["TaskId"], row["Latitude"], row["Longitude"], row["TaskDuration"], skill, row["Level"], openingTime, closingTime, [], 0, 0) )
    

       #tasks_unavailabilities
    task_unavailabilities_sheet = pd.read_excel(xls, 'Tasks Unavailabilities')
    for index, row in task_unavailabilities_sheet.iterrows():
        Start = dateToMinute( row["Start"] )
        End = dateToMinute( row["End"] )
        unavailability = TUnavailability(0,0, Start, End)
        tasks[ task_to_rank[ row["TaskId"] ] ].Unavailabilities.append(unavailability)
    
    return employees, tasks