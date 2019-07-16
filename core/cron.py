from django_cron import CronJobBase, Schedule
from core.constants import MINUTE_DAY, MINUTE_WEEK, MINUTE_MONTH
from .services import SlackService, GoogleService
from .models import Service


class MySlackCronJob(CronJobBase):
    slack = Service.objects.filter(name='slack').first()
    if slack.frequency == 'everyday':
        RUN_EVERY_MINS = MINUTE_DAY
    elif slack.frequency == 'everyweek':
        RUN_EVERY_MINS = MINUTE_WEEK
    elif slack.frequency == 'everymonth':
        RUN_EVERY_MINS = MINUTE_MONTH

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.my_slack_cron_job'

    def do(self):
        SlackService.receive_messages()


class MyGmailCronJob(CronJobBase):
    gmail = Service.objects.filter(name='gmail').first()
    if gmail.frequency == 'everyday':
        RUN_EVERY_MINS = MINUTE_DAY
    elif gmail.frequency == 'everyweek':
        RUN_EVERY_MINS = MINUTE_WEEK
    elif gmail.frequency == 'everymonth':
        RUN_EVERY_MINS = MINUTE_MONTH

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'core.my_gmail_cron_job'

    def do(self):
        GoogleService.receive_email_messages()
