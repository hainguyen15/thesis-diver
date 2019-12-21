# from django.db import models
from djongo import models
from model_utils import Choices
from apps import settings
from apps.core.constants import DEFAULT_DS_STATUS, CHOICES_DS_STATUS

class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at', '-last_modified']

class StringObject(models.Model):
    class_name = models.CharField(max_length=30)
    class Meta:
        abstract = True

class Metrics(models.Model):
    metric_name = models.CharField(max_length=30)
    value       = models.FloatField()
    class Meta:
        abstract = True
    
class BaseDataset(TimestampedModel):
    user            = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    name            = models.CharField(max_length=100)
    description     = models.TextField(blank=True, default='')
    total_samples   = models.PositiveIntegerField(default=0)
    total_classes   = models.PositiveIntegerField(default=1)
    status          = models.SmallIntegerField(choices=CHOICES_DS_STATUS, default=DEFAULT_DS_STATUS)
    labels          = models.ListField(default=[])
        
    class Meta:
        abstract = True

class BaseDLModel(TimestampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    metrics = models.ArrayModelField(model_container=Metrics)
    running_task = models.CharField()
    

    class Meta:
        abstract = True
