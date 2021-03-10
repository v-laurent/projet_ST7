import math
import gmplot
from math import sin, cos,sqrt,atan2,radians,acos,asin
import os

#rayon de la terre en m
R = 6371000
## Phase du projet ##
phase = "phase1" 
#phase = "phase2"
#phase = "phase3"

def distance(A,B):    
    ALatitude, ALongitude = radians(A.Latitude), radians(A.Longitude)
    BLatitude, BLongitude = radians(B.Latitude), radians(B.Longitude)
    a = sin( (BLatitude - ALatitude) / 2)**2 + cos(ALatitude)*cos(BLatitude)*sin( (BLongitude - ALongitude) / 2)**2
    c = 2*asin(sqrt(a))
    distance = R * c
    return distance

def dateToMinute(date):
    pm = (date[-2:] == 'pm')
    h,m = map(int, date[:-2].split(":") )
    return 12*60*pm + 60*h + m


colors=['black','red','green','blue','yellow','cyan','orange','slategray','lemonchiffon']
color_code=dict()
color_code={i:color for (i,color) in enumerate(colors)}

def draw(latitude_list_list,longitude_list_list,task_numbers,name,DELTA):
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

def fichier_texte(DELTA,T,employees,number_of_tasks,titre,phase=phase):
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = directory + '_'+ phase
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    texte=open(f'{titre}.txt','w')
    #rajouter le cas ou la tache n est pas realisee
    resultats=[['taskId','performed','employeeName','startTime']]

    number_of_employees=len(employees)
    for i in range(0,number_of_tasks): 
        for j in range(0,number_of_tasks):
            for k in range(1,number_of_employees):
                if DELTA[(i,j,k)].x==1:
                    if i!= 0:
                        resultats.append([f'T{i}',1,employees[k].EmployeeName,T[(i,k)].x])
    for line in (resultats):
        texte.write("{};{};{};{};\n".format(line[0],line[1],line[2],line[3]))
    print(resultats)
