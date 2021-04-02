import pandas as pd
import numpy as np
from classes import *
from utils import *
from reading_data import *
import matplotlib.pyplot as plt

#################################################
country = 'Australia'
dossier_txt = 'fichiers_txt_phase2'
version = 'V2ByV2'
#################################################
# chosen accuracy for the warning (in minutes)
epsilon = 1


def verification(country, epsilon=0.05):
    employees,tasks = readingData(country)          # the depot is not in tasks
    number_of_employees = len(employees)-1
    number_of_tasks = len(tasks)-1
    
    decision = pd.read_csv(f"{dossier_txt}/Solution{country}{version}.txt", sep=';', nrows=number_of_tasks)
    decision = decision[['taskId','performed','employeeName','startTime']]

    lunch = pd.read_csv(f"{dossier_txt}/Solution{country}{version}.txt", sep=';', skiprows=number_of_tasks+1 ,nrows=number_of_employees)
    lunch = lunch[['employeeName','lunchBreakStartTime']]

    # Pourcentage of accomplished tasks
    print("Pourcentage de tâches réalisées : {} %".format(round((decision['performed'].sum())/number_of_tasks*100,1)))

    # Constraints
    for i in range(1, number_of_tasks+1):
        task_id = tasks[i].TaskId
        T_i_startTime = decision[decision['taskId']==task_id].loc[:,'startTime'].values
        # vérification que la tâche Ti est faite
        if len(decision[decision['taskId']==task_id].loc[:,'performed'].values) == 0:
            print(f"ERROR : ligne de la tâche {task_id} manquante")
            continue
        if decision[decision['taskId']==task_id].loc[:,'performed'].values == 0:
            print(f"Tâche {task_id} non réalisée")
            continue
        employee_name = decision[decision['taskId']==task_id].loc[:,'employeeName'].values[0]
        
        k=1
        while employees[k].EmployeeName != employee_name:
            k+=1                                                # index of the employee accomplishing the task

        # 1- tasks availabilities            
        if T_i_startTime < tasks[i].OpeningTime:
            print(f"ERROR 1.1 : tâche {task_id} réalisée par {employee_name} avant l'ouverture de la tâche")
        if T_i_startTime > tasks[i].ClosingTime:
            print(f"ERROR 1.2 : tâche {task_id} réalisée par {employee_name} après la fermeture de la tâche")
        if T_i_startTime > tasks[i].ClosingTime - tasks[i].TaskDuration:
            print(f"ERROR 1.3 : tâche {task_id} réalisée par {employee_name} trop proche de la fermeture de la tâche")
        for unavailability in tasks[i].Unavailabilities :
                if T_i_startTime + tasks[i].TaskDuration > unavailability.Start and T_i_startTime < unavailability.End:
                    print(f"ERROR 1.4 : tâche {task_id} réalisée par {employee_name} pendant une période d'indisponibilité de la tâche")

        # 2- employees availabilities
        if T_i_startTime < employees[k].WorkingStartTime:
            print(f"ERROR 2.1 : {employee_name} réalise la tache {task_id} avant le début de son service")
        if T_i_startTime > employees[k].WorkingEndTime:
            print(f"ERROR 2.2 : {employee_name} réalise la tache {task_id} après la fin de son service")
        if T_i_startTime > employees[k].WorkingEndTime - tasks[i].TaskDuration - trajet(tasks[i],employees[k]):
            print(f"ERROR 2.3 : {employee_name} réalise la tache {task_id} trop proche de la fin de son service")
        for unavailability in employees[k].Unavailabilities :
            if T_i_startTime + tasks[i].TaskDuration > unavailability.Start and T_i_startTime < unavailability.End:
                print(f"ERROR 2.4 : {employee_name} réalise la tache {task_id} pendant sa période d'indisponibilité")

        # 3- skills
        if employees[k].Skill != tasks[i].Skill:
            print(f"ERROR 3.1 : compétence {employees[k].Skill} manquante")
        else :
            if employees[k].Level < tasks[i].Level:
                print(f"ERROR 3.2 : compétence n°{tasks[k].Skill} de niveau {tasks[i].Level} requis par {employee_name} (niveau {employees[k].Level} appris)")


    # Verify the employees travels
    for k in range(1,number_of_employees+1):
        employee_name = employees[k].EmployeeName
        tasks_id = decision[decision['employeeName']==employee_name].loc[:,'taskId'].values
        T_i_startTime = decision[decision['employeeName']==employee_name].loc[:,'startTime'].values

        # verify that employees work
        if len(T_i_startTime) == 0:
            print(f"{employee_name} n'effectue aucune tâche")
            continue
        
        sorted_indices = np.argsort(T_i_startTime)         # indexs of tasks accomplished only by employee k
        sorted_indices_bis = []                             # set of all tasks
        for i in sorted_indices:
            for j in range(1,number_of_tasks+1):
                if tasks[j].TaskId == tasks_id[i]:
                    sorted_indices_bis.append(j)

        # 4- Lunch break time
        lunch_time = lunch[lunch['employeeName']==employee_name].loc[:,'lunchBreakStartTime'].values
        if len(lunch_time) == 0:
            print(f"ERROR 4.1 : {employee_name} ne fait pas de pause repas") 
        elif lunch_time < 12*60:
            print(f"ERROR 4.2 : {employee_name} fait sa pause repas trop tôt, à {lunch_time[0]}")
        elif lunch_time > 14*60:
            print(f"ERROR 4.3 : {employee_name} fait sa pause repas trop tard, à {lunch_time[0]}")
    
        # 5- depot/work travel
        i0 = sorted_indices[0]
        i0_bis = sorted_indices_bis[0]
        eps = T_i_startTime[i0] - (employees[k].WorkingStartTime + trajet(employees[k], tasks[i0_bis]))
        if eps < 0:
            print(f"ERROR 5.1 : {employee_name} part de son dépôt trop tôt")
        else:
            if eps > epsilon:
                print(f"warning 5.2 : {employee_name} part de son dépôt {round(eps,2)}min trop tard")
        
        # 6- time coherence of tasks
        for i in range(1,len(sorted_indices)):
            i1 = sorted_indices[i-1]                # starting task
            i2 = sorted_indices[i]                  # arrival task
            i1_bis = sorted_indices_bis[i-1]
            i2_bis = sorted_indices_bis[i]
            eps = T_i_startTime[i2] - (T_i_startTime[i1] + tasks[i1_bis].TaskDuration + trajet(tasks[i1_bis],tasks[i2_bis]))
            if eps < 0:
                print(f"ERROR 6.1 : {employee_name} commence la tâche {tasks_id[i2]} trop tôt par rapport à la tâche précédente {tasks_id[i1]}")            
            else:
                if eps > epsilon:
                    print(f"warning 6.2 : {employee_name} met {round(eps,2)}min de trop pour aller de la tâche {tasks_id[i2]} à la tâche {tasks_id[i1]}")

            # 4 bis- 1h lunch break time
            if T_i_startTime[i1] < lunch_time and T_i_startTime[i2] > lunch_time:
                if T_i_startTime[i1] + tasks[i1_bis].TaskDuration > 13*60:
                    print(f"ERROR 4.4 : {employee_name} fini la tâche T{i1_bis} trop tard pour manger")
                if T_i_startTime[i2] < 13*60:
                    print(f"ERROR 4.5 : {employee_name} commence la tâche T{i2_bis} trop tôt pour manger")
                if eps < 60:
                    print(f"ERROR 4.6 : {employee_name} n'a pas le temps de manger entre les tâches T{i1_bis} et T{i2_bis}")

            # 7- employee unavailability location
            for unavailability in employees[k].Unavailabilities :
                if T_i_startTime[i1] < unavailability.Start and T_i_startTime[i2] > unavailability.Start:
                    eps2 = T_i_startTime[i2] - (T_i_startTime[i1] + tasks[i1_bis].TaskDuration)
                    if eps2 < trajet(tasks[i1_bis], unavailability) + (unavailability.End - unavailability.Start)+ trajet(unavailability , tasks[i2_bis]):
                        print(f"ERROR 7.3 : {employee_name} n'est pas au bon endroit pendant sa période d'indisponibilité")

        # 8- last travel from task to depot
        iN = sorted_indices[-1]
        iN_bis = sorted_indices_bis[-1]
        if T_i_startTime[iN] > employees[k].WorkingEndTime - trajet(tasks[iN_bis], employees[k]):
            print(f"ERROR 8.1 : {employee_name} revient au dépôt trop tard")





##############################################################
# GANTT DIAGRAM
def gantt_diagram(country):
    employees,tasks = readingData(country)          # depot is not a task
    employees = employees[1:]
    tasks = tasks[1:]
    number_of_employees = len(employees)
    number_of_tasks = len(tasks)
    fig1,gnt=plt.subplots()
    gnt.set_yticks([10*(y+1) for y in range(len(employees))])
    gnt.set_ylim(0,10*len(employees)+7)
    gnt.set_xlim(475, 1085)
    gnt.set_xlabel('Temporal evolution')
    
    gnt.set_yticklabels(['{}'.format(employee.EmployeeName) for employee in employees])
    gnt.grid(True)

    task_times=[[] for _ in range(len(employees))]
    travel_times=[[] for _ in range(len(employees))]
    lunch_times=[[] for _ in range(len(employees))]
    unavailabilities_times=[[] for _ in range(len(employees))]

    decision = pd.read_csv(f"{dossier_txt}/Solution{country}{version}.txt", sep=';', nrows=number_of_tasks)
    decision = decision[['taskId','performed','employeeName','startTime']]
    lunch = pd.read_csv(f"{dossier_txt}/Solution{country}{version}.txt", sep=';', skiprows=number_of_tasks+1 ,nrows=number_of_employees)
    lunch = lunch[['employeeName','lunchBreakStartTime']]

    for k in range(number_of_employees):
        employee_name = employees[k].EmployeeName
        tasks_id = decision[decision['employeeName']==employee_name].loc[:,'taskId'].values
        T_i_startTime = decision[decision['employeeName']==employee_name].loc[:,'startTime'].values
        if len(T_i_startTime) == 0:
            continue
        sorted_indices = np.argsort(T_i_startTime)          # indexs of tasks accomplished only by employee k
        sorted_indices_bis = []                             # set of all the tasks
        for i in sorted_indices:
            for j in range(number_of_tasks):
                if tasks[j].TaskId == tasks_id[i]:
                    sorted_indices_bis.append(j)

        # lunch time
        lunch_time = 0
        if len(lunch[lunch['employeeName']==employee_name].loc[:,'lunchBreakStartTime'].values)==1:
            lunch_time = lunch[lunch['employeeName']==employee_name].loc[:,'lunchBreakStartTime'].values[0]
            lunch_times[k].append((lunch_time, 60))

        # travel time
        end_times=[]
        for task in range(len(tasks_id)):
            task_times[k].append((T_i_startTime[task],tasks[int(tasks_id[task].strip('T'))-1].TaskDuration))
            gnt.annotate(tasks_id[task], (T_i_startTime[task], 10*(k+1)-1))
            end_times.append(T_i_startTime[task]+tasks[int(tasks_id[task].strip('T'))-1].TaskDuration)
        end_times=sorted(end_times)
        travel_times[k].append((employees[k].WorkingStartTime,trajet(employees[k],tasks[sorted_indices_bis[0]])))
        for i in range(len(sorted_indices_bis)-1):
            if i==len(sorted_indices_bis)-1:
                break
            #print("{} vers {}".format(tasks[sorted_indices_bis[i]].TaskId,tasks[sorted_indices_bis[i+1]].TaskId))
            #print("{}".format(trajet(tasks[sorted_indices_bis[i]],tasks[sorted_indices_bis[i+1]])))
            travel_time = trajet(tasks[sorted_indices_bis[i]],tasks[sorted_indices_bis[i+1]])
            if end_times[i] > lunch_time + 60:
                travel_times[k].append((end_times[i], travel_time))
            else:
                time_until_lunch = lunch_time - end_times[i]
                if time_until_lunch > travel_time:
                    travel_times[k].append((end_times[i], travel_time))
                else :
                    travel_times[k].append((end_times[i], time_until_lunch))
                    travel_times[k].append((lunch_time+60, travel_time - time_until_lunch))

            #print(end_times[i-1])
            #print(end_times[i]+trajet(tasks[sorted_indices_bis[i]],tasks[sorted_indices_bis[i+1]]))
        if end_times[-1] < lunch_time + 60:
            travel_times[k].append((lunch_time+60,trajet(employees[k],tasks[sorted_indices_bis[-1]])))
        else: 
            travel_times[k].append((end_times[-1],trajet(employees[k],tasks[sorted_indices_bis[-1]])))

        # unavailabilities
        for unavailability in employees[k].Unavailabilities:
            unavailabilities_times[k].append((unavailability.Start, unavailability.End-unavailability.Start))


    colors=['orange','pink','purple','cyan','olive','brown']
    for i in range(len(employees)):
        gnt.broken_barh(task_times[i],(10*(i+1)-1,2), facecolors=('tab:{}'.format(colors[i])))
        gnt.broken_barh(travel_times[i],(10*(i+1)-2,0.5),facecolors=('tab:red'))
        gnt.broken_barh(lunch_times[i],(10*(i+1)-3,0.5),facecolors=('tab:green'))
        gnt.broken_barh(unavailabilities_times[i],(10*(i+1)-3,0.5),facecolors=('tab:blue'))
    
    plt.vlines([12*60, 14*60], 0, 10*(number_of_employees+1), 'red', 'dashed', alpha=0.5)
    plt.savefig('gantt_phase2/{}.png'.format(country))

    ## 2nd plot
    fig2,blab=plt.subplots()
    blab.set_ylim(0,10*len(tasks)+10)
    fig2.suptitle('{}_tasks'.format(country))
    blab.set_xlim(475, 1085)
    blab.set_xlabel('Temporal evolution')
    blab.set_yticks([10*(y+1) for y in range(len(tasks))])
    blab.set_yticklabels(['{}'.format(task.TaskId) for task in tasks])
    blab.grid(True)
    for i in range(len(tasks)):
        task_id = tasks[i].TaskId
        T_i_startTime = decision[decision['taskId']==task_id].loc[:,'startTime'].values
        
        # change the color if task Ti is done
        color = 'gray'
        if decision[decision['taskId']==task_id].loc[:,'performed'].values == 1:
            employee_name = decision[decision['taskId']==task_id].loc[:,'employeeName'].values[0]
            for k in range(len(employees)):
                if employees[k].EmployeeName == employee_name:
                    color = colors[k]
                    blab.broken_barh([(int(T_i_startTime[0]), tasks[i].TaskDuration)],(10*(i+1)-1,3),facecolors=(f'tab:red'))

        if len(tasks[i].Unavailabilities) == 0:
            blab.broken_barh([(tasks[i].OpeningTime,tasks[i].ClosingTime-tasks[i].OpeningTime)],(10*(i+1)-1,2),facecolors=(f'tab:{color}'))
        else :
            start_time = tasks[i].OpeningTime
            for unavailability in tasks[k].Unavailabilities:
                blab.broken_barh([(start_time,unavailability.Start-start_time)],(10*(i+1)-1,2),facecolors=(f'tab:{color}'))
                start_time = unavailability.End
            blab.broken_barh([(start_time,tasks[i].ClosingTime-start_time)],(10*(i+1)-1,2),facecolors=(f'tab:{color}'))

    plt.savefig('gantt_phase2/{}_tasks.png'.format(country))





verification(country, epsilon)
gantt_diagram(country)