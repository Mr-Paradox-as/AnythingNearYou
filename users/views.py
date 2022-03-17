from email import message
from importlib.resources import is_resource
import profile
import re
from unicodedata import name
from django.http import request
from django.shortcuts import redirect, render
from django.template import context
from django.db.models import Q
from .models import Profile, Skill, Message
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, Profileform, Skillform, Messageform
# Create your views here.
#skill file error in userprofile

def loginUser(request):
    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')


    if request.method == "POST":
        username =  request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request,'User does not exist')
        
        user = authenticate(request, username=username,password=password)


        if user is not None:
            login(request, user)
            return redirect('profiles')
        else:
            messages.info(request, 'Username and Password is incorrect')


    return render(request, 'users/login_register.html' )

def logoutUser(requset):
    logout(requset)
    return redirect('login')

def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            
            messages.success(request, 'User accout was created!')

            login(request, user)
            return redirect('edit-account')
        
        else:
            messages.success(request, 'An error has occured during registration..')


    context = {'page': page,'form':form}
    return render(request, 'users/login_register.html', context)

def profiles(request):
    search_query = ''
    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    skills = Skill.objects.filter(name__icontains=search_query)
    
    profiles = Profile.objects.distinct().filter(
        Q(name__icontains=search_query)|Q(short_intro__icontains=search_query)|Q(skill__in=skills))
    context = {'profiles': profiles, 'search_query':search_query}
    return render(request, 'users/profiles.html', context)


def userProfile(request,pk):
    profile = Profile.objects.get(id=pk)

    
    skills = profile.skill_set.all()

    context = {'profile':profile, 'skills':skills}
    
    return render(request, 'users/user-profile.html',context)

@login_required(login_url='login')
def userAccount(request):
    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {'profile':profile, 'skills':skills, 'projects': projects}
    return render(request,'users/account.html',context)


@login_required(login_url='login')
def editAccount(request):
    profile = request.user.profile
    form = Profileform(instance=profile)
    if request.method == 'POST':
        form = Profileform(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()

            return redirect('account')
    context = {'form':form}
    return render(request,'users/profile_form.html', context)
@login_required(login_url='login')
def createSkill(request):
    profile = request.user.profile
    form = Skillform()

    if request.method == 'POST':
        form = Skillform(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.success(request, 'Resource was added succesfully!')
            return redirect('account')

    context = {'form':form}
    return render(request,'users/skill_form.html',context)

@login_required(login_url='login')
def updateSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    form = Skillform(instance=skill)

    if request.method == 'POST':
        form = Skillform(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource was updated succesfully!')
            return redirect('account')
            
    context = {'form':form}
    return render(request,'users/skill_form.html',context)

@login_required(login_url='login')
def deleteSkill(request, pk):
    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)
    context = {'object':skill}
    if request.method == 'POST':
        skill.delete()
        return redirect('account')
    return render(request, 'delete_template.html',context)

@login_required(login_url='login')
def inbox(request):
    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()
    context= {'messageRequests':messageRequests,'unreadCount': unreadCount}
    return render(request, 'users/inbox.html',context)
    
@login_required(login_url='login')
def viewMessage(request,pk):
    profile = request.user.profile
    message = profile.messages.get(id = pk)
    if message.is_read == False:
        message.is_read = True
        message.save()
    context = {'message':message}
    return render(request,'users/message.html',context)

@login_required(login_url='login')
def createMessage(request,pk):
    recipient = Profile.objects.get(id=pk)
    form = Messageform()
    try:
        sender = request.user.profile
    except:
        sender = None 
    if request.method == 'POST':
        form = Messageform(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email
            message.save()

            messages.success(request,'Your message was succesfully sent!')
            return redirect('user-profile', pk=recipient.id)
    context = {'recipient':recipient,'form':form}
    return render(request,'users/message_form.html',context)
