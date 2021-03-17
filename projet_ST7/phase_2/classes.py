

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
        return self.EmployeeName +" "+ str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.Skill) +" "+ str(self.Level) +" "+ str(self.WorkingStartTime) +" "+ str(self.WorkingEndTime)+" "+str(self.Unavalaibilities)

##**********************************    TTask   **********************************

class TTask:
    def __init__(self, TaskId, Latitude, Longitude, TaskDuration, Skill, Level, OpeningTime, ClosingTime, Unavalaibilities, number_of_sisters, id_employee=0):
        self.TaskId = TaskId
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.TaskDuration = TaskDuration
        self.Skill = Skill
        self.Level = Level
        self.OpeningTime = OpeningTime
        self.ClosingTime = ClosingTime
        self.Unavalaibilities = Unavalaibilities
        self.number_of_sisters = number_of_sisters
        self.id_employee = id_employee

    def __str__(self): 
        return self.TaskId +" "+ str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.TaskDuration) +" "+ str(self.Skill) +" "+ str(self.Level) +" "+ str(self.OpeningTime) +" "+ str(self.ClosingTime)+ " "+ str(self.Unavalaibilities) + " "+ str(self.number_of_sisters)+" "+str(self.id_employee)

##**********************************    TUnavalaibility   **********************************

class TUnavalaibility:
    def __init__(self, Latitude, Longitude, Start, End):
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Start = Start
        self.End = End   
    
def __str__(self): 
        return str(self.Latitude) +" "+ str(self.Longitude) +" "+ str(self.Start) +" "+ str(self.End) 