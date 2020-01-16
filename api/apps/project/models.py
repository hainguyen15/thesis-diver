from django.db import models

from ..core.models import TimestampedModel
from ..core.constants import DEFAULT_PROJ_STATUS, CHOICES_PROJ_STATUS
from .. import settings
# Create your models here.

class Project(TimestampedModel):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    title       = models.CharField(max_length=20)
    desciption  = models.TextField(blank=True, default='')
    size        = models.IntegerField(null=False, default=0)
    status      = models.SmallIntegerField(choices=CHOICES_PROJ_STATUS, default=DEFAULT_PROJ_STATUS)
