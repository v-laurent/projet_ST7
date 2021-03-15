from os.path import dirname
import pandas as pd
from utils import *
from classes import *
import numpy as np
pd.options.mode.chained_assignment = None
country = "Poland"
def num_missing(x):
        return sum(x.isnull())

def extract_data_Anouar(country):
    current_dir = dirname(__file__)
    file_path = current_dir + "/InstancesV1/Instance" + country + "V1.xlsx"
    file_path_employee = current_dir + "/InstancesV1/Instance" +country+ "V1_Employee.csv"
    file_path_task = current_dir + "/InstancesV1/Instance" +country+ "V1_Task.csv"
    xls = pd.ExcelFile(file_path)

        #employees
    employees_sheet = pd.read_excel(xls, 'Employees')
    employee_csv = employees_sheet.to_csv(file_path_employee, index = (["EmployeeName","Latitude","Longitude","Skill","Level","WorkingStartTime","WorkingEndTime"]), header=True)
    employees =[]


    df_employee = pd.read_csv(file_path_employee)
    n_lines = df_employee.shape[0]
    n_missing = df_employee.apply(num_missing, axis=0)["EmployeeName"]
    index_missing = [k for k in range(n_lines-n_missing,n_lines)]
    df_employee.drop(index_missing, inplace=True)
    n_lines_final = df_employee.shape[0]
    skillToRank = {skill : i for i,skill in enumerate( set(df_employee["Skill"]) )}
    skillToRank['other'] = len(skillToRank)
    for k in range(n_lines_final):
        df_employee["WorkingStartTime"][k]=dateToMinute(df_employee["WorkingStartTime"][k])
        df_employee["WorkingEndTime"][k]=dateToMinute(df_employee["WorkingEndTime"][k])
        df_employee["Skill"][k] = skillToRank[ df_employee["Skill"][k] ]
        employees.append( TEmployee(df_employee["EmployeeName"][k], df_employee["Latitude"][k], df_employee["Longitude"][k], df_employee["Skill"][k], df_employee["Level"][k], df_employee["WorkingStartTime"][k], df_employee["WorkingEndTime"][k]) )
    print(df_employee.head())
    ### Tasks ##
    task_sheet = pd.read_excel(xls, 'Tasks')
    task_csv = task_sheet.to_csv(file_path_task, index = (["TaskId","Latitude","Longitude","TaskDuration","Skill", "Level","OpeningTime","ClosingTime"]), header=True)
    tasks =[]


    df_task = pd.read_csv(file_path_task)
    n_lines = df_task.shape[0]
    n_missing = df_task.apply(num_missing, axis=0)["TaskId"]
    index_missing = [k for k in range(n_lines-n_missing,n_lines)]
    print(index_missing)
    df_task.drop(index_missing, inplace=True)
    n_lines_final = df_task.shape[0]
    skillToRank = {skill : i for i,skill in enumerate( set(df_task["Skill"]) )}
    skillToRank['other'] = len(skillToRank)
    print(n_lines)
    print(n_missing)
    print(n_lines_final)
    print(df_task.head())
    for k in range(n_lines_final):
        df_task["OpeningTime"][k]=dateToMinute(df_task["OpeningTime"][k])
        df_task["ClosingTime"][k]=dateToMinute(df_task["ClosingTime"][k])
        df_task["Skill"][k] = skillToRank[ df_task["Skill"][k] ]
        tasks.append( TTask(df_task["TaskId"][k], df_task["Latitude"][k], df_task["Longitude"][k], df_task["TaskDuration"], df_task["Skill"][k], df_task["Level"][k], df_task["OpeningTime"][k], df_task["ClosingTime"][k]) )
    print(df_task.head())
    return employees, tasks

employees, tasks = extract_data_Anouar(country)