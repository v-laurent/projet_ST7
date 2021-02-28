import math

def distance(x1,y1,x2,y2):
    return math.sqrt( (x2-x1)**2 + (y2-y1)**2 )

def dateToMinute(date):
    pm = (date[-2:] == 'pm')
    h,m = map(int, date[:-2].split(":") )
    return 12*60*pm + 60*h + m


