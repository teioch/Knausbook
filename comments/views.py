from django.shortcuts import render, get_object_or_404
from gallery.models import Comment
# Django-automated implementation for presenting user with pages of data. Arguments (QuerySet data list, number of elements per page)
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages

# /comments/
@login_required
def show(request):
    # Requests all comments from database and filters out the comments 
    # associated with images that has been deactivated. Sorted by newest 
    # first, oldest last
    comments_list = Comment.objects.select_related().filter(picture__active =
        True).order_by('-submitted')

    paginator = Paginator(comments_list,20)
    page = request.GET.get('page')

    try:
        # Attempt to load a subset 'comments' from comments_list to match the
        # current page.
        comments = paginator.page(page)
    except PageNotAnInteger:
        # If the page specified in 'page' is not a number, return by default 
        # page number 1
        comments = paginator.page(1)
    except EmptyPage:
        # If the page selected doesn't contain any elements at all, return 
        # the last page that does contain elements.
        comments = paginator.page(paginator.num_pages)

    return render(request, 'comments/show.html', {'comments':comments})

@login_required
def delete(request, c_id, t_id=None):
    comment = get_object_or_404(Comment,id=c_id)
    b_id = comment.picture.id

    # If the user requesting the deletion (the logged in user) is in fact the
    # original author
    if comment.user == request.user:
        comment.delete()
        messages.info(request,'Kommentar ble slettet')
    else:
        messages.warning(request,'Sletting feilet: Det er ikke du som skrev dette.')
    
    # If tag id is specified
    if not t_id==None:
        # Return to view web page that is based on a specified tag
        return HttpResponseRedirect('/browse/view/%s/%s/' % (t_id,b_id))
    else:
        # Or return to view web page based on total collection
        return HttpResponseRedirect('/browse/view/%s' % (b_id))
