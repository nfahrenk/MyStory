# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from recording.models import SessionPage, SessionEvents
from recording.forms import SessionPageForm

def getSession(sessionId, baseUrl):
    try:
        session = Session.objects.get(id=sessionId)
        if session.isActive and session.baseUrl == baseUrl:
            return session
    except Session.DoesNotExist:
        pass
    return False

class SessionView(View):

    def post(self, request):
        form = SessionForm(request.POST)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors}, status=400)
        session = form.save()
        return JsonResponse({'sessionId': session.id})

class IdentifyView(View):
    
    def post(self, request):
        sessionId = request.POST.get('sessionId')
        if not isValidSession(sessionId, None):
            return JsonResponse({'errors': [{'sessionId': 'Not a valid session id'}]}, status=400)
        session = get_object_or_404(Session, id=sessionId)
        if not request.POST.get('identifier'):
            return JsonResponse({'errors': [{'identifier': 'Must be at least one character long'}]}, status=400)
        session.identifier = request.POST.get('identifier')
        session.save()
        return JsonResponse({'response': 'ok'})

class PageView(View):

    def post(self, request):
        sessionId = request.POST.get('sessionId')
        if not isValidSession(sessionId, None):
            return JsonResponse({'errors': [{'sessionId': 'Not a valid session id'}]}, status=400)
        form = SessionPageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.session = 
        else:
            return JsonResponse({'errors': form.errors})
        return JsonResponse({'response': 'ok'})

class SimpleEventsView(View):

    def post(self, request):
        events = request.POST.get('events', [])
        for event in events:
            form = SessionEventForm()