from django.contrib import admin
from .models import Message, Token, File, Tag, Service, User, Log

# Register your models here.

admin.site.register(Message)
admin.site.register(Token)
admin.site.register(File)
admin.site.register(Tag)
admin.site.register(Service)
admin.site.register(User)
admin.site.register(Log)
