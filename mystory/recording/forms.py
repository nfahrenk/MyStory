from django.forms import ModelForm, IntegerField, CharField
from recording.models import Session, Page

class SessionForm(ModelForm):
    class Meta:
        model = Session
        fields = ['baseUrl', 'timestamp']

class PageForm(ModelForm):
    class Meta:
        model = Page
        fields = ['screenWidth', 'screenHeight', 'url', 'timestamp']

class SimpleEventForm(ModelForm):
    key = CharField(max_length=128, required=False)
    x = IntegerField(required=False)
    y = IntegerField(required=False)

    class Meta:
        model = SimpleEvent
        fields = ['eventType', 'key', 'x', 'y', 'timestamp']