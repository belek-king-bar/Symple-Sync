from django.urls import path
from . import views

urlpatterns = [
    path('doGetEmails/', views.RecieveEmailListView.as_view(), name='DoGetEmails'),
    path('api/v1/do/slack_data', views.ReceiveSlackListView.as_view(), name='slack_integration'),
]
