import math
import gmplot
from math import sin, cos,sqrt,atan2,radians
def distance(depart,arrivee):
    lat1=depart.Latitude
    lat2=arrivee.Latitude
    lon1=depart.Longitude
    lon2=arrivee.Longitude
    lat1=radians(lat1)
    lat2=radians(lat2)
    lon1=radians(lon1)
    lon2=radians(lon2)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R=6371000
    distance = R * c
    return distance


"""
def distance(depart, arrivee):
    lat1=depart.Latitude
    lat2=arrivee.Latitude
    lon1=depart.Longitude
    lon2=arrivee.Longitude
    return sqrt((lon1-lon2)**2+(lat1-lat2)**2)

"""

def dateToMinute(date):
    pm = (date[-2:] == 'pm')
    h,m = map(int, date[:-2].split(":") )
    return 12*60*pm + 60*h + m
colors=['black','red','green','blue','yellow','cyan','orange','slategray','lemonchiffon']
color_code=dict()
color_code={i:color for (i,color) in enumerate(colors)}

def draw(latitude_list_list,longitude_list_list,task_numbers,name):
    mean_latitude=sum(latitude_list_list[0])/len(latitude_list_list[0])
    mean_longitude=sum(longitude_list_list[0])/len(longitude_list_list[0])
    gmap1 = gmplot.GoogleMapPlotter(mean_latitude, mean_longitude,  13 )
    for employee in range(len(latitude_list_list)):
        gmap1.plot(latitude_list_list[employee],longitude_list_list[employee], color_code[employee],edge_width=2.5)
        for point in range(len(latitude_list_list[employee])):
            gmap1.marker(latitude_list_list[employee][point],longitude_list_list[employee][point],title="{}".format(task_numbers[employee][point]))
    gmap1.draw( "{}".format(name) )

def trajet(depart,arrivee):
    return (3.6/(50*60))*distance(depart,arrivee)

def fichier_texte(DELTA,T,employees,number_of_tasks):
    texte=open('bordeaux.txt','w')
    #rajouter le cas ou la tache n est pas realisee
    resultats=[['taskId','performed','employeeName','startTime']]

    number_of_employees=len(employees)
    for i in range(0,number_of_tasks+1): 
        for j in range(0,number_of_tasks+1):
            for k in range(1,number_of_employees+1):
                if DELTA[(i,j,k)].x==1:
                    if i!= 0:
                        resultats.append([f'T{i}',1,employees[k-1].EmployeeName,T[(i,k)].x])
    for line in (resultats):
        texte.write("{};{};{};{};\n".format(line[0],line[1],line[2],line[3]))
    print(resultats)

