from email import message
import profile
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Profile
from django.conf import settings
from django.core.mail import send_mail

#@receiver(post_save, sender = Profile)
def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
        user = user,
        username = user.username,
        email = user.email,
        name = user.first_name,
        )
        subject = 'Welcome to ANY'
        message = 'We are glad you are here!.                                                                                                                                                                                                       This is a platform on which you can share your resources to others and buy the resources you are looking for.The main reason behind creating this website is that there is a lot of thing a student buys for their particular Semester but when the semester is over those thing means nothing to them. e.g., QUANTUM books, Sheets_box, Minidrafter, Notes etc. So now its up to how you use this platform. but this is just a platform what really going to make it work your love and support.So keep sharing and Using ANY .                                                                                                                                                                                                                                                                                                  Thank You!'
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,

        )


def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user
    if created == False:
        user.first_name = profile.name
        user.username = profile.username
        user.email = profile.email
        user.save()


def deleteUser(sender, instance, **kwargs):
    user = instance.user
    user.delete()

post_save.connect(createProfile, sender= User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender = Profile)
    

