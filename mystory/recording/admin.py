# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from recording.models import Session, Page, ActionEvent, ModifiedAttribute, InsertedOrDeleted

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    pass

@admin.register(ActionEvent)
class ActionEventAdmin(admin.ModelAdmin):
    pass

@admin.register(ModifiedAttribute)
class ModifiedAttributeAdmin(admin.ModelAdmin):
    pass

@admin.register(InsertedOrDeleted)
class InsertedOrDeletedAdmin(admin.ModelAdmin):
    pass