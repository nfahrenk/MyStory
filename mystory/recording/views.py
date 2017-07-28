# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views import View
from recording.models import Session, Page
from recording.forms import SessionForm, PageForm, ActionEventForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from urlparse import urlparse
from mystory.settings import BASE_DIR
import os, json
from bs4 import BeautifulSoup
from urlparse import urljoin
from django.shortcuts import render

def processHtml(url, contents):
    # Remove all script tags and replace links with absolute links
    soup = BeautifulSoup(contents)
    for match in soup.findAll('script'):
        match.decompose()
    for tag in soup.findAll():
        if tag.get('href'):
            tag['href'] = urljoin('http://publy.nickfahrenkrog.me/', tag['href'])
        elif tag.get('src'):
            tag['src'] = urljoin('http://publy.nickfahrenkrog.me/', tag['src'])
    return str(soup)

def jsView(request):
    abspath = os.path.join(BASE_DIR, 'static', 'js', 'mystory.js')
    with open(abspath, 'r') as f:
        response = HttpResponse(f.read())
    response['Content-Type'] = 'application/x-javascript'
    return response

def getBaseUrl(url):
    o = urlparse(url)
    return o.scheme + '://' + o.netloc

def getSession(sessionId, url):
    try:
        session = Session.objects.get(id=sessionId)
        if session.isActive and getBaseUrl(url) == session.baseUrl:
            return session
    except Session.DoesNotExist:
        pass
    return False

def wrapper(response):
    response['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    return response

def index(request):
    return render(request, 'index.html', {'session': Session.objects.filter(isActive=False, isProcessed=True).order_by('-timestamp').first()})

@method_decorator(csrf_exempt, name='dispatch')
class SessionView(View):    
    def post(self, request):
        form = SessionForm(request.POST)
        if not form.is_valid():
            return wrapper(JsonResponse({'errors': form.errors}, status=400))
        session = form.save()
        return wrapper(JsonResponse({'sessionId': session.id}))

@method_decorator(csrf_exempt, name='dispatch')
class IdentifyView(View):
    def post(self, request, sessionId):
        session = getSession(sessionId, request.POST.get('url'))
        if not session:
            return wrapper(JsonResponse({'errors': [{'sessionId': 'Not a valid session id'}]}, status=404))
        if not request.POST.get('identifier'):
            return wrapper(JsonResponse({'errors': [{'identifier': 'Must be at least one character long'}]}, status=400))
        session.identifier = request.POST.get('identifier')
        session.save()
        return wrapper(JsonResponse({'response': 'ok'}))

@method_decorator(csrf_exempt, name='dispatch')
class PageView(View):
    def post(self, request, sessionId):
        session = getSession(sessionId, request.POST.get('url'))
        if not session:
            return wrapper(JsonResponse({'errors': [{'sessionId': 'Not a valid session id'}]}, status=404))
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.session = session
            page.save()
            with open(os.path.join(BASE_DIR, 'static', 'sites', str(page.id) + '.html'), 'w') as f:
                f.write(processHtml(page.url, form.cleaned_data['text']))
        else:
            return wrapper(JsonResponse({'errors': form.errors}, status=400))
        return wrapper(JsonResponse({'pageId': page.id}))

@method_decorator(csrf_exempt, name='dispatch')
class EventsView(View):
    def post(self, request, sessionId):
        url = request.POST.get('url')
        session = getSession(sessionId, url)
        if not session:
            return wrapper(JsonResponse({'errors': [{'sessionId': 'Not a valid session id'}]}, status=404))
        actionEvents = json.loads(request.POST.get('actionEvents', []))
        page = Page.objects.filter(session__id=sessionId, url=url).order_by('-timestamp')
        if not page.exists():
            return wrapper(JsonResponse({'errors': [{'page': 'Page not previously initialized'}]}, status=404))
        page = page.first()
        errors = []
        for event in actionEvents:
            form = ActionEventForm(event)
            if form.is_valid():
                action = form.save(commit=False)
                action.page = page
                action.eventType = form.cleaned_data['eventType']
                action.save()
            else:
                eventStr = str(event.get('eventType')) + ' - ' + event.get('timestamp')
                errors.append({eventStr: form.errors})
        if errors:
            print errors
            return wrapper(JsonResponse({'errors': errors}, status=400))
        return wrapper(JsonResponse({'response': 'ok'}))

