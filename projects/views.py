import imp
import profile
from turtle import title
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.template import context
from django.db.models import Q 

from users import urls
from .models import Project,Tag
from .forms import ProjectForm
from django.http import HttpResponse



def projects(request):
    search_query = ''

    if request.GET.get('search_query'):
        search_query = request.GET.get('search_query')

    projects = Project.objects.distinct().filter(Q(title__icontains = search_query)|Q(description__icontains=search_query)|Q(owner__name__icontains=search_query))
    context = {'projects':projects,'search_query':search_query}
    return render(request, 'projects/projects.html', context)

def project(request, pk):
    projectObj = Project.objects.get(id=pk)
    tags = projectObj.tags.all()
    print('proejctObj',projectObj)
    return render(request, 'projects/single-project.html',{'project':projectObj,'tags':tags})

@login_required(login_url="login")
def createProject(requset):
    profile = requset.user.profile
    form = ProjectForm(requset.POST, requset.FILES)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = profile
        project.save()
        return redirect ('account')
    
    context = {'form':form}
    return render(requset,"projects/project_form.html",context)

@login_required(login_url="login")
def updateProject(request,pk):
    profile = request.user.profile

    project = profile.project_set.get(id=pk)
    form = ProjectForm(instance=project)

    if request.method == 'POST':
        form = ProjectForm(request.POST,request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('account')

    context = {'form':form}
    return render(request,"projects/project_form.html", context)

@login_required(login_url="login")
def deleteProject(request, pk):
    project = Project.objects.get(id=pk)
    if request.method == 'POST':
        project.delete()
        return redirect('projects')
    context = {'object':project}
    return render(request, 'delete_template.html',context)
