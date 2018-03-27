# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 10:16:56 2018

@author: TTM
"""
import kivy
kivy.require("1.10.0")
from firebase import firebase

from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.graphics import Color, Rectangle, Ellipse

url = "https://dwthymio.firebaseio.com/"
token = "LLwuIQuOJT1ReEtSLmpIzGfBbfUrBerTtPXLB9It"

firebase = firebase.FirebaseApplication(url, token)

class StartScreen(FloatLayout):
    pass

class StatusScreen(Popup):
    def __init__(self, number):
        super(StatusScreen, self).__init__()
        
        self.title = "Bin" + str(number)
        self.content = Label(text = "hello")
        self.size_hint = (.9,.9)     
            
class dustbin(Button):
    def __init__(self, value, status):
        super(dustbin, self).__init__()
        self.background_normal = ""
        self.size_hint= (.05,.05)
        self.font_size = 10
        self.pos = (50,50)
        self.status = status
        self.value = value
        self.text = "Bin " + str(value)
        self.font_size = 10
        
        if status <= 25:
            self.background_color = [0,255,0,1]
        elif status <= 50:
            self.background_color = [255,255,0,1]
        elif status <= 75:
            self.background_color = [255,165,0,1]
        elif status <= 100:
            self.background_color = [1,0,0,1]
            
        
    def __str__(self):
        return self.text
       
    def on_press(self):
        print("clicky")
    
    def on_release(self):
        stat = StatusScreen(self.value)
        stat.open()
        
class HomeScreen(FloatLayout):
    def __init__(self):
        super(HomeScreen, self).__init__()
        bin_status = firebase.get("/dustbin") #get dustbin statuses from firebase as a list
#======= create dustbins=======       
        bin_list = []
        for i in range(len(bin_status)):
            newBin = dustbin(i+1,bin_status[i])
            bin_list.append(newBin)
#======== set dustbin positions ====== 
        bin_pos = []
        bin_list[6].pos = (100,100)
        bin_list[5].pos = (200,200)
        
        
        with self.canvas:
            self.add_widget(bin_list[6])
            self.add_widget(bin_list[5])
                    
        with self.canvas.before:
            self.rect = Rectangle(size = self.size, pos = self.pos, source = "1.png" )
        
        def update_rect(instance,value):
            instance.rect.pos = instance.pos
            instance.rect.size = instance.size
            
        self.bind(pos= update_rect, size = update_rect)
        
        with self.canvas.after:
            pass    
        
class TestApp(App):
    def build(self):
        return HomeScreen()
    
TestApp().run()

