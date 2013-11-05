from gallery.models import Tag, Pic
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

@login_required
def list_tags(request):
    tags = Tag.objects.all().order_by('title') #QuerySet, fetches all tags from database sorted by their name
    return render(request,'tags/listTags.html',{'tags':tags})

@login_required
def expand(request,t_id):
    #Pick out only the images mentioned with tag_id in 't_id'.
    image_list = Pic.objects.filter(picture_tag__tag = t_id, active = True).order_by('-id') #QuerySet, fetches images matching id from the tag-list.

    paginator = Paginator(image_list,48) #Initiate Paginator, a tool for page handling. Arguments (list of objects, desired number of objects per page)
    page = request.GET.get('page') #Fetches current page from URL

    try:
        images = paginator.page(page) #Returns objects belonging to desired page.
    except PageNotAnInteger:
        #If page is not an integer, deliver first page
        images = paginator.page(1)
    except EmptyPage:
        #If page is out of range, deliver last page of results
        images = paginator.page(paginator.num_pages)

    return render(request, 'tags/listPictures.html', {'images':images, 't_id':t_id})
