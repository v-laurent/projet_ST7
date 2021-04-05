
import math
import numpy as np

##**********************************    TEmployee   **********************************

class TEmployee:
    
    def __init__(self, EmployeeName, Latitude, Longitude, Skill, Level, WorkingStartTime, WorkingEndTime, Unavailabilities):
        self.EmployeeName = EmployeeName
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Skill = Skill
        self.Level = Level
        self.WorkingStartTime = WorkingStartTime
        self.WorkingEndTime = WorkingEndTime
        self.Unavailabilities = Unavailabilities

    @property
    def Max_working_duration(self):
        return self.WorkingEndTime - self.WorkingStartTime - sum([ (u.End - u.Start) for u in self.Unavailabilities])

    def __str__(self): 
        return self.EmployeeName +" "+ str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.Skill) +" "+ str(self.Level) +" "+ str(self.WorkingStartTime) +" "+ str(self.WorkingEndTime)+" "+str(self.Unavailabilities)

##**********************************    TTask   **********************************

class TTask:
    def __init__(self, TaskId, Latitude, Longitude, TaskDuration, Skill, Level, OpeningTime, ClosingTime, Unavailabilities, number_of_sisters, id_employee=0):
        self.TaskId = TaskId
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.TaskDuration = TaskDuration
        self.Skill = Skill
        self.Level = Level
        self.OpeningTime = OpeningTime
        self.ClosingTime = ClosingTime
        self.Unavailabilities = Unavailabilities
        self.number_of_sisters = number_of_sisters
        self.id_employee = id_employee

    @property
    def X(self):
        R = 6371000 
        return R * math.sin(self.Latitude*math.pi/180) * math.sin(self.Longitude*math.pi/180) 

    @property
    def Y(self):
        R = 6371000 
        return -R * math.cos(self.Latitude*math.pi/180)

    @property
    def coord(self):
        R = 6371000 
        return np.array( [R * math.sin(self.Latitude*math.pi/180) * math.sin(self.Longitude*math.pi/180) , -R * math.cos(self.Latitude*math.pi/180)] )

    def __str__(self): 
        return str(self.TaskId) +" "+ str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.TaskDuration) +" "+ str(self.Skill) +" "+ str(self.Level) +" "+ str(self.OpeningTime) +" "+ str(self.ClosingTime)+ " "+ str(self.Unavailabilities) + " "+ str(self.number_of_sisters)+" "+str(self.id_employee)

##**********************************    TUnavailability   **********************************

class TUnavailability:
    def __init__(self, Latitude, Longitude, Start, End):
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Start = Start
        self.End = End   
    
def __str__(self): 
        return str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.Start) +" "+ str(self.End) 