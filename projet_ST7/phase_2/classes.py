

##**********************************    TEmployee   **********************************

class TEmployee:
    
    def __init__(self, EmployeeName, Latitude, Longitude, Skill, Level, WorkingStartTime, WorkingEndTime, Unavalaibilities):
        self.EmployeeName = EmployeeName
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Skill = Skill
        self.Level = Level
        self.WorkingStartTime = WorkingStartTime
        self.WorkingEndTime = WorkingEndTime
        self.Unavalaibilities = Unavalaibilities

    def __str__(self): 
        return self.EmployeeName +" "+ str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.Skill) +" "+ str(self.Level) +" "+ str(self.WorkingStartTime) +" "+ str(self.WorkingEndTime)

##**********************************    TTask   **********************************

class TTask:
    def __init__(self, TaskId, Latitude, Longitude, TaskDuration, Skill, Level, OpeningTime, ClosingTime):
        self.TaskId = TaskId
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.TaskDuration = TaskDuration
        self.Skill = Skill
        self.Level = Level
        self.OpeningTime = OpeningTime
        self.ClosingTime = ClosingTime
        self.Unavalaibilities = Unavalaibilities

    def __str__(self): 
        return self.TaskId +" "+ str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.TaskDuration) +" "+ str(self.Skill) +" "+ str(self.Level) +" "+ str(self.OpeningTime) +" "+ str(self.ClosingTime)

##**********************************    TUnavalaibility   **********************************

class TUnavalaibility:
    def __init__(self, Latitude, Longitude, Start, End):
        self.TaskId = Latitude
        self.Latitude = Longitude
        self.Longitude = Start
        self.TaskDuration = End   
    
def __str__(self): 
        return str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.Start) +" "+ str(self.End) 