from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('test/', views.test_view, name='test_view'),
    path('refresh-token/', views.refresh_token, name='refresh_token'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uuid:token>/', views.reset_password, name='reset_password'),
    path('reset-password-confirm/', views.reset_password_confirm, name='reset_password_confirm'),
    path('register/', views.register, name='register')
]
