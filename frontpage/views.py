# Import render, tool to send requests to specified URL along with 
# accociated variables
from django.shortcuts import render
# Import settings file (settings.py)
from django.conf import settings
# Import Pic from models
from gallery.models import Pic
# Import django tools for user authentication
from django.contrib.auth import authenticate, login, logout
# Import django tool for checking if user is authenticated or not
from django.contrib.auth.decorators import login_required

def index(request):
    # If user has pressed the logout button
    if request.GET.get('logout'):
        # Log user out (set session cookie = 0)
        logout(request)
    # If user is authenticated
    if request.user.is_authenticated():
        latest = Pic.objects.filter(active=True).order_by('-id')[:9]
        return render(request,'frontpage/main.html',{'latest':latest})
    # Else if user is not authenticated, let user see the login screen
    else:
        return render(request,'accounts/login/login.html')
