from django.db import models


class User(models.Model):
    username = models.CharField(max_length=255, verbose_name='User name')
    token = models.CharField(max_length=255, verbose_name='User token')

    def __str__(self):
        return self.username


class Services(models.Model):
    name = models.CharField(max_length=255, verbose_name='Service name')

    def __str__(self):
        return self.name


class Tags(models.Model):
    user = models.ManyToManyField('User', related_name='tags', verbose_name='User')
    service = models.ManyToManyField(Services, related_name='tags', verbose_name='Service')
    name = models.CharField(max_length=255, verbose_name='Tags name')

    def __str__(self):
        return self.name


class Token(models.Model):
    service = models.OneToOneField(Services, related_name='token', verbose_name='Service token',
                                   on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255, null=True, blank=True, verbose_name='Access Token')
    refresh_token = models.CharField(max_length=255, null=True, blank=True, verbose_name='Refresh Token')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service.name


class Messages(models.Model):
    user = models.ForeignKey(User, related_name='messages', null=True, blank=True, verbose_name='User messages',
                             on_delete=models.CASCADE)
    service = models.ForeignKey(Services, related_name='messages', verbose_name='Service messages',
                                on_delete=models.CASCADE)
    tag = models.ForeignKey(Tags, related_name='messages', verbose_name='Tag messages', on_delete=models.CASCADE)
    timestamp = models.CharField(max_length=255, null=True, blank=True, verbose_name='Timestamp')
    user_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Sender message user')
    text = models.TextField(max_length=2000, verbose_name='Text in message')
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag.name


class Files(models.Model):
    message = models.ForeignKey(Messages, related_name='files', verbose_name="File message",
                                on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name='File name')
    url_download = models.CharField(max_length=255, verbose_name='Url download for file')

    def __str__(self):
        return self.name


class Logs(models.Model):
    service = models.ForeignKey(Services, related_name='logs', verbose_name='Log service', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='logs', verbose_name='Log user', on_delete=models.CASCADE)
    log_message = models.CharField(max_length=255, verbose_name='Message log')

    def __str__(self):
        return self.log_message
