class TEmployee:
    def __init__(self, EmployeeName, Latitude, Longitude, Skill, Level, WorkingStartTime, WorkingEndTime):
        self.EmployeeName = EmployeeName
        self.Latitude = Latitude
        self.Longitude = Longitude
        self.Skill = Skill
        self.Level = Level
        self.WorkingStartTime = WorkingStartTime
        self.WorkingEndTime = WorkingEndTime


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