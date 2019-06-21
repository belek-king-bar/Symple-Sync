from django.contrib.postgres.fields import ArrayField
from django.db import models

# Create your models here.

class Email(models.Model):
  snippet = ArrayField(models.CharField(max_length=200))

  def __str__(self):
    return self.snippet
