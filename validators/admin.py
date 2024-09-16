from django.contrib import admin
from .models import Associated_validators, validators
# Register your models here.

admin.site.register(validators)
admin.site.register(Associated_validators)
