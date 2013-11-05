from gallery.models import Tag, Pic
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required

@login_required
def list_tags(request):
    tags = Tag.objects.all().order_by('title')
    return render(request,'tags/listTags.html',{'tags':tags})

@login_required
def expand(request,t_id):
    image_list = Pic.objects.filter(picture_tag__tag = t_id, 
                                    active = True).order_by('-id')

    paginator = Paginator(image_list,48)
    page = request.GET.get('page')

    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        images = paginator.page(1)
    except EmptyPage:
        images = paginator.page(paginator.num_pages)

    return render(request, 'tags/listPictures.html', 
        {'images':images, 't_id':t_id})
