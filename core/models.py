from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, verbose_name='User name')
    token = models.CharField(max_length=255, verbose_name='User token')

    def __str__(self):
        return self.username


class Service(models.Model):
    user = models.ManyToManyField(User, related_name='service', verbose_name="User")
    name = models.CharField(max_length=255, verbose_name='Service name')
    status = models.BooleanField(default=True, verbose_name="Service status")
    last_sync = models.DateTimeField(verbose_name="Last synchronization", null=True, blank=True)
    frequency = models.CharField(max_length=255, verbose_name='Service frequency', null=True, blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    user = models.ManyToManyField('User', related_name='tags', verbose_name='User')
    service = models.ManyToManyField(Service, related_name='tags', verbose_name='Service')
    name = models.CharField(max_length=255, verbose_name='Tag name', null=True)
    url = models.CharField(max_length=255, verbose_name='Tag url to confluence', null=True, blank=True,
                           default='url')


class Token(models.Model):
    service = models.OneToOneField(Service, related_name='token', verbose_name='Service token',
                                   on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True, blank=True, verbose_name='Access Token')
    refresh_token = models.CharField(max_length=255, null=True, blank=True, verbose_name='Refresh Token')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service.name


class Message(models.Model):
    user = models.ForeignKey(User, related_name='messages', verbose_name='User messages',
                             on_delete=models.CASCADE, null=True)
    service = models.ForeignKey(Service, related_name='messages', verbose_name='Service messages',
                                on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, related_name='messages', verbose_name='Tag messages', on_delete=models.CASCADE)
    timestamp = models.CharField(max_length=255, null=True, blank=True, verbose_name='Timestamp')
    user_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Sender message user')
    text = models.TextField(max_length=2000, verbose_name='Text in message')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service.name


class File(models.Model):
    message = models.ForeignKey(Message, related_name='files', verbose_name="File message",
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='File name')
    url_download = models.CharField(max_length=255, verbose_name='Url download for file')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Log(models.Model):
    service = models.ForeignKey(Service, related_name='logs', verbose_name='Log service', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='logs', verbose_name='Log user', on_delete=models.CASCADE)
    log_message = models.CharField(max_length=255, verbose_name='Message log')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.log_message
