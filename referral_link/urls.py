from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.auth_test, name='auth_test'),
    path('auth/send_code/', views.get_code, name='send_code'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('enter_code/', views.enter_code, name='enter_code'),
]
