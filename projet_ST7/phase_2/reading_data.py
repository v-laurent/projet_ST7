from os.path import dirname
import pandas as pd
from utils import *
from classes import *


def readingData(country):

    current_dir = dirname(__file__)
    file_path = current_dir + "/InstancesV2/Instance" + country + "V2.xlsx"
    xls = pd.ExcelFile(file_path)

    #employees_unavailabilities
    employees_unavailabilities_sheet = pd.read_excel(xls, 'Employees Unavailibilities')
    employees_unavailabilities = []
    
    for index, row in employees_unavailabilities_sheet.iterrows():
        Start = dateToMinute( row["Start"] )
        End = dateToMinute( row["End"] )
        employees_unavailabilities.append("ca vient" )

    #employees
    employees_sheet = pd.read_excel(xls, 'Employees')
    skillToRank = {skill : i for i,skill in enumerate( set(employees_sheet["Skill"]) )}
    skillToRank['other'] = len(skillToRank)
    employees = []
    
    for index, row in employees_sheet.iterrows():
        workingStartTime = dateToMinute( row["WorkingStartTime"] )
        workingEndTime = dateToMinute( row["WorkingEndTime"] )
        skill = skillToRank[ row["Skill"] ]
        employees.append( TEmployee(row["EmployeeName"], row["Latitude"], row["Longitude"], skill, row["Level"], workingStartTime, workingEndTime) )

      #tasks_unavailabilities
    task_unavailabilities_sheet = pd.read_excel(xls, 'Tasks Unavailabilities')
    tasks_unavailabilities = []
    for index, row in task_sheet_unavailabilities.iterrows():
        Start = dateToMinute( row["Start"] )
        End = dateToMinute( row["End"] )
        tasks_unavailabilities.append( "idem" )
        
    #tasks
    task_sheet = pd.read_excel(xls, 'Tasks')
    tasks = []
    for index, row in task_sheet.iterrows():
        openingTime = dateToMinute( row["OpeningTime"] )
        closingTime = dateToMinute( row["ClosingTime"] )
        if row["Skill"] in skillToRank.keys(): 
            skill = skillToRank[ row["Skill"] ] 
        else: skill = skillToRank["other"]
        tasks.append( TTask(row["TaskId"], row["Latitude"], row["Longitude"], row["TaskDuration"], skill, row["Level"], openingTime, closingTime) )

    
    
    return employees, tasks
