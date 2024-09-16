from django.db import models
from user_apps.models import user_app
from google_auth.models import NewUser
from google_auth.models import TimestampModel
# Create your models here.


class prompts(TimestampModel):
    app = models.ForeignKey(user_app, on_delete=models.CASCADE)
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    validate = models.BooleanField(default=False)
    prompt = models.TextField()
    
    def __str__(self) -> str:
        return self.prompt