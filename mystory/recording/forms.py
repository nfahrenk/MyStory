from django.forms import ModelForm, IntegerField, CharField, DateTimeField, ValidationError
from recording.models import Session, Page, ActionEvent, ActionEventEnum, ModifiedAttribute, InsertedOrDeleted

class SessionForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z %f'])
    
    class Meta:
        model = Session
        fields = ['baseUrl', 'timestamp']

class PageForm(ModelForm):
    text = CharField()
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z %f'])    
    
    class Meta:
        model = Page
        fields = ['screenWidth', 'screenHeight', 'url', 'timestamp']

class ActionEventForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z %f'])
    eventType = IntegerField()
    key = CharField(max_length=128, required=False)
    x = IntegerField(required=False)
    y = IntegerField(required=False)
    target = CharField(max_length=1024, required=False)

    # def clean_key(self):
    #     key = self.cleaned_data['key']
    #     eventType = self.cleaned_data['eventType']
    #     if eventType == ActionEventEnum.keydown.value or eventType == ActionEventEnum.keyup.value and key not in ['Control', 'Alt', 'Shift']:
    #         raise ValidationError("Keydown and keyup values can only be control / alt / shift")
    #     return key

    class Meta:
        model = ActionEvent
        fields = ['key', 'x', 'y', 'target', 'timestamp']

class ModifiedAttributeForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z %f'])

    class Meta:
        model = ModifiedAttribute
        fields = ['attributeName', 'oldValue', 'newValue', 'target', 'timestamp']

class InsertedOrDeletedForm(ModelForm):
    timestamp = DateTimeField(input_formats=['%a, %d %b %Y %H:%M:%S %Z %f'])

    class Meta:
        model = InsertedOrDeleted
        fields = ['isInserted', 'innerHTML', 'target', 'timestamp']
