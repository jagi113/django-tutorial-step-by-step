import datetime

from django.db import models
from django.utils import timezone


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.question_text

    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text


class Votes(models.Model):
    def floor_dt(dt, interval):
        replace = (dt.minute // interval)*interval
        return dt.replace(minute = replace, second=0, microsecond=0)
    
    question = models.ForeignKey(
        Question, related_name="question", on_delete=models.CASCADE)
    choice = models.ForeignKey(
        Choice, related_name="choice", on_delete=models.CASCADE)
    vote_time = models.DateTimeField(default=floor_dt(datetime.datetime.now(), 1))

    def __str__(self):
        return self.vote_time.strftime("%m/%d/%Y, %H:%M:%S")
    
    class Meta:
        ordering = ['vote_time']
        

