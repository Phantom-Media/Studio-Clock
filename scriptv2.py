import math
import tkinter as tk
import time
import requests
import json
import datetime
import feedparser
from PIL import Image, ImageTk
from threading import Thread
import traceback
import hidden

def now():
    return datetime.datetime.now().astimezone()

file="Logs/"+now().date().isoformat()+" "+now().time().isoformat()[0:8].replace(':','-')+".log"

def pw(*text):
    pout = ""#str(now()) + " "
    with open(file,"a") as f:
        #f.write(str(now())+" ")
        for t in text:
            t=str(t)
            f.write(t+" ")
            pout += t + " "
            f.write("\n")
    print(pout)

def get(url):
    global last_online_time
    try:
        out = requests.get(url)
        last_online_time = now()
        return out
    except (requests.exceptions.ConnectionError) as e:
        pw(now().ctime(), "- get Error - failed to connect")

scriptstart = now()
statusesurl = hidden.SEQUEMATIC
phantommedialogofile = "PhantomRadioSquare.png"
offline = True
last_online_time = None

pw("Script Start")

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


def getstats(url=hidden.STATUSES_URL):
    global newtitle
    global last_fetched
    global listeners
    global description

    getstatuses()

    try:    
        stats = json.loads(get(url).text)
    except (AttributeError) as e:
        pw(now().ctime(), "- getstats Error - Failed to fetch source")
        try:
            newtitle = "- - -  Last Online: " + str(last_online_time.ctime()) + "  - - -"
        except (AttributeError) as e:
            newtitle = "- - -  Last Online: Not Since Boot  - - -"
        listeners = None
        
    last_fetched = now()
    #pw(stats['icestats']['source'])
    try:
        source = stats['icestats']['source']
        if type(source) == dict:
            if source['listenurl'] == hidden.PHANTOM_NEBULA+'/stream':
                newtitle = source['title']
                listeners = source['listeners']
                description = source['server_description']
        elif type(source) == list:
            for i in source:
                if i['listenurl'] == hidden.PHANTOM_NEBULA+'/stream':
                    newtitle = i['title']
                    listeners = i['listeners']
                    description = i['server_description']
                    break
        else:
            pw(now().ctime(), source)
    except (KeyError, NameError) as e:
        pw(now().ctime(), "- getstats Error - Failed to parse source") 
        listeners = None
        description = None
    meta.configure(text=newtitle)

def listenercolours():
    global listeners
    
    try:
        if listeners != None:
            if int(ln['text']) < listeners:
                ln.configure(fg='green')
            elif int(ln['text']) > listeners:
                ln.configure(fg='red')
            else:
                ln.configure(fg='white')
        else: ln.configure(fg='white')
    except (TypeError) as e:
        pw(now().ctime(), "- line 85 -", e)
        ln.configure(fg='white')

    if listeners == None:
        ln.configure(text="0")
    else: ln.configure(text=listeners)
        
def getstatuses():
    global offline
    try:
        statuses = json.loads(get(statusesurl).text.replace("\'",""))
        offline = False
    except (AttributeError) as e:
        pw(now().ctime(), "- getstatuses Error - Failed to fetch source")
        statuses = {'On Air':0,'Mics Live':0}
        offline = True
    
    if statuses['On Air'] == 1:
        onAir.config(bg='green')
    else:
        onAir.config(bg="#013220")

    if statuses['Mics Live'] == 0:
        mics.config(bg='#3a1114')
    elif statuses['Mics Live'] == 1:
        mics.config(bg="red")

    if offline != True:
        s2.config(bg='#683a00')
    else:
        s2.config(bg="orange")

def OnAirToggle():
    statuses = json.loads(get(statusesurl).text)
    if onAir['bg'] == "green":
        onAir.config(bg='#013220')
        statuses['On Air']=0
    else:
        onAir.config(bg="green")
        statuses['On Air']=1
    get(statusesurl.replace('get','change')+'/='+json.dumps(statuses))

def MicsToggle():
    statuses = json.loads(get(statusesurl).text)
    if mics['bg'] == "red":
        mics.config(bg='#3a1114')
        statuses['Mics Live']=0
    else:
        mics.config(bg="red")
        statuses['Mics Live']=1
    get(statusesurl.replace('get','change')+'/='+json.dumps(statuses))

def CtrlToggle():
    statuses = json.loads(get(statusesurl).text)
    if s2['bg'] == "orange":
        s2.config(bg='#683a00')
    else:
        s2.config(bg="orange")
    get(statusesurl.replace('get','change')+'/='+json.dumps(statuses))

def rss(feed="http://feeds.bbci.co.uk/news/rss.xml"):
    global rss_out
    if feed == "latest":
        feed = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"
    elif feed == "int":
        feed = "http://feeds.bbci.co.uk/news/rss.xml?edition=int"
    elif feed == "uk":
        feed = "http://feeds.bbci.co.uk/news/uk/rss.xml"
    elif feed == "world":
        feed = "http://feeds.bbci.co.uk/news/world/rss.xml"
    elif feed == "england":
        feed = "http://feeds.bbci.co.uk/news/england/rss.xml"
    elif feed == "ni":
        feed = "http://feeds.bbci.co.uk/news/northern_ireland/rss.xml"
    elif feed == "scotland":
        feed = "http://feeds.bbci.co.uk/news/scotland/rss.xml"
    elif feed == "wales":
        feed = "http://feeds.bbci.co.uk/news/wales/rss.xml"
        
    global response

    response = feedparser.parse(feed)
    if response['bozo'] == True:
        rss_out[0] = None
        rss_out[1] = None
        rss_out[2] = None
        rss_out[3] = None
        rss_out[4] = None
        
    else:
        n = 0
        x = 0
        while x <= 4:
            try:
                if "World Cup" not in response['entries'][n]['title']:
                    rss_out[x] = {'title':response['entries'][n]['title'],'summary':response['entries'][n]['summary']}
                    x += 1
                n += 1
            except IndexError as e:
                pw(now().ctime(), "- line 184 -", e)
                rss_out[x] = None
                x += 1
    #pw(rss_out)    
    return rss_out

def getweather(lat=52.9228, lon=-1.4766, units="metric", appid=hidden.WEATHER_KEY):
    url = "https://api.openweathermap.org/data/2.5/weather?lat="+str(lat)+"&lon="+str(lon)+"&units="+units+"&appid="+appid
    try:
        response = json.loads(get(url).text.replace("\'",""))
        return response
    except (AttributeError) as e:
        pw(now().ctime(), "- getweather Error - Failed to fetch source")
    return None    

def setweather():
    locations = {'derby':{'lat':52.9228, 'lon':-1.4766},
                 'london':{'lat':51.5085, 'lon':-0.1257},
                 'belfast':{'lat':54.5833, 'lon':-5.9333},
                 'cardiff':{'lat':51.48, 'lon':-3.18},
                 'edinburgh':{'lat':55.9521, 'lon':-3.1965}
                 }
    string = ""
    for (i, j) in locations.items():
        try:
            j['temp'] = round(getweather(lat=j['lat'], lon=j['lon'])['main']['temp'],1)
        except TypeError as e:
            j['temp'] = None
            #pw(now().ctime(),'- line 214 -',e)

        if j['temp'] == None:
            string += "\n"
        else:
            string += str(j['temp']) + "°С\n"
            
        
    weather.config(text=string)
    #except (TypeError) as e:
     #   pw(now().ctime(), "- line 214 -", e)
      #  return None

def wordclock(time=None):
    if time == None:
        time = now()
        
    hourlook = {
        0:"Midnight",
        1:"One",
        2:"Two",
        3:"Three",
        4:"Four",
        5:"Five",
        6:"Six",
        7:"Seven",
        8:"Eight",
        9:"Nine",
        10:"Ten",
        11:"Eleven",
        12:"Twelve",
        13:"One",
        14:"Two",
        15:"Three",
        16:"Four",
        17:"Five",
        18:"Six",
        19:"Seven",
        20:"Eight",
        21:"Nine",
        22:"Ten",
        23:"Eleven",
        24:"Midnight"
    }

    minlook = {
        0:"o'clock",
        1:"One minute",
        2:"Two minutes",
        3:"Three minutes",
        4:"Four minutes",
        5:"Five minutes",
        6:"Six minutes",
        7:"Seven minutes",
        8:"Eight minutes",
        9:"Nine minutes",
        10:"Ten",
        11:"Eleven minutes",
        12:"Twelve minutes",
        13:"Thirteen minutes",
        14:"Fourteen minutes",
        15:"Quarter",
        16:"Sixteen minutes",
        17:"Seventeen minutes",
        18:"Eighteen minutes",
        19:"Nineteen minutes",
        20:"Twenty",
        21:"Twenty-one minutes",
        22:"Twenty-two minutes",
        23:"Twenty-three minutes",
        24:"Twenty-four minutes",
        25:"Twenty-five minutes",
        26:"Twenty-six minutes",
        27:"Twenty-seven minutes",
        28:"Twenty-eight minutes",
        29:"Twenty-nine minutes",
        30:"Half"
    }
    
    if time.minute == 0:
        out = hourlook[time.hour] + " " + minlook[time.minute]
    elif time.minute <= 30:
        out = minlook[time.minute] + " past " + hourlook[time.hour]
    else:
        out = minlook[60-time.minute] + " to " + hourlook[time.hour + 1]

    return out

try:
    my_w = tk.Tk()
    cl = tk.Label(my_w, text="Current\nListeners", bg="black", fg="white", font=("Arial", 50))
    cl.place(relx=0.9, rely=0.425, anchor='center')
    ln = tk.Label(my_w, text="0", bg="black", fg="white", font=("Arial", 80,  'bold'))
    ln.place(relx=0.9, rely=0.575, anchor='center')
    meta = tk.Label(my_w, wraplength=1600, anchor='center', height=2, text="", bg="black", fg="white", font=("Arial", 40))
    meta.place(relx=0.5835, rely=0.99, anchor='s')
    studio = tk.Label(my_w, text="Phantom Radio - Studio 1", bg="black", fg="white", font=("Arial", 50, 'bold'))
    studio.place(relx=0.5, rely=0.05, anchor='center')
    onAir = tk.Button(my_w, width=6, height=2, text="On\nAir", bg="green",fg="white", font=("Arial", 50, 'bold'), command=OnAirToggle)
    onAir.place(relx=0.1, rely=0.35, anchor='center')
    mics = tk.Button(my_w, width=6, height=2, text="Mics\nLive", bg="red",fg="white", font=("Arial", 50, 'bold'), command=MicsToggle)
    mics.place(relx=0.1, rely=0.6, anchor='center')
    s2 = tk.Button(my_w, width=6, height=2, text="Screen\nError" ,bg="#683a00",fg="white", font=("Arial", 50, 'bold'), command=CtrlToggle)
    s2.place(relx=0.1, rely=0.85, anchor='center')
    alive = tk.Label(my_w, text=alivetime(),bg="black", fg="white", font=("Arial", 5,  'bold'))
    alive.place(relx=1, rely=1, anchor='se')
    wordcl = tk.Label(my_w, wraplength=425, justify="center", text="Word Clock Text", bg="black", fg="white", font=("Arial", 50))
    wordcl.place(relx=0.85, rely=0.01, anchor='n')
    getstats()
    headlines = tk.Label(my_w, anchor='center', text="Latest Headlines", bg="black", fg="white", font=("Arial", 37, 'bold'))
    headlines.place(relx=0.80, rely=0.75, anchor='s')
    news = tk.Label(my_w, wraplength=750, anchor='center', height=2, text="News Text", bg="black", fg="white", font=("Arial", 30))
    news.place(relx=0.80, rely=0.75, anchor='n')
    newssource = tk.Label(my_w, anchor='center', text="from BBC News", bg="black", fg="white", font=("Arial", 15))
    newssource.place(relx=1, rely=0.85, anchor='e')
    weathertitle = tk.Label(my_w, anchor='center', text="Latest Temps:", bg="black", fg="white", font=("Arial", 30, 'bold'), justify="left")
    weathertitle.place(relx=0.625, rely=0.4, anchor='sw')
    locs = tk.Label(my_w, anchor='center', text="Derby:\nBelfast:\nEdinburgh:\nCardiff:\nLondon:", bg="black", fg="white", font=("Arial", 30), justify="left")
    locs.place(relx=0.625, rely=0.4, anchor='nw')
    weather = tk.Label(my_w, anchor='center', text="", bg="black", fg="white", font=("Arial", 30), justify="right")
    weather.place(relx=0.8, rely=0.4, anchor='ne')
    weathersource = tk.Label(my_w, anchor='center', text="from OpenWeather", bg="black", fg="white", font=("Arial", 15))
    weathersource.place(relx=0.8, rely=0.63, anchor='e')
    listeners
    width,height=800,800 # set the variables 
    c_width,c_height=width-5,height-5 # canvas width height
    d=str(width)+"x"+str(height)+"+3840+0"
    my_w.geometry(d)
    my_w.configure(bg='black')
    my_w.title("Studio 1 Clock")
    sw,sh = my_w.winfo_screenwidth(),my_w.winfo_screenheight()
    #pw("screen1:",sw,sh)
    w,h = 1600,900 
    my_w.geometry('%sx%s+%s+%s'%(w,h,int(sw),0))
    #my_w.attributes("-fullscreen",True)
    #my_w.geometry(d)

    c1 = tk.Canvas(my_w, width=c_width, height=c_height,bg='black',highlightthickness=0)
    c1.place(relx=0.4, rely=0.5, anchor='center')

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
            c1.create_text(t1,t2,fill='white',font=("Arial", 50, 'bold'),text=next(h)) # number added
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
    digital = c1.create_text(width/2,550,text=now().strftime("%H:%M:%S"),fill="red",font=("DSEG7 Classic Mini", 60, 'bold'))

    in_radian = math.radians(in_degree_m)
    x2=x+rm*math.sin(in_radian)
    y2=y-rm*math.cos(in_radian) 
    minute=c1.create_line(x,y,x2,y2,width=15,fill='white')

    in_degree_h=in_degree_h+(in_degree_m*0.0833333)          
    in_radian = math.radians(in_degree_h)
    x2=x+rh*math.sin(in_radian)
    y2=y-rh*math.cos(in_radian)
    hour=c1.create_line(x,y,x2,y2,width=15,fill='white')

    image = Image.open(phantommedialogofile)
    img=image.resize((260, 260))#195))
    my_img=ImageTk.PhotoImage(img)
    logo = tk.Label(my_w, image=my_img, bg="black")
    logo.place(relx=0.1, rely=0.12, anchor='center')

    rss_out = [None,None,None,None,None]
    newsitemno = 0
    newscatno = 0
    rss(feed="latest")
    try:
        news.config(text=rss_out[0]['title'])
    except (TypeError) as e:
            pw(now().ctime(), "- news.config Error - title does not exist")
            news.config(text="Feed Connection Error") 
    headlines.config(text="Latest Headlines")
    setweather()


    def clock():
        listenercolours()
        timedisp = now()
        c1.itemconfigure(digital, text=timedisp.strftime("%H:%M:%S"))
        wordcl.config(text=wordclock())
        alive.config(text=alivetime())

        global in_degree_s,second
        global in_degree_m,minute
        global in_degree_h,hour
        global newsitemno, newscatno

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
            
        if int(timedisp.strftime('%S')) % 15 == 0:
            Thread(target=getstats).start()
            Thread(target=getstatuses).start()
            try:
                if newsitemno == 0:
                    if newscatno == 0:
                        Thread(target=rss, args=("latest",)).start()
                        headlines.config(text="Latest Headlines")
                        newscatno += 1
                    elif newscatno == 1:
                        Thread(target=rss, args=("int",)).start()
                        headlines.config(text="Latest International Headlines")
                        newscatno += 1
                    elif newscatno == 2:
                        Thread(target=rss, args=("uk",)).start()
                        headlines.config(text="Latest UK Headlines")
                        newscatno += 1
                    elif newscatno == 3:
                        Thread(target=rss, args=("world",)).start()
                        headlines.config(text="Latest World Headlines")
                        newscatno = 0
                news.config(text=rss_out[newsitemno]['title'])
                if newsitemno == 4:
                    newsitemno = 0
                else:
                    newsitemno += 1
            except (TypeError) as e:
                pw(now().ctime(), "- news.config Error - title does not exist")
                news.config(text="Feed Connection Error")
                if newsitemno == 4:
                    newsitemno = 0
                else:
                    newsitemno += 1
                
        if int(timedisp.strftime('%S')) == 0:
            Thread(target=setweather).start()
        
        c1.after(1000,clock) # timer calling recrusive after 1 second
            
    my_w.attributes("-fullscreen", True)
    clock() # calling to start 
    my_w.mainloop()

except:
    pw(traceback.format_exc())
    
