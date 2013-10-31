from django.contrib import admin
from gallery.models import Pic
from gallery.models import Comment
from gallery.models import Tag

admin.site.register(Pic)
admin.site.register(Comment)
admin.site.register(Tag)
