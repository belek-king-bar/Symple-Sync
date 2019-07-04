from django.urls import path
from . import views

urlpatterns = [
    path('slack/message', views.SlackMessageView.as_view(), name='slack_message'),
    path('doGetSlackMessages', views.ReceiveSlackListView.as_view(), name='doGetSlackMessages'),
    path('doGetSlackOauthCode', views.ReceiveSlackCodeOauthView.as_view(), name='doGetSlackOauthCode'),
    path('doGetGmailMessages', views.RecieveEmailListView.as_view(), name='doGetGmailMessages'),
]