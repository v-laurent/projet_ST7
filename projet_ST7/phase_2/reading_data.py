from os.path import dirname
import pandas as pd
from utils import *
from classes import *


def readingData(country):

    current_dir = dirname(__file__)
    file_path = current_dir + "/InstancesV2/Instance" + country + "V2.xlsx"
    xls = pd.ExcelFile(file_path)

    #employees_unavailabilities
    employees_unavailabilities_sheet = pd.read_excel(xls, 'Employees Unavailabilities')
    employees_unavailabilities = {}
    
    for index, row in employees_unavailabilities_sheet.iterrows():
        Start = dateToMinute( row["Start"] )
        End = dateToMinute( row["End"] )
        employees_unavailabilities[row["EmployeeName"]]= [TUnavalaibility (row["Latitude"], row["Longitude"], Start, End )]

    #employees
    employees_sheet = pd.read_excel(xls, 'Employees')
    skillToRank = {skill : i for i,skill in enumerate( set(employees_sheet["Skill"]) )}
    skillToRank['other'] = len(skillToRank)
    employees = [0]  ## in order to begin index at 1, rather than 0
    
    for index, row in employees_sheet.iterrows():
        workingStartTime = dateToMinute( row["WorkingStartTime"] )
        workingEndTime = dateToMinute( row["WorkingEndTime"] )
        skill = skillToRank[ row["Skill"] ]
        if row["EmployeeName"] in employees_unavailabilities:  ## if the employee is unavailable
            employees.append( TEmployee(row["EmployeeName"], row["Latitude"], row["Longitude"], skill, row["Level"], workingStartTime, workingEndTime, employees_unavailabilities[row["EmployeeName"]]) )
        else:
            employees.append( TEmployee(row["EmployeeName"], row["Latitude"], row["Longitude"], skill, row["Level"], workingStartTime, workingEndTime, [] ) )

      #tasks_unavailabilities
    task_unavailabilities_sheet = pd.read_excel(xls, 'Tasks Unavailabilities')
    tasks_unavailabilities = {}
    for index, row in task_unavailabilities_sheet.iterrows():
        Start = dateToMinute( row["Start"] )
        End = dateToMinute( row["End"] )
        tasks_unavailabilities[row["TaskId"]] = TUnavalaibility(0,0, Start, End)

    #tasks
    task_sheet = pd.read_excel(xls, 'Tasks')
    tasks = [0]  ## in order to begin index at 1, rather than 0
    for index, row in task_sheet.iterrows():
        #openingTime = dateToMinute( row["OpeningTime"] )
        #closingTime = dateToMinute( row["ClosingTime"] )
        openingTime = 777
        closingTime = 7777
        if row["Skill"] in skillToRank.keys(): 
            skill = skillToRank[ row["Skill"] ] 
        else: 
            skill = skillToRank["other"]
        if row["TaskId"] in tasks_unavailabilities:  ## if the task is unavailable
            tasks.append( TTask(row["TaskId"], row["Latitude"], row["Longitude"], row["TaskDuration"], skill, row["Level"], openingTime, closingTime, tasks_unavailabilities[row["TaskId"]], 0, 0) )
        else:
            tasks.append( TTask(row["TaskId"], row["Latitude"], row["Longitude"], row["TaskDuration"], skill, row["Level"], openingTime, closingTime, [], 0, 0) )
    
    
    return employees, tasks
