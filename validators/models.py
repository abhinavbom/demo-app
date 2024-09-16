from django.db import models
from google_auth.models import NewUser
from user_apps.models import user_app
from google_auth.models import TimestampModel


class validators(TimestampModel):
    name = models.CharField(max_length=255, unique=True)
    descriptions = models.TextField()
    parameters = models.JSONField(null=True,blank=True)
    codename = models.IntegerField(unique=True)
    
    def __str__(self) -> str:
        return self.name
    
    
class Associated_validators(TimestampModel):
    apikey = models.TextField()
    parameters = models.JSONField()
    validator = models.ForeignKey(validators, on_delete=models.CASCADE)
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    userapp = models.ForeignKey(user_app, on_delete=models.CASCADE)
    