#!set encoding=utf8
# The line above forces encoding of the page to be utf8. Unknown why this is required, but without it, the page fails
from django.contrib.auth.models import User                 # Import User models from django-automated user administration
from django.contrib import messages                         # Import messages-tool, for printing dynamic, boxed messages
from django.shortcuts import render                         # Import render, tool for redirecting user to specific URL along with accociated variables
from django.contrib.auth.decorators import login_required   # Django tool for authenticating users before accessing functions

@login_required
def changepwd(request):
    # If user filled out a form on previous page
    if request.method == "POST":
        # If that form field was "password_one" and "password_two"
        if request.POST.get('password_one') and request.POST.get('password_two'):
            # Assign input passwords to variables
            pwd_one = request.POST['password_one']
            pwd_two = request.POST['password_two']
            # Assign currently logged in user to u
            u = request.user
            
            # If the two input passwords are the same
            if pwd_one == pwd_two:
                # Assign password on user to the newly input password. (Django knows this is a password and automatically hashes it to encrypt it)
                u.set_password('%s' % (pwd_one))
                # Save edits on user model to database.
                u.save()
                messages.info(request, 'Passordendring var vellykket')
            else:
                messages.info(request, 'Du tastet inn forskjellige passord')

        # End request.POST.get('password')
        # If user filled out form post named "name"
        if request.POST.get('name'):
            # Assign user input to new_name
            new_name = request.POST.get('name')
            # Assign currently logged in user to 'user'
            user = request.user
            # Alter currently logged in user's model field 'first_name' to input
            user.first_name = new_name
            try:
                # Attempt a save
                user.save()
                messages.info(request, 'Navneendring utført.')
            except:
                # Throw error message if failed. (Though there is no real rason why it should fail. It is better to be safe however, as the field is required to be able to log in. If something fails it is better to catch it and reject it)
                messages.warning(request, 'Noe gikk galt! Navneendring ikke utført.')
        # End if request.Get.get('name')
    # End request.method == POST
    
    # Fetch first_name of the logged in user. Used to input to form "name" in profile page to show what is currently registered.
    first_name = request.user.first_name

    return render(request, 'profile/profile.html', {'first_name':first_name})

