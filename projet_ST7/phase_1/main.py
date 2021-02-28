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
    employees.append( TEmployee(row["EmployeeName"], row["Latitude"], row["Longitude"], row["Skill"], row["Level"], row["WorkingStartTime"],row["WorkingEndTime"]) )





<<<<<<< HEAD
=======
employee = TEmployee(1,1,1,1,1,1,1)
task = TTask(1,1,1,1,1,1,1,1)
>>>>>>> 2c2502501694dc3e202a1d6785780b08feb5ff51
