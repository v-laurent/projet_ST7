import pandas as pd
import numpy as np
import plotly.express as px
country = "bordeaux"
employees = ["Ambre", "Valentin"]

def verification(country):
    decision = pd.read_csv(f"{country}.txt", sep=';')
    decision = decision[['taskId','performed','employeeName','startTime']]

    contenu = []
    for employee in employees :
        for i in range(len(decision) -1):
            if decision.iloc[i+1][1] == 1 and employee == decision.iloc[i+1][2]:
                start = decision.iloc[i+1][3]
                taskduration = 60
                s_hour = int(start//60)
                if s_hour < 10 :
                    s_hour = str(0)+str(s_hour)
                s_minute = int(start%60)
                if s_minute < 10 :
                    s_minute = str(0) + str(s_minute)
                e_hour = int((start+taskduration)//60)
                if e_hour < 10 :
                    e_hour = str(0) + str(e_hour)
                e_minute = int((start+taskduration)%60)
                if e_minute < 10 :
                    e_minute = str(0) + str(e_minute)
                taskname = decision.iloc[i+1][0]
                resource = decision.iloc[i][2]
                contenu.append(dict(Task="{}".format(taskname), Start='2020-03-10 {}:{}'.format(s_hour,s_minute), Finish='2020-03-10 {}:{}'.format(e_hour,e_minute), Resource = resource))
    tab = pd.DataFrame(contenu)
    fig = px.timeline(tab, x_start="Start", x_end="Finish", y="Resource", text = "Task", title = "Planning Journée")
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(title_font_size = 40, font_size= 20)
    fig.show()          

verification("bordeaux")