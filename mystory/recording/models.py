# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from enum import Enum
import heapq
from itertools import chain
from uuid import uuid4
import inspect
from selenium.webdriver.common.keys import Keys
from parsePage import processHtml

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
    actionEvent = 0
    modifiedAttribute = 1
    insertedOrDeleted = 2

def lookupCategory(instance):
    if isinstance(instance, ActionEvent):
        return CategoryEnum.actionEvent.value
    elif isinstance(instance, ModifiedAttribute):
        return CategoryEnum.modifiedAttribute.value
    elif isinstance(instance, InsertedOrDeleted):
        return CategoryEnum.insertedOrDeleted.value
    return -1

class ActionEventEnum(ChoiceEnum):
    click = 0
    dblclick = 1
    contextmenu = 2
    mousedown = 3
    mouseup = 4
    keydown = 5
    keyup = 6
    keypress = 7
    mousemove = 8

class Session(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=str(uuid4()))
    identifier = models.CharField(max_length=64, blank=True)    
    baseUrl = models.URLField()
    isActive = models.BooleanField(default=True)
    isProcessed = models.BooleanField(default=False)
    timestamp = models.DateTimeField()

    @classmethod
    def getInitialSeleniumInstructions(cls):
        return [
            'from selenium import webdriver',
            'from selenium.webdriver.common.keys import Keys',
            'from selenium.webdriver.common.desired_capabilities import DesiredCapabilities',
            'from selenium.webdriver.common.action_chains import ActionChains',
            'import time',
            'class Actions(ActionChains):',
            '\tdef wait(self, time_s):',
            '\t\tself._actions.append(lambda: time.sleep(time_s))',
            '\t\treturn self',
            'driver = webdriver.Remote(command_executor="http://127.0.0.1:4444/wd/hub", desired_capabilities=DesiredCapabilities.CHROME)',                       
        ]

    @classmethod
    def getFinalSeleniumInstructions(cls):
        return [
            'driver.quit()'
        ]   

    def generateSeleniumInstructions(self):
        instructions = []
        prevPage = None
        for page in self.pages.all():
            instructions.extend(page.getSeleniumInstructions(prevPage))
            isActionChain = False
            previousTimestamp = page.timestamp
            prevX = 0
            prevY = 0
            for timestamp, event in page.getAllEvents():
                category = lookupCategory(event)
                isActionEvent = category == CategoryEnum.actionEvent.value
                if isActionEvent:
                    command = event.getSeleniumCommand(prevX, prevY)
                else:
                    command = event.getSeleniumCommand()
                delta = timestamp - previousTimestamp
                if not command:
                    continue
                if isActionChain and isActionEvent:
                    if delta.total_seconds() > 0:
                        instructions[-1] += '.wait(' + str(delta.total_seconds()) + ')'
                    instructions[-1] += '.' + command
                elif isActionEvent:
                    instructions.append('Actions(driver).' + command)
                elif isActionChain:
                    instructions[-1] += '.perform()'
                    instructions.append('time.sleep(' + str(delta.total_seconds()) + ')')
                    instructions.append(command)
                else:
                    instructions.append('time.sleep(' + str(delta.total_seconds()) + ')')
                    instructions.append(command)
                isActionChain = category == CategoryEnum.actionEvent.value
                previousTimestamp = timestamp
                if isActionEvent and event.eventType == ActionEventEnum.mousemove.value:
                    prevX = event.x
                    prevY = event.y
            if isActionChain:
                instructions[-1] += '.perform()'
            prevPage = page
        return instructions

    def generatePythonFileContents(self):
        instructions = chain(
            Session.getInitialSeleniumInstructions(), 
            self.generateSeleniumInstructions(),
            Session.getFinalSeleniumInstructions())
        return '\n'.join(instructions)

    def __str__(self):
        return self.generatePythonFileContents()

    def __unicode__(self):
        return str(self)

class Page(models.Model):
    session = models.ForeignKey(Session, related_name='pages', on_delete=models.CASCADE)
    screenWidth = models.IntegerField()
    screenHeight = models.IntegerField()
    url = models.URLField()
    timestamp = models.DateTimeField()

    @classmethod
    def eventsForMerge(cls, events):
        return [(evt.timestamp, evt) for evt in events.all()]

    def getAllEvents(self):
        return heapq.merge(Page.eventsForMerge(self.actionEvents), Page.eventsForMerge(self.insertedOrDeleteds), Page.eventsForMerge(self.modifiedAttributes))

    def getHtmlUrl(self):
        return 'file:///sites/%d.html' % self.id

    def getSeleniumInstructions(self, prevPage=None):
        instructions = []
        if not prevPage or prevPage.getHtmlUrl() != self.getHtmlUrl():
            instructions.append('driver.get("%s")' % self.getHtmlUrl())
        if not prevPage or (self.screenWidth != prevPage.screenWidth or self.screenHeight != prevPage.screenHeight):
            instructions.append('driver.set_window_size(%d, %d)' % (self.screenWidth, self.screenHeight))
        return instructions

    def __str__(self):
        return self.url + " - " + self.session.id

    def __unicode__(self):
        return str(self)

    class Meta:
        ordering = ['timestamp']

class ActionEvent(models.Model):
    page = models.ForeignKey(Page, related_name='actionEvents', on_delete=models.CASCADE)
    eventType = models.IntegerField(choices=ActionEventEnum.choices())
    key = models.CharField(max_length=128, blank=True, default='')
    target = models.CharField(max_length=1024, blank=True, default='')
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    timestamp = models.DateTimeField()

    @classmethod
    def getJavascriptToSeleniumEvent(cls, eventValue):
        javascriptEventToSelenium = {
            ActionEventEnum.click.value: 'click',
            ActionEventEnum.dblclick.value: 'double_click',
            ActionEventEnum.contextmenu.value: 'context_click',
            ActionEventEnum.mousedown.value: 'click_and_hold',
            ActionEventEnum.mouseup.value: 'release',
            ActionEventEnum.keydown.value: 'key_down',
            ActionEventEnum.keyup.value: 'key_up',
            ActionEventEnum.keypress.value: 'send_keys',
            ActionEventEnum.mousemove.value: 'move_by_offset'
        }
        return javascriptEventToSelenium[eventValue]

    def getSeleniumEvent(self):
        return ActionEvent.getJavascriptToSeleniumEvent(self.eventType)

    def keyboardCommand(self, seleniumEvent):
        key = '"' + self.key + '"'
        #  The following for loop is a quick way to see if it's a constant that needs to be translated
        for const in dir(Keys):            
            if const.isupper() and self.key.lower().replace('_', '') == const.lower().replace('_', ''):
                key = 'Keys.' + const
        return '%s(%s)' % (seleniumEvent, key)

    def coordinateCommand(self, seleniumEvent, prevX, prevY):
        # Used for mouse movements, window resize, etc.
        if self.x == prevX and self.y == prevY:
            return ''
        return '%s(%d, %d)' % (seleniumEvent, self.x - prevX, self.y - prevY)

    def basicCommand(self, seleniumEvent):
        return '%s("%s")' % (seleniumEvent, self.target)

    def getSeleniumCommand(self, prevX=0, prevY=0):
        seleniumEvent = self.getSeleniumEvent()
        if self.eventType in [ActionEventEnum.keypress.value, ActionEventEnum.keyup.value, ActionEventEnum.keydown.value]:
            return self.keyboardCommand(seleniumEvent)
        elif self.eventType == ActionEventEnum.mousemove.value:
            return self.coordinateCommand(seleniumEvent, prevX, prevY)
        else:
            return self.basicCommand(seleniumEvent)

    def __str__(self):
        return self.getSeleniumCommand()

    def __unicode__(self):
        return str(self)

    class Meta:
        ordering = ['timestamp']

class ModifiedAttribute(models.Model):
    page = models.ForeignKey(Page, related_name='modifiedAttributes', on_delete=models.CASCADE)
    target = models.CharField(max_length=1024)
    attributeName = models.CharField(max_length=128)
    oldValue = models.CharField(max_length=1024)
    newValue = models.CharField(max_length=1024)
    timestamp = models.DateTimeField()

    def getSeleniumCommand(self):
        attributeName = "className" if self.attributeName == "class" else self.attributeName
        return 'driver.execute_script(\'document.querySelector(\"%s\").%s = %s;\')' % (
            self.target, attributeName, self.newValue.replace('"', '\"'))

    def __str__(self):
        return self.getSeleniumCommand()

    def __unicode__(self):
        return str(self)

    class Meta:
        ordering = ['timestamp']

class InsertedOrDeleted(models.Model):
    page = models.ForeignKey(Page, related_name='insertedOrDeleteds', on_delete=models.CASCADE)
    target = models.CharField(max_length=1024)
    isInserted = models.BooleanField(default=True)
    innerHTML = models.TextField()
    timestamp = models.DateTimeField()

    def getSeleniumCommand(self):
        return 'driver.execute_script(\'document.querySelector(\"%s\").innerHTML = %s;\')' % (
            self.target, processHtml(self.page.url, self.innerHTML))

    def __str__(self):
        return self.getSeleniumCommand()

    def __unicode__(self):
        return str(self)

    class Meta:
        ordering = ['timestamp']

