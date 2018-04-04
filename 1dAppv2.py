# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 09:15:50 2018

@author: TTM
"""

import kivy
kivy.require("1.10.0")

from firebase import firebase

from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.popup import Popup

from kivy.uix.screenmanager import ScreenManager, Screen
#from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from kivy.graphics import Color, Rectangle, Ellipse

url = "https://d-kivy.firebaseio.com/"
token = "aRGawiS0B9hfyqAw1VfwwXZZkdYjBOKuQRuZ8MLD"

firebase = firebase.FirebaseApplication(url, token)

def callback1(instance):
    sm.switch_to(Level1("Level 1"))
    
def callback2(instance):
    sm.switch_to(Level2("Level 2"))
    
def callback3(instance):
    sm.switch_to(Level3("Level 3"))
    
def callback4(instance):
    sm.switch_to(Level4("Level 4"))
    
version = "Dustbin Manager - Beta 1.10"

class HomeButton(Button):
    def __init__(self):
        super(HomeButton, self).__init__()
        self.size_hint = (.05,.05)
        self.text = "Home"        
        
    def on_press(self):
        sm.switch_to(HomeScreen("home"))
        
class dustbin(Button):
    def __init__(self,name, status):
        super(dustbin, self).__init__()
        self.text = name
        self.status = status
        
        if status <= 25:
            self.background_color = [0,255,0,1]
        elif status <= 60:
            self.background_color = [255,255,0,1]
        elif status <= 80:
            self.background_color = [255,165,0,1]
        elif status <= 100:
            self.background_color = [255,0,0,1]    

        
    def on_release(self):
        stat = StatusScreen(self.text)
        stat.open()

class StatusScreen(Popup):
    def __init__(self, name):
        super(StatusScreen, self).__init__()
        self.content = Label(text = "hello")
        self.size_hint = (.9,.9)
        self.title = name                 

class HomeScreen(Screen):
    def __init__(self, name):
        super(HomeScreen, self).__init__()
    
        layout = BoxLayout(orientation = "vertical")
        layout1 = GridLayout(cols = 2)
        
        btn1 = Button(text = "Level 1")
        btn1.bind(on_press = callback1)
        
        btn2 = Button(text = "Level 2")
        btn2.bind(on_press = callback2)
        
        btn3 = Button(text = "Level 3")
        btn3.bind(on_press = callback3)
        
        btn4 = Button(text = "Level 4")
        btn4.bind(on_press = callback4)
        
        label = Label(text = "Overview", font_size = "20sp", size_hint = (1, 0.2))
        
        layout1.add_widget(btn1)
        layout1.add_widget(btn2)
        layout1.add_widget(btn3)
        layout1.add_widget(btn4)
        
        layout.add_widget(label)
        layout.add_widget(layout1)
        
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
        
#class updateLabel(Label):

class Level1(Screen):
    def __init__(self, name):
        super(Level1, self).__init__()
        layout = BoxLayout(orientation = "vertical")
        layout2 = GridLayout(rows = 2, size_hint =(1,0.2))        
        home = HomeButton()
        dlist = firebase.get("/Level 1")
        dlist_keys = list(firebase.get("/Level 1").keys())
        
        for i in dlist_keys:
            dbin = dustbin(i,dlist[i][-1])
            layout2.add_widget(dbin)
            
        label2 = Label(text = name , size_hint = (1, 0.1))
         
        #layout1.add_widget(label)
        
        layout.add_widget(label2)
        layout.add_widget(Map("1.png"))
        layout.add_widget(layout2)
        
        layout.add_widget(home)
        
        with self.canvas:
            self.add_widget(layout)

#class Level2(Screen):
#    def __init__(self, name):
#        pass
#
#class Level3(Screen):
#    def __init__(self, name):
#        pass
#
#class Level4(Screen):
#    def __init__(self, name):
#        pass

    
sm = ScreenManager()
sm.add_widget(HomeScreen(name='home'))

class TestApp(App):
    def build(self):
        self.title = version
        return sm

if __name__ == '__main__':    
    TestApp().run()