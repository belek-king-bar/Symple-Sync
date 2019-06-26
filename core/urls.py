from django.urls import path

from core import services
from . import views

urlpatterns = [
    path('api/v1/do/slack_data', views.ReceiveSlackListView.as_view(), name='slack_integration'),
    path('', views.RecieveEmailListView.as_view(), name='DoGetEmails'),
    url(r'email', views.EmailView.as_view()),
]