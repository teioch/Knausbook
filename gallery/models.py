# set fileencoding=utf8
from django.db import models
from django.contrib.auth.models import User
#from django.utils import encoding

class Pic(models.Model):
    title = models.CharField(max_length=35)
    date = models.DateTimeField('date uploaded')
    user = models.ForeignKey(User)
    filename = models.CharField(max_length=100)
    ip = models.CharField(max_length=16)
    active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.filename

class Media(models.Model):
    file = models.FileField(upload_to='upload')
    new_upload = models.BooleanField()

class Comment(models.Model):
    picture = models.ForeignKey(Pic)
    user = models.ForeignKey(User)
    comment = models.CharField(max_length=255)
    submitted = models.DateTimeField('date submitted')
    ip = models.CharField(max_length=16)

    def __unicode__(self):
        return self.comment

class Tag(models.Model):
    title = models.CharField(max_length=40)

    def __unicode__(self):
        return self.title

class Picture_tag(models.Model):
    picture = models.ForeignKey(Pic)
    tag = models.ForeignKey(Tag)

    def __unicode__(self):
        return u'%s' % (self.tag.title)

