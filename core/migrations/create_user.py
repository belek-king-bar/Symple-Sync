
from django.db import migrations, models


def create_user(apps, schema_editor):
    apps.get_model('core', 'User').objects.create(username='Dmitriy', token='1234')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_user),
    ]
