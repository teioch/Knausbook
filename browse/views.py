#!set encoding=utf8

# For returning user to specified address, as well as defining variables to 
# send along with it
from django.shortcuts import render
# Imports models for database elements Pic, Comment, Tag, Picture_tag
from gallery.models import Pic, Comment, Tag, Picture_tag
# Import Paginator, tool for generating pages with a specified number of 
# objects per page
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Exception handler
from django.core.exceptions import ObjectDoesNotExist
# Django-automated authorized login check for all functions preceeded by 
# "@login_required". Redirects non-logged in users to a login page
from django.contrib.auth.decorators import login_required
# Django-automated tool for popping up message-boxes
from django.contrib import messages
# Django tool for getting date and time, and handling objects of this type
import datetime
# Tool for redirecting users to a specified URL
from django.http import HttpResponseRedirect
# Tool for allowing the use of url names specified in urls.py
from django.core.urlresolvers import reverse

# Function to fetch and return all images to be shown in a grid
@login_required
def index(request):
    image_list = Pic.objects.filter(active = True).order_by('-id')
    paginator = Paginator(image_list,48)

    page = request.GET.get('page')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #If page is not an integer, deliver first page
        images = paginator.page(1)
    except EmptyPage:
        #If page is out of range, deliver last page of results
        images = paginator.page(paginator.num_pages)

    return render(request, 'browse/index.html', {'images':images})

# Function to fetch and present view mode when users are not browsing a 
# specific tag
@login_required
def view(request,bid):
    image = Pic.objects.get(id = bid)

    # If image has been previously deactivated, send user back to the browse
    # overview along with popping a message about said picture being removed
    if image.active == False:
        messages.warning(request, 'Dette bildet er slettet.')
        return HttpResponseRedirect(reverse('browse'))
    
    tags = Tag.objects.select_related().filter(picture_tag__picture = image)
    comments = Comment.objects.select_related().filter(picture_id = bid)

    # If user filled out a form
    if request.method == "POST":
        # If a field named 'comment' has been filled out
        if request.POST.get('comment'):
            comment_model = set_comment_meta(request,bid)
            if len(comment) > 200:
                messages.warning(request,'Kommentaren din er på %s tegn.' + 
                    'Den kan ikke være lenger enn 200 tegn.' + 
                    % (len(comment)))
            else:
                # Save the comment model to database
                comment_model.save()
                # Trigger confirm message
                messages.info(request,'Kommentar lagt til.')
    
    # Assign currently logged in user to variable
    currently_logged_in_as = request.user
    prev_image = get_prev_image(bid)
    next_image = get_next_image(bid)

    return render(request, 'browse/view.html', {
        'image':image,
        'next_image':next_image,
        'prev_image':prev_image,
        'tags':tags,
        'comments':comments,
        'currently_logged_in_as':currently_logged_in_as
        })

def get_prev_image(bid):
    prev_id = str(int(bid) + 1)
    found = False
    while not found:
        if int(bid) <= get_oldest_active_id(bid):
            if Pic.objects.get(id=prev_id).active == True:
                prev_image = Pic.objects.get(id=prev_id)
                found = True
            else:
                prev_id = str(int(prev_id) + 1)
        elif int(bid) == get_newest_active_id(bid):
            prev_image = Pic.objects.get(id = get_oldest_active_id(bid))
            found = True
        else:
            if Pic.objects.get(id=prev_id).active == True:
                prev_image = Pic.objects.get(id=prev_id)
                found = True
            else:
                prev_id = str(int(prev_id) + 1)
    return prev_image

def get_next_image(bid):
    found = False
    next_id = str(int(bid) - 1)

    while not found:
        if int(bid) <= get_oldest_active_id(bid):
            next_image = Pic.objects.get(id=get_newest_active_id(bid))
            found = True
        elif int(bid) == get_newest_active_id(bid):
            if Pic.objects.get(id=next_id).active == True:
                next_image = Pic.objects.get(id=next_id)
                found = True
            else:
                next_id = str(int(next_id) - 1)
        else:
            if Pic.objects.get(id=next_id).active == True:
                next_image = Pic.objects.get(id=next_id)
                found = True
            else:
                next_id = str(int(next_id) - 1)
    return next_image

def set_comment_meta(request, bid):
    # Assign content from comment-field to 'comment'
    comment = request.POST.get('comment')
    comment_model = Comment()
    comment_model.picture = Pic.objects.get(id=bid)
    comment_model.user = request.user
    comment_model.comment = comment
    comment_model.submitted = datetime.datetime.now()
    comment_model.ip = request.META['REMOTE_ADDR']

    return comment_model

def get_oldest_active_id(bid):
    iterator = 0
    found = False

    while not found:
        if Pic.objects.all().order_by('id')[iterator].active == True:
            return Pic.objects.all().order_by('id')[iterator].id
        else:
            iterator += 1
            if iterator == 50:
                break
    return bid

def get_newest_active_id(bid):
    iterator = 0
    found = False

    while not found:
        if Pic.objects.all().order_by('-id')[iterator].active == True:
            return Pic.objects.all().order_by('-id')[iterator].id
        else:
            iterator += 1
            if iterator == 50:
                break

    return bid

# Function to "delete" (deactivate) image
@login_required
def delete(request,bid):
    # Fetch image object with id = bid from database
    image = Pic.objects.get(id = bid)
    # Set model field "active" to False, thereby making the image unavailable
    image.active = False
    # Save the updated model to database
    image.save()
    # Trigger success message
    messages.info(request,'Bildet er nå fjernet')
    return HttpResponseRedirect(reverse('browse'))

# Function to present an edit interface to user, as well as handling edit 
# inputs
@login_required
def edit(request,bid):
    image = Pic.objects.get(id = bid)
    tags = Tag.objects.filter(picture_tag__picture = image)    
    prev_image = get_prev_image(bid)
    next_image = get_next_image(bid)
    
    # If user filled out a form
    if request.method=="POST":
        # If that form was the field with the name "tag"
        if request.POST.get('tag', False):
            create_new_tag(request)
            affiliate_tag_to_image(post_tag, bid)

        # If user sent a remove tag request
        if request.POST.get('remove_tag', False):
           delete_tag(request,bid)

    return render(request, 'browse/edit.html', {
        'tags':tags,
        'image':image,
        'prev_image':prev_image,
        'next_image':next_image
        })

def create_new_tag(request):
    post_tag = request.POST['tag']
    try:
        # Try to fetch the inputted tag from the table containing unique 
        # examples of tags used
        exists = Tag.objects.get(title=post_tag)
    except ObjectDoesNotExist:
        # If this fetch fails, we know the tag has never been used before
        #  and we create it from scratch
        new_tag = Tag()
        new_tag.title = post_tag
        new_tag.save()

def affiliate_tag_to_image(post_tag, bid):
    fetched_tag = Tag.objects.get(title=post_tag)
    image = Pic.objects.get(id = bid)
    try:
        # Try to get one tag matching user input from the list of tags 
        # accociated with the image
        tag = tags.get(title=post_tag)
        # If this is successful, we know that the tag is already accociated 
        # with the image, and there is no need to add it again
        already_registered = True
    except ObjectDoesNotExist:
        # If we are unable to fetch the tag from the list, then it has not 
        # been accociated with the image and we can perform the affiliation
        already_registered = False
        
    if already_registered:
        messages.warning(request, 'Bildet er allerede tagget med %s' + 
            % (post_tag))
    else:
        tag_input = Picture_tag()
        tag_input.picture = image
        tag_input.tag = fetched_tag
        tag_input.save()

        messages.info(request, u'Bildet er nå tagget med %s' % (post_tag))

def delete_tag(request, bid):
    rm_tag= Tag.objects.get(title=request.POST['remove_tag'])
    rm_pic = Pic.objects.get(id=bid)
    rm_pic_tag = Picture_tag.objects.get(tag = rm_tag,picture = rm_pic)
    rm_pic_tag.delete()
    messages.info(request, u'Fjernet tag %s fra bildet' % (rm_tag.title))


# This function does the same as 'def view'. The only difference is the 
# ammount of arguments it takes in to set the basis for what images are
# retrieved.
@login_required
def tagview(request,t_id,p_id):
    images = Pic.objects.filter(picture_tag__tag=t_id).order_by('-date')
    image = images.get(id=p_id)
    tags = Tag.objects.filter(picture_tag__picture = image)
    comments = Comment.objects.filter(picture_id = p_id)
    current_tag = Tag.objects.get(id=t_id)

    # If user filled out a form on the previous page
    if request.method == "POST":
        # If the form filled out was named 'comment'
        if request.POST.get('comment'):
            new_comment = request.POST.get('comment')
            comment_model = Comment()
            comment_model.picture = Pic.objects.get(id=p_id)
            comment_model.user = request.user
            comment_model.comment = new_comment
            comment_model.submitted = datetime.datetime.now()
            comment_model.ip = request.META['REMOTE_ADDR']

            # If comment is over 200 characters
            if len(new_comment) > 200:
                messages.warning(request, 'Kommentaren din er på %s tegn.' + 
                    ' Den kan ikke være lenger enn 200 tegn.' + 
                    % (len(new_comment)))
            else:
                # Save model to database
                comment_model.save()
                messages.info(request, 'Kommentar lagt til.')
    
    # Fetch the username of the currently logged in user.
    currently_logged_in_as = request.user

    try:
        #Does the same as in def view, only here it looks for the next image
        # that also has the same tag t_id as before, based on date.
        next_tag_image = images.filter(picture_tag__tag=t_id, 
            date__lt=image.date)[0]
    except:
        next_tag_image = None
    try:
        #Again, the same as in def view, only based on a tag.
        prev_tag_image = images.filter(picture_tag__tag=t_id, 
            date__gt=image.date).reverse()[0]
    except:
        prev_tag_image = None

    return render(request, 'browse/view.html', {
        'image':image,
        'next_tag_image':next_tag_image,
        'prev_tag_image':prev_tag_image,
        't_id':t_id,
        'current_tag':current_tag,
        'tags':tags,
        'comments':comments,
        'currently_logged_in_as':currently_logged_in_as
        })
