from os.path import dirname
import pandas as pd
from utils import *
from classes import *


current_dir = dirname(__file__)
file_path = current_dir + "/InstancesV1/Instance" + "Bordeaux" + "V1.xlsx"
file_path2 = current_dir + "/InstancesV1/Instance" + "Bordeaux" + "V1.csv"
xls = pd.ExcelFile(file_path)

    #employees
employees_sheet = pd.read_excel(xls, 'Employees')
employee_csv = employees_sheet.to_csv(file_path2, index = (["EmployeeName","Latitude","Longitude","Skill","Level","WorkingStartTime","WorkingEndTime"]), header=True)

df = pd.read_csv(file_path2)
print(df.shape)
df.dropna()
print(df.shape)
print(df["EmployeeName"][1])

