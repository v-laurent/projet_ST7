from classes import TEmployee
from classes import TTask
from utils import *
import csv
from os.path import dirname, join
import pandas as pd

#reading data
current_dir = dirname(__file__)
file_path = current_dir + "/InstancesV1/InstanceBordeauxV1.xlsx"
xls = pd.ExcelFile(file_path)

#employees
employees_sheet = pd.read_excel(xls, 'Employees')
employees = []
for index, row in employees_sheet.iterrows():
    workingStartTime = dateToMinute( row["WorkingStartTime"] )
    workingEndTime = dateToMinute( row["WorkingEndTime"] )
    employees.append( TEmployee(row["EmployeeName"], row["Latitude"], row["Longitude"], row["Skill"], row["Level"], workingStartTime, workingEndTime) )

#tasks
task_sheet = pd.read_excel(xls, 'Tasks')
tasks = []
for index, row in task_sheet.iterrows():
    openingTime = dateToMinute( row["OpeningTime"] )
    closingTime = dateToMinute( row["ClosingTime"] )
    tasks.append( TTask(row["TaskId"], row["Latitude"], row["Longitude"], row["TaskDuration"], row["Skill"], row["Level"], openingTime, closingTime) )

print(tasks[0])

