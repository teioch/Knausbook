Knausbook
=========

A picture gallery system written (in django) for a local choir. 

The system is a basic tag based system. There is currently no search system in it. Only an overview of active tags.

The system supports multiple images uploaded in one batch.

Images "deleted" are not in fact deleted from neither database, nor the server, but marked as "inactive". Access to these images via the system is not supported. The reason for this functionality is to allow anyone to delete whatever they want, while avoiding loss of data due to malicious users.

Each image has its own comment field where users can write.

Each user can choose what they would like their shown profile name to be, while user name remains the same.

There is no application to obtain a username. Only a sysadmin can create a new user through the Django-admin interface.

Note that only the files that have been altered or written by me (ie. files unique for this system, ie. non-django-created files) are contained in this git repository. Simply copying this repo will not result in a functioning system.
