from django.conf.urls import url
from django.urls import path

from core import services
from . import views

urlpatterns = [
    path('', views.RecieveEmailListView.as_view(), name='DoGetEmails'),
    url(r'email', views.EmailView.as_view()),
]