# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from enum import Enum
import heapq
from itertools import chain

class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not(inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not(m[0][:2] == '__')]
        # format into django choice tuple
        choices = tuple([(str(p[1].value), p[0]) for p in props])
        return choices

class CategoryEnum(Enum):
    simpleEvent = 0
    complexEvent = 1
    modifiedAttribute = 2
    insertedOrDeleted = 3

def lookupCategory(x):
    if isinstance(x, SessionSimpleEvent):
        return CategoryEnum.simpleEvent.value
    elif isinstance(x, SesionComplexEvent):
        return CategoryEnum.complexEvent.value

class SimpleEventEnum(ChoiceEnum):
    click = 0
    dblclick = 1
    contextmenu = 2
    mousedown = 3
    mouseup = 4
    keydown = 5
    keyup = 6
    keypress = 7

class Session(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=lambda : str(uuid4()))    
    identifier = models.CharField(max_length=64, blank=True)    
    baseUrl = models.UrlField()
    isActive = models.BooleanField(default=True)
    isProcessed = models.BooleanField(default=False)
    timestamp = models.DateTimeField()

    @classmethod
    def getInitialSeleniumInstructions(cls):
        return [
            'from selenium import webdriver',
            'from selenium.webdriver.common.keys import Keys',
            'from selenium.webdriver.common.desired_capabilities import DesiredCapabilities',
            'driver = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub", desired_capabilities=DesiredCapabilities.CHROME)',                       
        ]

    def getFinalSeleniumInstructions(self):
        return [
            'driver.quit()'
        ]

    def generateSeleniumInstructions(self):
        instructions = []
        g = lambda x : (x.timestamp, f(x), x.getSeleniumCommand())
        for page in self.pages:
            instructions.extend(page.getSeleniumInstructions())
            allEvents = [page.simpleEvents, page.complexEvents, page.modifiedAttributes, page.insertedOrDeleted]
            flattenedEvents = heapq.merge(*map(g, allEvents))
            for timestamp,category,command in flattenedEvents:
                # Create action chain if complex or simple events
                pass
        return instructions

    def generatePythonFileContents(self):
        instructions = chain(
            Session.getInitialSeleniumInstructions(), 
            self.generateSeleniumInstructions(),
            Session.generateSeleniumInstructions())
        return '\n'.join(instructions)

class SessionPage(models.Model):
    session = models.ForeignKey(Session, related_name='pages', on_delete=models.CASCADE)
    screenWidth = models.IntegerField()
    screenHeight = models.IntegerField()
    url = models.UrlField()
    timestamp = models.DateTimeField()

    def getHtmlUrl(self):
        return ''

    def getSeleniumInstructions(self):
        return [
            'driver.get("%s")' % self.getHtmlUrl(),
            'driver.set_window_size(%d, %d)' % (self.screenWidth, self.screenHeight)
        ]

    def __str__(self):
        return self.url " - " + self.sessionId

    def __unicode__(self):
        return str(self)

    class Meta:
        ordering = ['timestamp']

class ActionEvent(models.Model):
    page = models.ForeignKey(SessionPage, related_name='simpleEvents', on_delete=models.CASCADE)
    eventType = models.IntegerField(choices=SimpleEventEnum.choices())
    key = models.CharField(max_length=128)
    x = models.IntegerField()
    y = models.IntegerField()
    timestamp = models.DateTimeField()

    @classmethod
    def getJavascriptToSeleniumEvent(cls, eventValue):
        javascriptEventToSelenium = {
            SimpleEventEnum.click.value: 'click',
            SimpleEventEnum.dblclick.value: 'double_click',
            SimpleEventEnum.contextmenu.value: 'context_click',
            SimpleEventEnum.mousedown.value: 'click_and_hold',
            SimpleEventEnum.mouseup.value: 'release',
            SimpleEventEnum.keydown.value: 'key_down',
            SimpleEventEnum.keyup.value: 'key_up',
            SimpleEventEnum.keypress.value: 'send_keys'
        }
        return javascriptEventToSelenium[eventValue]

    def getSeleniumEvent(self):
        return SessionEvent.getJavascriptToSeleniumEvent(self.eventType)

    def getSeleniumCommand(self):
        seleniumEvent = self.getSeleniumEvent()
        if self.eventType == ActionEventEnum.keypress.value:
            return '%s(%s)' % (seleniumEvent, self.key)
        else if self.eventType == ActionEventEnum.mousemove.value:
            return '%s(%d, %d)' % (seleniumEvent, self.x, self.y)
        else:
            return seleniumEvent + '()'

    class Meta:
        ordering = ['timestamp']
