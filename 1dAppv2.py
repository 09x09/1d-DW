# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 09:15:50 2018

@author: TTM
"""
import matplotlib.pyplot as plt
import time
import kivy
kivy.require("1.10.0")

from firebase import firebase

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from kivy.graphics import Rectangle

#configure firebase
url = "https://d-kivy.firebaseio.com/"
token = "aRGawiS0B9hfyqAw1VfwwXZZkdYjBOKuQRuZ8MLD"

firebase = firebase.FirebaseApplication(url, token)

version = "Dustbin Manager - Beta 1.30"

#screen manager functions. Global as it is required in multiple screens
def callback1(instance):
    sm.switch_to(Level1("Level1"))
    
def callback2(instance):
    sm.switch_to(Level2("Level2"))
    
def callback3(instance):
    sm.switch_to(Level3("Level3"))
    
def callback4(instance):
    sm.switch_to(Level4("Level4"))
    
def callback5(instance):
    sm.switch_to(Full("Full"))
    
def update(screen):
    sm.switch_to(updateScreen("uS"))
    string = "sm.switch_to(" + screen +")"
    def callback(screen):        
        return eval(string)
        
    Clock.schedule_once(callback,3)
    
class HomeButton(Button):
    def __init__(self):
        super(HomeButton, self).__init__()
        self.size_hint = (1,.05)
        self.text = "Home"        
        
    def on_press(self):
        sm.switch_to(HomeScreen("home"))

#label to countdown to next update        
class updateLabel(Label):
    def __init__(self, name):
        super(updateLabel, self).__init__()
        self.size_hint = (1,0.05)
        self.text = "loading" 
        self.minDiff = 0
        self.secDiff = 0
        self.name = name
        Clock.schedule_interval(self.getCurrentTime,1)
 
        
    def getCurrentTime(self,dt):
        currentTime = time.localtime()
        currentMin = currentTime[4]
        currentSec = currentTime[5]
        
 #make the timer count down instead of up       
        self.minDiff = 29 - currentMin % 30
        self.secDiff = 60 - currentSec % 60
        
        if self.secDiff == 60:
            self.secDiff = 0
            
        if self.secDiff == 29 and self.minDiff == 0:
            self.text = "updating..."
            update(self.name)
            
        
        output = "Next update in " + "{:02d}".format(self.minDiff) + ":" + "{:02d}".format(self.secDiff)
        if self.text == "updating...":
            self.text = "done"
            
        else:
            self.text = output
                      
class loadingLabel(Label):
    def __init__(self):
        super(loadingLabel, self).__init__()
        self.text = "updating" 
        Clock.schedule_interval(self.callback,1)
        self.counter = 0
        
    def callback(self,dt):
        if "..." in self.text:
            self.text = "updating"

        else:
            self.text += "."
            
class updateScreen(Screen):
    def __init__(self, name):
        super(updateScreen, self).__init__()
        self.add_widget(loadingLabel())

        
class forceUpdate(Button):
    def __init__(self, name):
        super(forceUpdate, self).__init__()
        self.text = "Force Update"
        self.size_hint = (1, 0.05)
        self.name = name
        
    def on_press(self):
        update(self.name)

class dustbin(Button):
    def __init__(self,name, data):
        super(dustbin, self).__init__()
        self.name = name
        self.text = name
        self.data = data
        self.status = data[-1] #last measured state

        #set background color based on the last measured state of the bin
        if self.status <= 25:
            self.background_color = [0,255,0,1]
        elif self.status <= 60:
            self.background_color = [255,255,0,1]
        elif self.status <= 80:
            self.background_color = [255,165,0,1]
        elif self.status <= 100:
            self.background_color = [255,0,0,1]
            self.text += " FULL"

    def on_release(self):
        stat = StatusScreen(self.text, self.data)
        stat.open()
        
        
class StatusScreen(Popup):
    def __init__(self, name, data):
        super(StatusScreen, self).__init__()
        self.size_hint = (.9,.9)
        self.title = name

        last_cleared = 0

        clear_text = ""
        
        for i in range(1, len(data)):
            if data[-i]-data[-i-1] < 0:
                last_cleared = i-1
                break
            
            else:
                last_cleared = -1
                
        days_cleared = last_cleared//24
                
        if last_cleared == -1:
            clear_text = "Bin has not been cleared"
            
        else:
            if days_cleared == 0:
                clear_text = "Bin was last cleared "+ str(last_cleared) + " hours ago"
            else:
                clear_text = "Bin was last cleared "+ str(days_cleared) + " days and " + str(last_cleared-days_cleared*24)+ " hours ago"

        box = BoxLayout(orientation = "vertical")
        
        #plot the measured data in a graph
        plt.clf()
        plt.plot(data)
        
        label = Label(text = "7 Day Statistics", size_hint = (1, 0.1))
        label1 = Label(text = clear_text, size_hint = (1, 0.1))
        
        box.add_widget(label)
        box.add_widget(FigureCanvasKivyAgg(plt.gcf()))
        box.add_widget(label1)
        
        with self.canvas:
            self.add_widget(box)
                        

        
class HomeScreen(Screen):
    def __init__(self, name):
        super(HomeScreen, self).__init__()
    
        layout = BoxLayout(orientation = "vertical")
        layout1 = GridLayout(rows = 5)
        
        #creatw menu buttons
        btn1 = Button(text = "Level 1", background_color = [0.686,0.933,0.933,1])
        btn1.bind(on_press = callback1)
        
        btn2 = Button(text = "Level 2", background_color = [0.690,0.878,0.902,1])
        btn2.bind(on_press = callback2)
        
        btn3 = Button(text = "Level 3", background_color = [0.678,0.847,0.902,1])
        btn3.bind(on_press = callback3)
        
        btn4 = Button(text = "Level 4", background_color = [0.690,0.769,0.871,1])
        btn4.bind(on_press = callback4)
        
        btn5 = Button(text = "Full bins", background_color = [0.275,0.510,0.706,1])
        btn5.bind(on_press = callback5)
        
        label = Label(text = "Overview", font_size = "20sp", size_hint = (1, 0.2))
        
        layout1.add_widget(btn1)
        layout1.add_widget(btn2)
        layout1.add_widget(btn3)
        layout1.add_widget(btn4)
        layout1.add_widget(btn5)
        
        layout.add_widget(label)
        layout.add_widget(layout1)
        layout.add_widget(updateLabel("HomeScreen(\"HS\")"))
        layout.add_widget(forceUpdate("HomeScreen(\"HS\")"))
        
        with self.canvas:
            self.add_widget(layout)

class Map(FloatLayout):
     def __init__(self, source):
        super(Map, self).__init__()
        self.source = source
        
        with self.canvas.before:
            self.rect = Rectangle(size = self.size, pos = self.pos ,source = self.source)
        
        def update_rect(instance,value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
            
        self.bind(pos= update_rect, size = update_rect)
        
#Create screens for each floor
class Level1(Screen):
    def __init__(self, name):
        super(Level1, self).__init__()
        layout = BoxLayout(orientation = "vertical")
        layout2 = GridLayout(rows = 2, size_hint =(1,0.2))        
        home = HomeButton()
        update = updateLabel("Level1(\"L1\")")
        dlist = firebase.get("/Level 1")
        dlist_keys = list(firebase.get("/Level 1").keys())
        layout3 = Map("level1.jpeg")
        
        #create the same number of dustbins as the number of nodes in \Level1
        #each bin is belongs to the class dustbin()
        for i in dlist_keys:
            dbin = dustbin(i,dlist[i])
            layout2.add_widget(dbin)
            
        label2 = Label(text = name , size_hint = (1, 0.1))
        
        layout.add_widget(label2)
        layout.add_widget(layout3)
        layout.add_widget(layout2)
        
        layout.add_widget(update)
        layout.add_widget(forceUpdate("Level1(\"L1\")"))
        layout.add_widget(home)
        
        with self.canvas:         
            self.add_widget(layout)
                   

class Level2(Screen):
    def __init__(self, name):
        super(Level2, self).__init__()
        layout = BoxLayout(orientation = "vertical")
        layout2 = GridLayout(rows = 2, size_hint =(1,0.2))        
        home = HomeButton()
        update = updateLabel("Level2(\"L2\")")
        dlist = firebase.get("/Level 2")
        dlist_keys = list(firebase.get("/Level 2").keys())
        layout3 = Map("level2.jpeg")
        
        for i in dlist_keys:
            dbin = dustbin(i,dlist[i])
            layout2.add_widget(dbin)
            
        label2 = Label(text = name , size_hint = (1, 0.1))
        
        layout.add_widget(label2)
        layout.add_widget(layout3)
        layout.add_widget(layout2)
        
        layout.add_widget(update)
        layout.add_widget(forceUpdate("Level2(\"L2\")"))
        layout.add_widget(home)
        
        with self.canvas:         
            self.add_widget(layout)

class Level3(Screen):
    def __init__(self, name):
        super(Level3, self).__init__()
        layout = BoxLayout(orientation = "vertical")
        layout2 = GridLayout(rows = 2, size_hint =(1,0.2))        
        home = HomeButton()
        update = updateLabel("Level3(\"L3\")")
        dlist = firebase.get("/Level 3")
        dlist_keys = list(firebase.get("/Level 3").keys())
        layout3 = Map("level3.jpeg")
        
        for i in dlist_keys:
            dbin = dustbin(i,dlist[i])
            layout2.add_widget(dbin)
            
        label2 = Label(text = name , size_hint = (1, 0.1))
        
        layout.add_widget(label2)
        layout.add_widget(layout3)
        layout.add_widget(layout2)
        
        layout.add_widget(update)
        layout.add_widget(forceUpdate("Level3(\"L3\")"))
        layout.add_widget(home)
        
        with self.canvas:         
            self.add_widget(layout)

class Level4(Screen):
    def __init__(self, name):
        super(Level4, self).__init__()
        layout = BoxLayout(orientation = "vertical")
        layout2 = GridLayout(rows = 2, size_hint =(1,0.2))        
        home = HomeButton()
        update = updateLabel("Level4(\"L4\")")
        dlist = firebase.get("/Level 4")
        dlist_keys = list(firebase.get("/Level 4").keys())
        layout3 = Map("level4.jpeg")
        
        for i in dlist_keys:
            dbin = dustbin(i,dlist[i])
            layout2.add_widget(dbin)
            
        label2 = Label(text = name , size_hint = (1, 0.1))
        
        layout.add_widget(label2)
        layout.add_widget(layout3)
        layout.add_widget(layout2)
        
        layout.add_widget(update)
        layout.add_widget(forceUpdate("Level4(\"L4\")"))
        layout.add_widget(home)
        
        with self.canvas:         
            self.add_widget(layout)

#for ease of view of full bins            
class Full(Screen):
    def __init__(self, name):
        super(Full, self).__init__()
        layout = BoxLayout(orientation = "vertical")
        layout2 = GridLayout(cols = 2)
        home = HomeButton()
        update = updateLabel("Full(\"Full\")")
        dlist = dict()
        searchList = ["/Level 1", "/Level 2", "/Level 3", "/Level 4"]
        
        #get all data from firebase and search for full bins
        for i in searchList:
            bins = firebase.get(i)
            for j in list(bins.keys()):
                if bins[j][-1] > 80:
                    dlist[j] = [i,bins[j]]
                    
        #clean up data and create dustbin() objects out of each set of data 
        for k in list(dlist.keys()):
            dbin = dustbin(k,dlist[k][1])
            dbin.text = dlist[k][0][1::] + " :"+ dbin.name
            layout2.add_widget(dbin)    

        label2 = Label(text = name , size_hint = (1, 0.1))
        
        layout.add_widget(label2)
        layout.add_widget(layout2)
        
        layout.add_widget(update)
        layout.add_widget(forceUpdate("Full(\"Full\")"))
        layout.add_widget(home)
        
        with self.canvas:         
            self.add_widget(layout)                    
        
    
sm = ScreenManager()
sm.add_widget(HomeScreen(name='home'))
sm.add_widget(Level1(name='Level1'))


class TestApp(App):
    def build(self):
        self.title = version
        return sm

if __name__ == '__main__':    
    TestApp().run()