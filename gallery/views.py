#!set ecoding=utf8

# Import models from gallery
from gallery.models import Pic,Comment,Tag
# Import settings.py
from django.conf import settings
# Tools for redirecting user to pages
from django.http import HttpResponseRedirect, HttpRequest
# Tool to redirect user to page and accociated variables in the same go
from django.shortcuts import render
# Import os; datetime; which is for getting and handling dates and hours. 
# time; which is in this case used to fetch unix timestamp. 
# ExifTags; which is used to read exif metadata from images, in this case to
# make sure if the image is rotated or not
import os, datetime, time, ExifTags
# Django tool to read/write files from/to disk
from django.core.files.storage import FileSystemStorage
# Django tool to pop message boxes to user
from django.contrib import messages
# Python tool to process image size and filters etc.
from PIL import Image
# Django tool to require user authentication to specific functions
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    latest_images = Pic.objects.all().order_by('-id')[:5]

    return render(request,'base/index.html',{'latest_images': latest_images})

@login_required
def upload(request):
    # Set the uplaod directories
    # Fullsize is unique because a different tool saves this image. The rest 
    # are handled by PIL, which uses a simple string instead.
    destination_fullsize = FileSystemStorage(location='%sgallery/fullsize' 
        % (settings.MEDIA_ROOT))
    destination_medium = '%sgallery/medium/' % (settings.MEDIA_ROOT)
    destination_thumb = '%sgallery/thumb/' % (settings.MEDIA_ROOT)
    fullsize_folder = '%sgallery/fullsize/' % (settings.MEDIA_ROOT)

    # If method used is POST it can be safely assumed an upload is being 
    # attempted
    if request.method == 'POST':
        # If the request comes with files attached.
        if len(request.FILES):
            user = request.user
            ip = request.META['REMOTE_ADDR']
            user_filename = '%s_%i' % (user,time.time())
            incrementer = 1

            for f in request.FILES.getlist('files'):
                # For every file, generate data to be input into models.
                date = datetime.datetime.now()
                filename = '%s_%i.%s' % (user_filename, 
                                         incrementer, 
                                         f.content_type.split("/")[1])
                picture = Pic()
                picture.title = f.name
                picture.date = date
                picture.user = user
                picture.filename = filename
                picture.active = 1
                picture.ip = ip
                picture.save()

                incrementer = incrementer + 1

                destination_fullsize.save(filename, f)
                image = Image.open('%s%s' % (fullsize_folder, filename))
                
                # The following step is necessary because PIL ignores 
                # exif-data and doesn't store new images with it. This means
                # that images taken with a tilted camera will be lying on 
                # the side when presented in this gallery. Unless the
                # following step is run that is.    
                try:
                    # Look up all known Exif datatypes from ExifTags and traverse them
                    for orientation in ExifTags.TAGS.keys():
                        # When the iteration finds the orientation field, break up. Using break will make ExifTags.TAGS[orien.] keep what it currently have
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                 
                    try:
                        # Get all exif-data for the current image.
                        exif = dict(image._getexif().items())
                    except:
                        exif = dict()
                    # The following statements checks the exif-data to see if
                    # the image is rotated through exif-data. If so, the 
                    # image is force-rotated to be in the right position even
                    # without exif-data. 
                    # NOTE: Not all camera uses the numbers 3, 6 and 8 for 
                    # orientation definitions and this *may* not always work.
                    # If a problem occurs with this, check the exif-data of 
                    # the image manually and add the correct values for that 
                    # image to this code.
                    if exif[orientation] == 3:
                        image_medium = image.rotate(180, expand=True)
                        image_thumb = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image_medium = image.rotate(270, expand=True)
                        image_thumb = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image_medium = image.rotate(90, expand=True)
                        image_thumb = image.rotate(90, expand=True)
                    # If exif-orientation data is found, but no match is 
                    # made, fallback to just add the image as it is.
                    else:
                        image_medium = image
                        image_thumb = image
                except:
                    # If the exif-data is of a format that we can't read, 
                    # fallback to save image as it is.
                    image_medium = image
                    image_thumb = image
                
                # PIL creates a smaller image of the fullsized image. Scale
                # is intact, and resized so that the longest side (height or
                # width) is no larger than 860 and 260 pixels respectively.
                image_medium.thumbnail((860,860), Image.ANTIALIAS)
                image_medium.save('%s%s' % 
                                 (destination_medium, filename), 
                                 'JPEG', 
                                 quality=75)
                
                image_thumb.thumbnail((260,260), Image.ANTIALIAS)
                image_thumb.save('%s%s' % 
                                (destination_thumb, filename), 
                                'JPEG', 
                                quality=75)

            messages.info(request, 'Upload vellykket!')
            return HttpResponseRedirect('/upload/') 
    
        else:
            messages.warning(request, 'Det oppstod en feil.' + 
                ' Ingen bilder lastet opp')
    return render(request, 'gallery/upload.html')

