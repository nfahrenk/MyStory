# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from enum import Enum
import heapq
from itertools import chain
from uuid import uuid4
import inspect
from selenium.webdriver.common.keys import Keys

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
        return 0
    else:
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
    filename = models.CharField(max_length=256, blank=True)
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
            allEvents = [event for event in page.actionEvents.all()]
            isActionChain = False
            previousTimestamp = page.timestamp
            prevX = 0
            prevY = 0
            for event in allEvents:
                timestamp = event.timestamp
                category = lookupCategory(event)
                command = event.getSeleniumCommand(prevX, prevY)
                if not command:
                    continue
                if isActionChain and category == CategoryEnum.actionEvent.value:
                    delta = timestamp - previousTimestamp
                    if delta.total_seconds() > 0:
                        instructions[-1] += '.wait(' + str(delta.total_seconds()) + ')'
                    instructions[-1] += '.' + command
                elif category == CategoryEnum.actionEvent.value:
                    instructions.append('Actions(driver).' + command)
                elif isActionChain:
                    instructions[-1] += '.perform()'
                    instructions.append(command)
                else:
                    instructions.append(command)
                isActionChain = category == CategoryEnum.actionEvent.value
                previousTimestamp = timestamp
                if event.eventType == ActionEventEnum.mousemove.value:
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

    def getSeleniumCommand(self, prevX=0, prevY=0):
        seleniumEvent = self.getSeleniumEvent()
        if self.eventType in [ActionEventEnum.keypress.value, ActionEventEnum.keyup.value, ActionEventEnum.keydown.value]:
            g = lambda x: x.lower().replace('_', '')
            key = '"' + self.key + '"'
            for const in dir(Keys):
                if g(self.key) == g(const):
                    key = 'Keys.' + const
            return '%s(%s)' % (seleniumEvent, key)
        elif self.eventType == ActionEventEnum.mousemove.value:
            if self.x == prevX and self.y == prevY:
                return ''
            return '%s(%d, %d)' % (seleniumEvent, self.x - prevX, self.y - prevY)
        else:
            return seleniumEvent + '()'

    def __str__(self):
        return self.getSeleniumCommand()

    def __unicode__(self):
        return str(self)

    class Meta:
        ordering = ['timestamp']
