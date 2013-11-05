#!set encoding=utf8
# The line above forces encoding of the page to be utf8. 
# Unknown why this is required, but without it, the page fails

# Import User models from django-automated user administration
from django.contrib.auth.models import User
# Import messages-tool, for printing dynamic, boxed messages
from django.contrib import messages
# Import render, tool for redirecting user to specific URL along with 
# accociated variables
from django.shortcuts import render
# Django tool for authenticating users before accessing functions
from django.contrib.auth.decorators import login_required

@login_required
def changepwd(request):
    # If user filled out a form on previous page
    if request.method == "POST":
        # If that form field was "password_one" and "password_two"
        if request.POST.get('password_one') and request.POST.get('password_two'):
            pwd_one = request.POST['password_one']
            pwd_two = request.POST['password_two']
            u = request.user
            
            # If the two input passwords are the same
            if pwd_one == pwd_two:
                u.set_password('%s' % (pwd_one))
                u.save()
                messages.info(request, 'Passordendring var vellykket')
            else:
                messages.info(request, 'Du tastet inn forskjellige passord')

        # If user filled out form post named "name"
        if request.POST.get('name'):
            new_name = request.POST.get('name')
            user = request.user
            user.first_name = new_name
            try:
                user.save()
                messages.info(request, 'Navneendring utført.')
            except:
                # Throw error message if failed.
                messages.warning(request, 'Noe gikk galt! Navneendring ikke utført.')
    
    first_name = request.user.first_name

    return render(request, 'profile/profile.html', {'first_name':first_name})

