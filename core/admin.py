from django.contrib import admin
from .models import Messages, Token, Files, Tags, Services, User, Logs

# Register your models here.

admin.site.register(Messages)
admin.site.register(Token)
admin.site.register(Files)
admin.site.register(Tags)
admin.site.register(Services)
admin.site.register(User)
admin.site.register(Logs)
