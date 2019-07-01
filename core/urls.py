from django.urls import path
from . import views

urlpatterns = [
    path('doGetSlackMessages', views.ReceiveSlackListView.as_view(), name='doGetSlackMessages'),
    path('doGetSlackOauthCode', views.ReceiveSlackCodeOauthView.as_view(), name='doGetSlackOauthCode'),
    path('doGetGmailMessages', views.RecieveEmailListView.as_view(), name='doGetGmailMessages'),
]
