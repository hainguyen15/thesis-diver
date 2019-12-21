from django.db import models

from apps.core.models import TimestampedModel
from apps.core.constants import USER_SUBSCRIPTION

class Profile(TimestampedModel):
    user = models.OneToOneField(
        'authentication.User', on_delete=models.CASCADE
    )

    bio = models.TextField(blank=True)
    image = models.URLField(blank=True)
    subsciption = models.CharField(choices=USER_SUBSCRIPTION, max_length=1, default='F')
    
