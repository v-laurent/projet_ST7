import math
import gmplot
from math import sin, cos,sqrt,atan2,radians,acos,asin
import os

#rayon de la terre en m
R = 6371000
## Phase du projet ##
phase = "1" 
#phase = "2"
#phase = "3"
## Instance jeu de données ##
instance = "1"
#instance = "2"
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


colors=['black','red','green','blue','yellow','cyan','orange','slategray','lemonchiffon']
color_code=dict()
color_code={i:color for (i,color) in enumerate(colors)}

def draw(latitude_list_list,longitude_list_list,task_numbers,name,DELTA,phase=phase):
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = directory + os.sep+"gmplot_fichiers_phase" +phase
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    mean_latitude=sum(latitude_list_list[1])/len(latitude_list_list[1])
    mean_longitude=sum(longitude_list_list[1])/len(longitude_list_list[1])
    gmap1 = gmplot.GoogleMapPlotter(mean_latitude, mean_longitude,  10)
    for employee in range(1,len(latitude_list_list)):
        gmap1.plot(latitude_list_list[employee],longitude_list_list[employee], color_code[employee-1],edge_width=2.5)
        for point in range(0,len(latitude_list_list[employee])):
            gmap1.marker(latitude_list_list[employee][point],longitude_list_list[employee][point],title="{}".format(task_numbers[employee][point]))
    gmap1.draw( "{}".format(name))

def trajet(depart,arrivee):
    return (3.6/(50*60))*distance(depart,arrivee)

def fichier_texte(DELTA,T,P,employees,number_of_tasks,country,phase=phase,instance=instance):
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = directory + os.sep+"fichiers_txt_phase" +phase
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    titre = "Solution"+country+"V"+instance+"ByV"+phase
    texte=open(f'{titre}.txt','w')
    #rajouter le cas ou la tache n est pas realisee
    resultats=[['taskId','performed','employeeName','startTime']]

    number_of_employees=len(employees)
    for i in range(0,number_of_tasks): 
        for j in range(0,number_of_tasks):
            for k in range(1,number_of_employees):
                if DELTA[(i,j,k)]==1:
                    if i!= 0:
                        resultats.append([f'T{i}',1,employees[k].EmployeeName,T[(k,i)]])

    resultats.append(["employeeName", "lunchBreakStartTime"])
    for k in range(number_of_employees):
        for i in range(number_of_tasks):
            if P[(i,k)] == 1:
                if T[(i,k)] + tasks[i].TaskDuration <= 12*60:
                    resultats.append([f'{employees[k].EmployeeName}', 12*60])
                else :
                    resultats.append([f'{employees[k].EmployeeName}', T[(i,k)] + tasks[i].TaskDuration])

    for line in (resultats):
        if len(line) == 4:
            texte.write("{};{};{};{};\n".format(line[0],line[1],line[2],line[3]))
        else :
            texte.write("{};{};\n".format(line[0],line[1]))
    
    print(resultats) 