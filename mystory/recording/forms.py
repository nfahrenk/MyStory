from django.forms import ModelForm
from recording.models import Session, Page

class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['screenWidth', 'screenHeight', 'baseUrl', 'timestamp']

class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = ['url', 'timestamp']

class SimpleEventForm(ModelForm):
    class Meta:
        model = SimpleEvent
        fields = ['eventType', 'targetSelector', 'timestamp']