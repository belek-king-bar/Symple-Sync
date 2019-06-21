from django.urls import path

from . import views

urlpatterns = [
    path('', views.receive_emails, name='receive_emails'),
]