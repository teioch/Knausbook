from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'knausbook.views.home', name='home'),
    # url(r'^knausbook/', include('knausbook.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Enable admin interface:
    url(r'^admin/', include(admin.site.urls)),
    # Main index page
    url(r'^$', 'frontpage.views.index', name='frontpage'),
    # Django has finished views.py organizing login. Only template is made
    url(r'^accounts/login/', 'django.contrib.auth.views.login', {'template_name': 'accounts/login/login.html'}, name='login'),
    # Django automated logout function
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='login'),
    # For uploading images
    url(r'^upload/$', 'gallery.views.upload',name='upload'),
    # For getting an overview of all images uploaded to system, sorted in pages.. Shows 48 images per page
    url(r'^browse/$', 'browse.views.index', name='browse'),
    # Shows a page with all tags registered to system. Only unique tags
    url(r'^tags/$', 'tags.views.list_tags', name='tags'),
    # Shows all images that have been tagged with tag_id = (\d+)
    url(r'^tags/expand/(\d+)/$', 'tags.views.expand', name='expand'),
    # Shows a bigger version of the image, allows to choose next and previous image of the grand total collection
    url(r'^browse/view/(\d+)/$', 'browse.views.view', name='view'),
    # Shows an interface to edit details about the image with id = (\d+). Allows adding and removing tags, and deactivating an image
    url(r'^browse/edit/(\d+)/$', 'browse.views.edit', name='edit'),
    # Function to deactivate an image. Processes based on (\d+) and redirects to browse/
    url(r'^browse/delete/(\d+)/$', 'browse.views.delete', name='delete_image'),
    # Extended function of view to support tags. Only difference is pressing next and prev will show next image containing the tag user is currently browsing
    url(r'^browse/view/(\d+)/(\d+)/$', 'browse.views.tagview', name="tagview"),
    # Shows and allows editing of user specific details. (Password and projected name)
    url(r'^profile/$', 'profile.views.changepwd', name="profile"),
    # Shows all comments sorted by date, presented in pages. 20 comments per page.
    url(r'^comments/$', 'comments.views.show', name="comments"),
    # Deletes a comment from the database completely. Sends user back to the image in view mode
    url(r'^comments/delete/(\d+)/$', 'comments.views.delete', name="delete_comment"),
    # Same as normal deletion of comments, only user is redirected to view mode with continued support of the chosen tag
    url(r'^comments/delete/(\d+)/(\d+)/$', 'comments.views.delete', name="tag_delete_comment"),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
