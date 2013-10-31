#!set ecoding=utf8
from gallery.models import Pic,Comment,Tag                  # Import models from gallery
from django.conf import settings                            # Import settings.py
from django.http import HttpResponseRedirect, HttpRequest   # Import tools for redirecting user to pages
from django.shortcuts import render                         # Import tool to redirect user to page and accociated variables in the same go
import os, datetime, time, ExifTags                         # Import os; datetime; which is for getting and handling dates and hours. time; which is in this case used to fetch unix timestamp. ExifTags; which is used to read exif metadata from images, in this case to make sure if the image is rotated or not
from django.core.files.storage import FileSystemStorage     # Django tool to read/write files from/to disk
from django.contrib import messages                         # Django tool to pop message boxes to user
from PIL import Image                                       # Python tool to process image size and filters etc.
from django.contrib.auth.decorators import login_required   # Django tool to require user authentication to specific functions

@login_required
def index(request):
    latest_images = Pic.objects.all().order_by('-date')[:5] #QuerySet, returns the five newest images.

    return render(request,'base/index.html',{'latest_images': latest_images})

@login_required
def upload(request):
    # Set the uplaod directories
    # Fullsize is unique because a different tool saves this image. The rest are handled by PIL, which uses a simple string instead.
    #destination_fullsize = FileSystemStorage(location='/srv/vhost/candiss/knausbook/media/gallery/fullsize')
    destination_fullsize = FileSystemStorage(location='%sgallery/fullsize' % (settings.MEDIA_ROOT))
    destination_medium = '%sgallery/medium/' % (settings.MEDIA_ROOT)
    destination_thumb = '%sgallery/thumb/' % (settings.MEDIA_ROOT)
    fullsize_folder = '%sgallery/fullsize/' % (settings.MEDIA_ROOT)

    if request.method == 'POST':             # Check for POST-tag from the web page to see if an upload is attempted
        if len(request.FILES):               # Check to see that the FILES-tag from the web page actually contains files.

            user = request.user              # Fetches the currently logged in user
            ip = request.META['REMOTE_ADDR'] # Fetches the user's IP-address
            user_filename = '%s_%i' % (user,time.time())
            incrementer = 1

            for f in request.FILES.getlist('files'):
                # For every file, generate data to be input into models.
                date = datetime.datetime.now()   # Fetches current date
                filename = '%s_%i.%s' % (user_filename, incrementer, f.content_type.split("/")[1]) # Generate filename. Based on username + unix timestamp + the filetype of the uploaded file.
                picture = Pic()              # Create Pic object for models
                picture.title = f.name       # Set title name to be the name of the uploaded file
                picture.date = date          # Set date
                picture.user = user          # Sets username on who uploaded the image
                picture.filename = filename  # Set filename
                picture.active = 1           # Set active = true
                picture.ip = ip              # Set IP address
                picture.save()               # Saves input data to models and thereby to database as well.

                incrementer = incrementer + 1              # Incrementing ID to guarantee unique filenames

                destination_fullsize.save(filename, f)                   # Saves image to disk in directory specified in destination_fullsize initiation. 
                image = Image.open('%s%s' % (fullsize_folder, filename)) # Uses PIL to open the saved image (line above this one).
                

                try:                                                     # This step is necessary because PIL ignores exif-data and doesn't store new images with it. This means that images taken with a tilted camera will be lying on the side when presented.
                    for orientation in ExifTags.TAGS.keys():             # Look up all known Exif datatypes from ExifTags and traverse them
                        # When the iteration finds the orientation field, break up. Using break will make ExifTags.TAGS[orien.] keep what it currently have
                        if ExifTags.TAGS[orientation] == 'Orientation' : break
                 
                    try:
                        exif = dict(image._getexif().items())                # Get all exif-data for the current image.
                    except:
                        exif = dict()
                    # The following statements checks the exif-data to see if the image is rotated through exif-data. If so, the image is force-rotated to be in the right position even without exif-data
                    # NOTE: Not all camera uses the numbers 3, 6 and 8 for orientation definitions and this *may* not always work.
                    # If a problem occurs with this, check the exif-data of the image manually and add the correct values for that image to this code.
                    if exif[orientation] == 3:
                        image_medium = image.rotate(180, expand=True)
                        image_thumb = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image_medium = image.rotate(270, expand=True)
                        image_thumb = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image_medium = image.rotate(90, expand=True)
                        image_thumb = image.rotate(90, expand=True)
                    # If exif-orientation data is found, but no match is made, fallback to just add the image as it is.
                    else:
                        image_medium = image
                        image_thumb = image
                except:
                    # If the exif-data is of a format that we can't read, fallback to save image as it is.
                    image_medium = image
                    image_thumb = image
                
                image_medium.thumbnail((860,860), Image.ANTIALIAS) # PIL creates a smaller image of the fullsized image. Scale is intact, and resized so that the longest side (height or width) is no larger than 860 pixels.
                image_medium.save('%s%s' % (destination_medium, filename), 'JPEG', quality=75) # Image is saved. Arguments (Address and filename, image type, image quality)
                
                image_thumb.thumbnail((260,260), Image.ANTIALIAS)
                image_thumb.save('%s%s' % (destination_thumb, filename), 'JPEG', quality=75)

            messages.info(request, 'Upload vellykket!') # Creates an animated message box with a confirmation that the operation was successful
            return HttpResponseRedirect('/upload/') 
    
        else:
            messages.warning(request, 'Det oppstod en feil. Ingen bilder lastet opp') # Creates animated message box, telling the user operation failed.
    return render(request, 'gallery/upload.html')

