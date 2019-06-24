from django.urls import path

from core import services
from . import views

urlpatterns = [
    path('', views.RecieveEmailListView.as_view(), name='DoGetEmails'),
]