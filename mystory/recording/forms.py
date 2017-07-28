from django.forms import ModelForm, IntegerField, CharField, DateTimeField
from recording.models import Session, Page, ActionEvent

class SessionForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z'])
    
    class Meta:
        model = Session
        fields = ['baseUrl', 'timestamp']

class PageForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z'])    
    
    class Meta:
        model = Page
        fields = ['screenWidth', 'screenHeight', 'url', 'timestamp']

class ActionEventForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z'])
    eventType = IntegerField()
    key = CharField(max_length=128, required=False)
    x = IntegerField(required=False)
    y = IntegerField(required=False)

    class Meta:
        model = ActionEvent
        fields = ['key', 'x', 'y', 'timestamp']