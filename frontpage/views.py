from django.shortcuts import render                         # Import render, tool to send requests to specified URL along with accociated variables
from django.conf import settings                            # Import settings file (settings.py) 
from gallery.models import Pic                              # Import Pic from models
from django.contrib.auth import authenticate, login, logout # Import django tools for user authentication
from django.contrib.auth.decorators import login_required   # Import django tool for checking if user is authenticated or not

# Function for what the front page should contain
def index(request):
    # If user has pressed the logout button
    if request.GET.get('logout'):
        # Log user out (set session cookie = 0)
        logout(request)
    # If user is authenticated
    if request.user.is_authenticated():
        # Set latest to the 9 newest images from database
        latest = Pic.objects.filter(active=True).order_by('-date')[:9]
        return render(request,'frontpage/main.html',{'latest':latest})
    # Else if user is not authenticated, let user see the login screen
    else:
        return render(request,'accounts/login/login.html')
