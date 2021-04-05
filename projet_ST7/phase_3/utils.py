import math
import gmplot
from math import sin, cos,sqrt,atan2,radians,acos,asin
import os
from classes import *
from  matplotlib.colors import cnames

#rayon de la terre en m
R = 6371000
## Phase du projet ##
#phase = "1" 
#phase = "2"
phase = "3"
## Instance jeu de données ##
#instance = "1"
instance = "2"
#instance = "3"
#instance = "4"

def distance(A,B):    
    ALatitude, ALongitude = radians(A.Latitude), radians(A.Longitude)
    BLatitude, BLongitude = radians(B.Latitude), radians(B.Longitude)
    a = sin((BLatitude - ALatitude)/2)**2 + cos(ALatitude)*cos(BLatitude)*sin((BLongitude - ALongitude)/2)**2
    c = 2*asin(sqrt(a))
    distance = R * c
    return distance

def dateToMinute(date):
    pm = (date[-2:] == 'pm')
    h,m = map(int, date[:-2].split(":") )
    if pm and h==12:
        return 12*60+m
    return 12*60*pm + 60*h + m


colors = [key for key,c in cnames.items()]
#colors=['black','red','green','blue','yellow','cyan','orange','slategray','lemonchiffon']
color_code=dict()
color_code={i:color for (i,color) in enumerate(colors)}

def draw(employees,tasks,latitude_list_list,longitude_list_list,task_numbers,name,DELTA,phase=phase):
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = directory + os.sep+"gmplot_fichiers_phase" +phase
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    mean_latitude=sum(latitude_list_list[1])/len(latitude_list_list[1])
    mean_longitude=sum(longitude_list_list[1])/len(longitude_list_list[1])
    gmap1 = gmplot.GoogleMapPlotter(mean_latitude, mean_longitude,  10)
    
    for i in range(1,len(tasks)):
        task = tasks[i]
        gmap1.marker(task.Latitude,task.Longitude,'red',label="{}".format(task.TaskId))
    
    for employee in range(1,len(latitude_list_list)):
        gmap1.plot(latitude_list_list[employee],longitude_list_list[employee], color_code[employee-1],edge_width=2.5)
        for point in range(0,len(latitude_list_list[employee])):
            gmap1.marker(latitude_list_list[employee][point],longitude_list_list[employee][point],'lightgreen',label="{}".format(task_numbers[employee][point])
            ,title=employees[employee].EmployeeName)
    gmap1.draw( "{}".format(name))
    
def trajet(depart,arrivee):
    return (3.6/(50*60))*distance(depart,arrivee)

def fichier_texte(DELTA,T,P,tasks,new_tasks,employees,number_of_unavailabilities,country,phase=phase,instance=instance):
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = directory + os.sep + "fichiers_txt_phase" + phase
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    
    titre = "Solution"+country+"V"+instance+"ByV"+phase
    texte = open(f'{titre}.txt','w')
    number_of_tasks = len(tasks)-1
    number_of_employees = len(employees)-1
    
    resultats=[['taskId','performed','employeeName','startTime']]
    for n in range(1, number_of_tasks+1):
        SOMME_DELTA = 0
        for i in range(1, len(new_tasks)):
            for j in range(1, len(new_tasks)):
                for k in range(1, number_of_employees + 1):
                    if new_tasks[i].TaskId == 'T{}'.format(n):
                        if DELTA[(i,j,k)] == 1:
                            resultats.append([f'T{n}',1,employees[k].EmployeeName,T[(k,i)]])
                            SOMME_DELTA += 1
        if SOMME_DELTA == 0:
            resultats.append([f'T{n}',0,"",""])

    resultats.append([])
    resultats.append(["employeeName", "lunchBreakStartTime"])
    for k in range(1, number_of_employees+1):
        for i in range(1, number_of_employees +1): 
            if P[(k,i)] == 1:                   #the employee doesn't do anything before noon
                resultats.append([f'{employees[k].EmployeeName}', 12*60])
        for i in range(1 + number_of_employees, len(new_tasks)):
            if P[(k,i)] == 1:
                if T[(k,i)] + new_tasks[i].TaskDuration <= 12*60:
                    resultats.append([f'{employees[k].EmployeeName}', 12*60])
                else :
                    resultats.append([f'{employees[k].EmployeeName}', T[(k,i)] + new_tasks[i].TaskDuration])



    for line in (resultats):
        if len(line) == 4:
            texte.write("{};{};{};{};\n".format(line[0],line[1],line[2],line[3]))
        elif len(line) == 0 :
            texte.write("\n")
        else:
            texte.write("{};{};\n".format(line[0],line[1]))
    
    #print(resultats) 

    
def sous_taches(tasks):
    new_tasks=[]
    number_of_tasks = len(tasks)
    for i in range(1,number_of_tasks):
        number_of_sisters=len(tasks[i].Unavailabilities)
        for unava in range(len(tasks[i].Unavailabilities)):
            if tasks[i].Unavailabilities[unava].End >= tasks[i].ClosingTime:
                number_of_sisters-=1
            if tasks[i].Unavailabilities[unava].Start == tasks[i].OpeningTime:
                number_of_sisters-=1
        if len(tasks[i].Unavailabilities)==0:
            new_tasks.append(tasks[i])
        else:
            start=tasks[i].OpeningTime
            end=min(tasks[i].Unavailabilities[0].Start,tasks[i].ClosingTime)
            if tasks[i].Unavailabilities[0].Start != 8*60:
                new_tasks.append(TTask(tasks[i].TaskId,tasks[i].Latitude,tasks[i].Longitude,
                                tasks[i].TaskDuration,tasks[i].Skill, tasks[i].Level,
                                start, end, [],number_of_sisters)) 
            if end==tasks[i].ClosingTime:
                continue
            for sous_tache in range(len(tasks[i].Unavailabilities)):
                start=tasks[i].Unavailabilities[sous_tache].End
                if sous_tache == len(tasks[i].Unavailabilities)-1:
                    end=tasks[i].ClosingTime
                else:
                    end=min(tasks[i].Unavailabilities[sous_tache+1].Start,tasks[i].ClosingTime)
                if end>start:
                    new_tasks.append(TTask(tasks[i].TaskId,tasks[i].Latitude,tasks[i].Longitude,
                            tasks[i].TaskDuration,tasks[i].Skill, tasks[i].Level,
                            start, end, [], number_of_sisters))
                if end == tasks[i].ClosingTime:
                    break

    return new_tasks


def score(DELTA,T,P,tasks,new_tasks,employees,nb_unavailabilities,country,phase=phase,instance=instance):
    "Give some statistics of the solution (time of tasks, of travel, of unavailability, ...)"
    number_of_employees, number_of_tasks = len(employees)-1, len(new_tasks)-1
    tasks_time, travel_time, unavailability_time, inactivity_time = 0, 0, 0, 0
    print('================================================================================================')
    for k in range(1,number_of_employees+1):
        tasks_time_k, travel_time_k, unavailability_time_k = 0, 0, 0
        for i in range(1,number_of_tasks+1):
            for j in range(1,number_of_tasks+1):
                if DELTA[(i,j,k)]==1:
                    if type(new_tasks[i].TaskId) != int:
                        tasks_time_k += new_tasks[i].TaskDuration
                    travel_time_k += trajet(new_tasks[i],new_tasks[j])
        for l in range(len(employees[k].Unavailabilities)):
            unavailability_time_k += employees[k].Unavailabilities[l].End - employees[k].Unavailabilities[l].Start
        inactivity_time_k = employees[k].WorkingEndTime - employees[k].WorkingStartTime - tasks_time_k - travel_time_k - unavailability_time_k
        print(f"{employees[k].EmployeeName} fait {round(tasks_time_k/60,1)} h de tâches, {round(travel_time_k/60,1)} h de trajet, {round(unavailability_time_k/60,1)} h d'indisponibilité et {round(inactivity_time_k/60,1)} h d'inactivité")
        tasks_time += tasks_time_k
        travel_time += travel_time_k
        unavailability_time += unavailability_time_k
        inactivity_time += inactivity_time_k
    print("Soit au total :")
    print(f" - {round(tasks_time/60,1)} h de tâches \n - {round(travel_time/60,1)} h de trajet \n - {round(unavailability_time/60,1)} h d'indisponibilité \n - {round(inactivity_time/60,1)} h d'inactivité")
    print("sur {} h".format(round((tasks_time+travel_time+unavailability_time+inactivity_time)/60)))
    print('================================================================================================')
