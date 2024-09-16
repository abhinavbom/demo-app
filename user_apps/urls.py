from django.urls import path
from .views import app_list, create, update_app, delete_app, app_details

urlpatterns = [
    path('create_apps/', create.as_view(), name='create_apps'),
    path('get_apps/', app_list.as_view(), name='get_apps'),
    path('app_details/', app_details.as_view(), name='app_details'),
    path('update_apps/', update_app.as_view(), name='update_apps'),
    path('delete_apps/', delete_app.as_view(), name='delete_app'),
]

