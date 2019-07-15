from django.urls import path
from . import views

urlpatterns = [
    path('slack/message', views.SlackMessageView.as_view(), name='slack_message'),
    path('gmail/message', views.RecieveGmailListView.as_view(), name='gmail_message'),
    path('services', views.ServiceView.as_view(), name='get_put_services'),
    path('tags', views.TagsView.as_view(), name='get_post_tags'),
    path('logs', views.LogsView.as_view(), name='get_logs'),
    path('doGetSlackMessages', views.ReceiveSlackListView.as_view(), name='doGetSlackMessages'),
    path('doGetGmailMessages', views.SaveGmailListView.as_view(), name='doGetGmailMessages'),
    path('doGetSlackOauthCode', views.ReceiveSlackCodeOauthView.as_view(), name='doGetSlackOauthCode'),
    path('doGetGmailOauthCode', views.ReceiveGmailCodeOauthView.as_view(), name='doGetGmailOauthCode'),
]