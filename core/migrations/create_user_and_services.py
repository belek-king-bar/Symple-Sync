from ..models import User
from django.db import migrations


def create_user(apps, schema_editor):
    apps.get_model('core', 'User').objects.create(username='Dmitriy', token='1234')


def create_services(apps, schema_editor):
    user = User.objects.first()
    service_slack = apps.get_model('core', 'Service').objects.create(name='slack', status=True, frequency='everyday')
    service_gmail = apps.get_model('core', 'Service').objects.create(name='gmail', status=True, frequency='everyday')
    service_slack.user.add(user.id)
    service_gmail.user.add(user.id)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user),
        migrations.RunPython(create_services)
    ]
