from django.urls import path
from . import views

urlpatterns = [
    path('doGetSlackMessages', views.ReceiveSlackListView.as_view(), name='doGetSlackMessages'),
    path('doGetSlackOauthCode', views.ReceiveSlackCodeOauthView.as_view(), name='doGetSlackOauthCode'),
    path('doGetGmailOauthCode', views.ReceiveGmailCodeOauthView.as_view(), name='doGetGmailOauthCode'),
    path('doGetGmailMessages', views.RecieveGmailListView.as_view(), name='doGetGmailMessages'),
    path('doSaveGmailMessages', views.SaveGmailListView.as_view(), name='doSaveGmailMessages'),
]
