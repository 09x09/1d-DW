# -*- coding: utf-8 -*-
"""
Created on Mon Apr 16 08:26:03 2018

@author: TTM
"""
from kivy.config import Config
Config.set("kivy", "keyboard_mode","systemanddock") #enables keyboard on Rpi

import time
import kivy
kivy.require("1.10.0")

from firebase import firebase

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.togglebutton import ToggleButton
from kivy.clock import Clock
from kivy.uix.textinput import TextInput

import re
import RPi.GPIO as GPIO

#set up GPIO pins, firebase
GPIO.setmode(GPIO.BCM)

url = "https://d-kivy.firebaseio.com/"
token = "aRGawiS0B9hfyqAw1VfwwXZZkdYjBOKuQRuZ8MLD"

firebase = firebase.FirebaseApplication(url, token)

def close(instance): 
    GPIO.cleanup()
    App.get_running_app().stop()
    Window.close()
    
full = 16 #distance we consider the dustbin to be full
empty = 84 #distance from sensor to bottom of bin

TRIG = 20
ECHO = 25
OPEN = 24
CLOSE = 21

GPIO.setup(TRIG, GPIO.OUT) 
GPIO.setup(ECHO,GPIO.IN)

GPIO.setup(CLOSE, GPIO.OUT)
GPIO.output(CLOSE, GPIO.HIGH)
time.sleep(1)
GPIO.setup(OPEN, GPIO.OUT)
GPIO.output(OPEN, GPIO.HIGH)

def measure():
    GPIO.output(TRIG, False)
    time.sleep(2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG,False)
    
    while GPIO.input(ECHO) == 0:
        startTime = time.time()
        
    while GPIO.input(ECHO) == 1:       
        endTime = time.time()
        
    duration = endTime - startTime
    distance = round((duration * 17150),2)
    
    amount = round(((empty-distance)/(empty-full)),1) #calculate the fraction occupied by trash
    percentageFull = int(amount*100) #convert to percentage
    
    return percentageFull

def closeCover():
    GPIO.output(CLOSE, GPIO.LOW)#relay requires low input to trigger
    time.sleep(2.1)
    GPIO.output(CLOSE, GPIO.HIGH)
    time.sleep(1)

def openCover():
    GPIO.output(OPEN, GPIO.LOW)
    time.sleep(2.1)
    GPIO.output(OPEN, GPIO.HIGH)
    time.sleep(1)


class updateLabel(Label):
    def __init__(self):
        super(updateLabel, self).__init__()
        self.size_hint = (1,0.15)
        self.text = "loading" 
        self.minDiff = 0
        self.secDiff = 0
        self.name = ""
        self.floor = ""
        self.value = 0
        Clock.schedule_interval(self.getCurrentTime,1)

        
    def getCurrentTime(self,dt):
        currentTime = time.localtime()
        currentMin = currentTime[4]
        currentSec = currentTime[5]
        
        self.minDiff = 29 - currentMin % 30
        self.secDiff = 60 - currentSec % 60
        
        if self.secDiff == 60:
            self.secDiff = 0

            
        if self.secDiff == 29 and self.minDiff == 0:
            self.text = "updating..."
            
        output = "Next update in " + "{:02d}".format(self.minDiff) + ":" + "{:02d}".format(self.secDiff)
        if self.text == "updating...":
            self.text = "done"
            
        else:
            self.text = output

class Config(Popup):
    def __init__(self):
        super(Config, self).__init__() 
        self.size_hint = (0.8,0.8)
        self.title = "Settings"
        self.name = "default"
        self.level = "Level 1"
        layout = FloatLayout()
        formLayout = BoxLayout(orientation = "vertical", size_hint =(0.6,0.6), pos_hint = {"top":0.8, "right": 0.8})
        inputLayout = GridLayout(cols = 2)
        buttonLayout = GridLayout(cols = 4, size_hint = (1,0.8))
        
        label1= Label(text = "Name")
        
        textBox1 = TextInput(text = "Enter dustbin name", multiline = False)
        textBox1.bind(on_text_validate= self.on_enter)
        
        inputLayout.add_widget(label1)
        inputLayout.add_widget(textBox1)
        
        for i in range(1,5):
            floor = "Level " + str(i)
            btn = ToggleButton(text = floor, group = "Floors")
            if self.name == btn.text:
                btn.state = "down"
                
            def setLevel(instance):
                self.level = floor
            
            btn.bind(on_release = setLevel)
                
            buttonLayout.add_widget(btn)
        
        formLayout.add_widget(inputLayout)
        formLayout.add_widget(buttonLayout)

        layout.add_widget(formLayout) 
        
        with self.canvas:
            self.add_widget(layout)
    
    def on_enter(self, instance):
        self.name = instance.text
            
class status(Label):
    def __init__(self):
        super(status, self).__init__()
        self.text = "[size=80]0[/size]" 
        self.markup = True
        
#display color based on how full the bin is        
        with self.canvas.before:
            regex = "([0-9]{1,})(?=\[)"
            value = re.findall(regex, self.text)
            print(value)
            if int(value[0]) <= 25:
                Color(0,1,0)
            elif int(value[0]) <= 60:
                Color(1,1,0)
            elif int(value[0]) <= 80:
                Color(1,0.4,0)
            elif int(value[0]) <= 100 or self.text == "[size=80]FULL[/size]":
                Color(1,0,0)
                self.text = "[size=80]FULL[/size]"
        
            self.rect = Rectangle(pos = self.pos, size = self.size)
        
        def update_rect(instance,value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
            
        self.bind(pos= update_rect, size = update_rect)      

class Home(BoxLayout):
    def __init__(self):
        super(Home, self).__init__()
        self.orientation = "vertical"
        
        self.setting = Config()
        self.nextUpdate = updateLabel()
        self.statusLabel = status()
   
        btn2 = Button(text = "Force update", size_hint = (1, 0.15)) 
        btn2.bind(on_press = self.update)
        
        btn4 = Button(text = "Settings", size_hint = (1, 0.15))
        btn4.bind(on_press = self.setting.open)
    
        btn3 = Button(text = "Quit", size_hint=(1,0.15))
        btn3.bind(on_press = close)
        
        with self.canvas:
            self.add_widget(self.statusLabel)
            self.add_widget(self.nextUpdate)
            self.add_widget(btn2)
            self.add_widget(btn4)
            self.add_widget(btn3)

        Clock.schedule_interval(self.autoUpdater,1)

    def autoUpdater(self,dt):
        if self.nextUpdate.secDiff == 29 and self.nextUpdate.minDiff == 0:
            self.update
    
    def update(self, instance = "1"):       
        nodeLevel = "/" + self.setting.level #start extracting data from firebase
        getValues = firebase.get(nodeLevel)
        stat = measure()
        name = self.setting.name
        if name not in getValues.keys(): #create a new key-value pair for new bins
            getValues[name] = []
            
        getValues[name].append(stat)
        firebase.put("/", self.setting.level,getValues)

#display sensor readings
        if self.statusLabel.text == "[size=80]FULL[/size]" and int(stat) <=25:
            openCover()

        if int(stat) <= 80:
            self.statusLabel.text = "[size=80]" + str(stat) + "%[/size]"

        else:
            self.statusLabel.text = "[size=80]FULL[/size]"
            closeCover()
            
        with self.statusLabel.canvas.before:         
            regex = "([0-9]{1,})(?=%|\[)"
            value = re.findall(regex, self.statusLabel.text)
            try:
                if int(value[0]) <= 25:
                    Color(0,1,0)
                elif int(value[0]) <= 60:
                    Color(1,1,0)
                elif int(value[0]) <= 80:
                    Color(1,0.4,0)
                
            except:
                Color(1,0,0)
        
            self.statusLabel.rect = Rectangle(pos = self.statusLabel.pos, size = self.statusLabel.size)
        
class TestApp(App):
    def build(self):
        return Home()

if __name__ == '__main__':
    TestApp().run()
