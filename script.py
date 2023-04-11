import math
import tkinter as tk
import time
import requests
import json
import datetime 

def now():
    return datetime.datetime.now().astimezone()

scriptstart = now()
statusesurl = "https://sequematic.com/variable-get/3805/A389BC3C78/Studio Statuses"

def alivetime():
    global scriptstart
    delta = now() - scriptstart
    days = delta.days
    hours = int(delta.seconds / 3600)
    minutes = int(delta.seconds / 60) - (hours * 60)
    seconds = delta.seconds - (hours * 3600) - (minutes * 60)
    days = str(days)
    hours = "0" + str(hours)
    minutes = "0" + str(minutes)
    seconds = "0" + str(seconds)
    out = days+":"+hours[-2:]+":"+minutes[-2:]+":"+seconds[-2:]
    return "Uptime: "+out

def getstats(url='https://phantommedia.radioca.st/status-json.xsl'):
    global newtitle
    global last_fetched
    global stats
    global listeners
    global description

    getstatuses()
        
    try:
        stats = json.loads(requests.get(url).text)
        last_fetched = now()
        #print(stats['icestats']['source'])
        source = stats['icestats']['source']
        if type(source) == dict:
            if source['listenurl'] == 'http://nebula.shoutca.st:8491/stream':
                try:
                    newtitle = source['title']
                    listeners = source['listeners']
                    description = source['server_description']
                except (NameError) as e:
                    print(now(), e)
        elif type(source) == list:
            for i in source:
                if i['listenurl'] == 'http://nebula.shoutca.st:8491/stream':
                    newtitle = i['title']
                    listeners = i['listeners']
                    description = i['server_description']
                    break
        else:
            print(now(), source)
    except (UnicodeEncodeError, ConnectionRefusedError, TimeoutError, requests.exceptions.ConnectionError) as error:
        print(now(), error)
    meta.configure(text=newtitle)
    ln.configure(text=listeners)
    if int(ln['text']) < listeners:
        ln.configure(fg='green')
    elif int(ln['text']) > listeners:
        ln.configure(fg='red')
    else:
        ln.configure(fg='white')

def getstatuses():
    statuses = json.loads(requests.get(statusesurl).text)
    
    if statuses['On Air'] == 1:
        onAir.config(bg='green')
    else:
        onAir.config(bg="#013220")

    if statuses['Mics Live'] == 0:
        mics.config(bg='#3a1114')
    elif statuses['Mics Live'] == 1:
        mics.config(bg="red")

    if statuses['Studio In Control'] == 1:
        s2.config(bg='#683a00')
    else:
        s2.config(bg="orange")

def OnAirToggle():
    statuses = json.loads(requests.get(statusesurl).text)
    if onAir['bg'] == "green":
        onAir.config(bg='#013220')
        statuses['On Air']=0
    else:
        onAir.config(bg="green")
        statuses['On Air']=1
    requests.get(statusesurl.replace('get','change')+'/='+json.dumps(statuses))

def MicsToggle():
    statuses = json.loads(requests.get(statusesurl).text)
    if mics['bg'] == "red":
        mics.config(bg='#3a1114')
        statuses['Mics Live']=0
    else:
        mics.config(bg="red")
        statuses['Mics Live']=1
    requests.get(statusesurl.replace('get','change')+'/='+json.dumps(statuses))

def CtrlToggle():
    statuses = json.loads(requests.get(statusesurl).text)
    if s2['bg'] == "orange":
        s2.config(bg='#683a00')
        statuses['Studio In Control']=1
    else:
        s2.config(bg="orange")
    requests.get(statusesurl.replace('get','change')+'/='+json.dumps(statuses))

my_w = tk.Tk()
ln = tk.Label(my_w, text="Current\nListeners",bg="black",fg="white",font=("Arial", 50))
ln.place(relx=0.85, rely=0.425, anchor='center')
ln = tk.Label(my_w, text="0",bg="black",fg="white",font=("Arial", 80,  'bold'))
ln.place(relx=0.85, rely=0.575, anchor='center')
meta = tk.Label(my_w, text="",bg="black",fg="white",font=("Arial", 40))
meta.place(relx=0.5, rely=0.95, anchor='center')
studio = tk.Label(my_w, text="Phantom Radio - Studio 1",bg="black",fg="white",font=("Arial", 50, 'bold'))
studio.place(relx=0.5, rely=0.05, anchor='center')
onAir = tk.Button(my_w, width=6, height=3, text="On\nAir",bg="green",fg="white",font=("Arial", 50, 'bold'), command=OnAirToggle)
onAir.place(relx=0.1, rely=0.2, anchor='center')
mics = tk.Button(my_w, width=6, height=3, text="Mics\nLive",bg="red",fg="white",font=("Arial", 50, 'bold'), command=MicsToggle)
mics.place(relx=0.1, rely=0.5, anchor='center')
s2 = tk.Button(my_w, width=6, height=3, text="Not In\nCtrl",bg="#683a00",fg="white",font=("Arial", 50, 'bold'), command=CtrlToggle)
s2.place(relx=0.1, rely=0.8, anchor='center')
alive = tk.Label(my_w, text=alivetime(),bg="black",fg="white",font=("Arial", 5,  'bold'))
alive.place(relx=1, rely=1, anchor='se')
getstats()
#image1 = Image.open(phantommedialogofile).resize((250, 250), Image.ANTIALIAS)
#logo = ImageTk.PhotoImage(image1)
#my_w.tk.call('tk', 'scaling',200)
width,height=875,875 # set the variables 
c_width,c_height=width-5,height-5 # canvas width height
d=str(width)+"x"+str(height)+"+3840+0"
my_w.geometry(d)
my_w.configure(bg='black')
my_w.title("Studio 1 Clock")
sw,sh = my_w.winfo_screenwidth(),my_w.winfo_screenheight()
#print("screen1:",sw,sh)
w,h = 1600,900 
my_w.geometry('%sx%s+%s+%s'%(w,h,int(sw),0))
#my_w.attributes("-fullscreen",True)
#my_w.geometry(d)

c1 = tk.Canvas(my_w, width=c_width, height=c_height,bg='black',highlightthickness=0)
c1.place(relx=0.5, rely=0.5, anchor='center')

x,y=width/2,height/2 # center 
x1,y1,x2,y2=x,y,x,10 # second needle

center=c1.create_oval(x-8,y-8,x+8,y+8,fill='white')

r1=width*7/15 # dial lines for one minute 
r2=width*7/20 # for hour numbers  after the lines 
rs=width*7/20 # length of second needle 
rm=width*4/11 # length of minute needle
rh=width*4/16 # lenght of hour needle

in_degree = 0
in_degree_s=int(time.strftime('%S')) *6 # local second 
in_degree_m=int(time.strftime('%M'))*6 # local minutes  
in_degree_h=int(time.strftime('%I')) * 30 # 12 hour format

if(in_degree_h==360):
    in_degree_h=0 # adjusting 12 O'clock to 0 
h=iter(['12','1','2','3','4','5','6','7','8','9','10','11'])
for i in range(0,60):
    in_radian = math.radians(in_degree)
    if(i%5==0): 
        ratio=1-0.125 # Long marks ( lines )
        t1=x+r2*math.sin(in_radian) # coordinate to add text ( hour numbers )
        t2=x-r2*math.cos(in_radian) # coordinate to add text ( hour numbers )
        c1.create_text(t1,t2,fill='white',font=("Arial", 60, 'bold'),text=next(h)) # number added
    else:
        ratio=1-0.050 # small marks ( lines )
    
    x1=x+ratio*r1*math.sin(in_radian)
    y1=y-ratio*r1*math.cos(in_radian)
    x2=x+r1*math.sin(in_radian)
    y2=y-r1*math.cos(in_radian)
    if(i%5==0):
        c1.create_line(x1,y1,x2,y2,width=10,fill="white")
    else:
        c1.create_line(x1,y1,x2,y2,width=10,fill="red")
    in_degree=in_degree+6 # increment for next segment
    
in_radian = math.radians(in_degree_s) 
x2=x+rs*math.sin(in_radian)
y2=y-rs*math.cos(in_radian)
second=c1.create_line(x,y,x2,y2,fill='red',width=5) # draw the second needle
digital = c1.create_text(width/2,600,text=now().strftime("%H:%M:%S"),fill="red",font=("DSEG7 Classic Mini", 60, 'bold'))

in_radian = math.radians(in_degree_m)
x2=x+rm*math.sin(in_radian)
y2=y-rm*math.cos(in_radian) 
minute=c1.create_line(x,y,x2,y2,width=15,fill='white')

in_degree_h=in_degree_h+(in_degree_m*0.0833333)          
in_radian = math.radians(in_degree_h)
x2=x+rh*math.sin(in_radian)
y2=y-rh*math.cos(in_radian)
hour=c1.create_line(x,y,x2,y2,width=15,fill='white')

def clock():
    timedisp = now()
    c1.itemconfigure(digital, text=timedisp.strftime("%H:%M:%S"))
    alive.config(text=alivetime())

    global in_degree_s,second
    global in_degree_m,minute
    global in_degree_h,hour

    in_degree_h=(int(timedisp.strftime('%I')) * 30) + (int(timedisp.strftime('%M')) * 0.5)
    in_radian = math.radians(in_degree_h) # in radian 
    c1.delete(hour) # deleting hour needle 
    x2=x+rh*math.sin(in_radian) # Horizontal coordinate for outer edge
    y2=y-rh*math.cos(in_radian) # vertical coordinate for outer adge 
    hour=c1.create_line(x,y,x2,y2,width=15,fill='white')
    if(in_degree_h>=360):
        in_degree_h=0

    in_degree_m=(int(timedisp.strftime('%M'))*6)# + (int(time.strftime('%S')) * 0.5 * 0.2) # increment for each segment 
    in_radian = math.radians(in_degree_m) # coverting to radian 
    c1.delete(minute) # delete the previous needle
    x2=x+rm*math.sin(in_radian) # Horizontal coordinate of outer edge
    y2=y-rm*math.cos(in_radian) # vertical coordinate of outer dege
    minute=c1.create_line(x,y,x2,y2,width=15,fill='white')
    
    in_degree_s=int(timedisp.strftime('%S')) *6
    in_radian = math.radians(in_degree_s)
    c1.delete(second) # delete the needle 
    x2=x+rs*math.sin(in_radian) # Horizontal coordinate of outer edge
    y2=y-rs*math.cos(in_radian) # vertical coordinate of outer adge
    second=c1.create_line(x,y,x2,y2,fill='red',width=5)
    if(in_degree_s==0): # one rotattion is over if reached 360 
        in_degree_s=0 # start from zero angle again 
    in_degree_s=in_degree_s+6 # increment of one segment is 6 degree
        
    if int(timedisp.strftime('%S')) % 30 == 0:
        getstats()
    elif int(timedisp.strftime('%S')) % 15 == 0:
        getstatuses()
    
    c1.after(1000,clock) # timer calling recrusive after 1 second
        
my_w.attributes("-fullscreen", True)
clock() # calling to start 
my_w.mainloop()

