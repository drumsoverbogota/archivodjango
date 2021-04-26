from django.shortcuts import render

from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView

class LoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login/login.html'
    next_page = '/admin'

class LogoutView(LogoutView):
    next_page = '/'