from django.urls import path
from .views import GetAllPrompts, validate

urlpatterns = [
    path('getprompts/', GetAllPrompts.as_view(), name='getprompts'),
    path('', validate.as_view(), name='validate'),
    
]

