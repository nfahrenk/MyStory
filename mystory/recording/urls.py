from django.conf.urls import url
from recording import views

app_name = 'recording'
urlpatterns = [
    url(r'^start$', views.SessionView.as_view(), name='start'),
    url(r'^page/(?P<sessionId>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})$', views.PageView.as_view(), name='page'),
    url(r'^initialize/(?P<sessionId>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})$', views.IdentifyView.as_view(), name='initialize'),
    url(r'^record/(?P<sessionId>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})$', views.EventsView.as_view(), name='record'),
    url(r'^mystory\.js$', views.jsView, name='js'),
    url(r'^$', views.index, name='index')
]