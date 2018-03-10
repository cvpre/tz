from django.urls import path

from . import views


app_name = 'regauth'

urlpatterns = [
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register/', views.register, name='register'),
    path('change-password/', views.change_password, name='change_password'),
]
