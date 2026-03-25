from django.shortcuts import render, redirect, get_object_or_404
from .models import Assignment
from .forms import AssignmentForm
from django.contrib.auth.decorators import login_required
from .models import Project
from .forms import ProjectForm


@login_required
def assignment_list(request):
    assignments = Assignment.objects.filter(user=request.user)
    return render(request, 'assignments/list.html', {'assignments': assignments})


@login_required
def add_assignment(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.user = request.user
            assignment.save()
            return redirect('assignment_list')
    else:
        form = AssignmentForm()

    return render(request, 'assignments/add.html', {'form': form})

def complete_assignment(request, id):
    assignment = Assignment.objects.get(id=id)
    assignment.completed = True
    assignment.save()
    return redirect('assignment_list')

def add(request):
    return render(request,'add.html')

def assignment_detail(request, assignment_id):
    # Fetch the assignment by ID or return 404 if not found
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    context = {
        'assignment': assignment
    }
    
    return render(request, 'assignments/assignment_detail.html', context)

def completed_assignments(request):
    assignments = Assignment.objects.filter(completed=True)
    return render(request, 'assignments/completed_assignments.html', {
        'assignments': assignments
    })
    
def update_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return redirect('assignment_list')   # or dashboard
    else:
        form = AssignmentForm(instance=assignment)

    return render(request, 'assignments/update_assignment.html', {'form': form})

def project_list(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        progress = request.POST.get("progress")

        project = get_object_or_404(Project, id=project_id, user=request.user)
        project.progress = int(progress)
        project.save()

        return redirect('project_list')

    projects = Project.objects.filter(user=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})

def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'projects/create_project.html', {'form': form})

def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')  # back to list
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/edit_project.html', {'form': form})