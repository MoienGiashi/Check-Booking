from bs4 import BeautifulSoup as bs
import urllib.request as request
import re
import numpy as np
import smtplib, ssl

# url = 'type the address'
# will send you the change
def SendEmail(receiver_email,day):
    server = smtplib.SMTP("smtp.gmail.com",587)
    sender_email = "xxxxxxxx"  
    password = 'xxxxxxxx'
    message = """\
    **** schedule changed. 

    Someone cancelled the booking on %s.
    Check at http://www.chem.utoronto.ca/cgi-bin/Calcium40_cni.pl?Op=ShowIt&CalendarName=ESEM__STEM. Close the program when not using.
    """ % day_dic_inv[day]
    
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
    server.quit()


url = 'http://www.chem.utoronto.ca/cgi-bin/Calcium40_cni.pl?CalendarName=ESEM__STEM&Op=ShowIt&Amount=Week&NavType=Absolute&Type=TimePlan&DayViewStart=8&DayViewHours=16&DayViewIncrement=2'
day_dic = {
    'Mon':0,
    'Tue':1,
    'Wed':2,
    'Thu':3,
    'Fri':4,
    'Sat':5,
    'Sun':6
    }
day_dic_inv = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']

old_timetable = np.loadtxt('old_timetable.txt',dtype = np.uint8,delimiter=',')
configfile = open('config.txt','r')
config = configfile.readlines()
configfile.close()

day_track = []
time_track = []
for line in config:
    if line.startswith('\n') or line.startswith('#'):
        continue
    elif re.search("@",line):
        receiver_email = line
    else:
        day_track.append([day_dic[line[0:3]]])
        time_track.append([(int(line[4:6]) - 8) * 2 + int(int(line[7:9]) / 30),\
                           (int(line[10:12]) - 8) * 2 + int(int(line[13:15]) / 30)])


html = request.urlopen(url).read()
soup = bs(html,'html.parser')
table = soup.find("table",class_="EventCells")
row = table.find_all("tr",class_=re.compile(""))
new_timetable = np.zeros((32,7),np.uint8)
for i,time in enumerate(row):
    # i=0 8am; i=1 8:30am etc
    empty_slot = []
    for j in range(7):
        if new_timetable[i,j] == 0:
            empty_slot.extend(str(j))
    for j,slot in enumerate([k for k in time.children if k != ' ' and 'colspan' in k.attrs]):
        if 'rowspan' in slot.attrs:
            # duration=1 0.5h
            duration = int(slot['rowspan'])
            new_timetable[i:i + duration,int(empty_slot[j])] += 1

# print (new_timetable)
for i in range(len(day_track)):
    day = day_track[i][0]
    starttime = time_track[i][0]
    stoptime = time_track[i][1]
    changed_time = new_timetable[starttime:stoptime,day] - old_timetable[starttime:stoptime,day]
    if 255 in changed_time:
        SendEmail(receiver_email,day)
        print ('changed')
np.savetxt('old_timetable.txt', new_timetable, delimiter=',',fmt='%i')
