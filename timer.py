# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 13:28:34 2018

@author: TTM
"""
import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
import time


class updateLabel(Label):
    def __init__(self):
        super(updateLabel, self).__init__()
        self.text = "loading" 
        Clock.schedule_interval(self.getCurrentTime,1)
        self.counter = 0
        
    def getCurrentTime(self,dt):
#        currentTime = time.localtime()
#        currentMin = currentTime[4]
#        currentSec = currentTime[5]
#        
#        minDiff = 29 - currentMin % 30
#        secDiff = 60 - currentSec % 60
#        
#        if secDiff == 60:
#            secDiff = 0
#            
#        if secDiff == 0 and minDiff == 0:
#            self.update()
#        
#        output = "Next update in " + "{:02d}".format(minDiff) + ":" + "{:02d}".format(secDiff)
#        self.text = output
        if "..." in self.text:
            self.text = "loading"

        else:
            self.text += "."
            
class TestApp(App):
    def build(self):
        return updateLabel()

if __name__ == '__main__':    
    TestApp().run()
            
    
            