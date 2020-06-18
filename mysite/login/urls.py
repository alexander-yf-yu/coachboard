from django.urls import path, include

from . import views


urlpatterns = [
    path('index', views.index, name='login_index'),
    path('', views.login_view, name='login_main'),
    path('register', views.register, name='register'),
    path('login_fail', views.login_fail, name='login_fail'),
]