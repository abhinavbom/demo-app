from django.urls import path
from . import views

urlpatterns = [
    path('auth/sign-in', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out.as_view(), name='sign_out'),
    path('auth-receiver/', views.auth_receiver, name='auth_receiver'),
    path('dashboard', views.dashboard.as_view(), name='dashboard'),
    path('dashboardanalytics', views.dashboard_analytics.as_view(), name='dashboardanalytics'),
    path('getauthkey', views.getauthkey.as_view(), name='getauthkey'),
    path('exchange-code/', views.exchange_code_for_token, name='exchange_code_for_token'),

]

