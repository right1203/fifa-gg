from django.conf import settings
from django.db import models
from django.utils import timezone


class Match(models.Model):
    matchid = models.CharField(max_length=200)
    result = models.CharField(max_length=200,  null=True)
    tddate = models.DateTimeField(null=True)
    loadingtime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id} / {self.matchid} / {self.result} / {self.tddate} / {self.loadingtime}'
