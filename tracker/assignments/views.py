from django.shortcuts import render, redirect, get_object_or_404 
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField, Q
from django.contrib import messages
from .models import Assignment, Project
from .forms import AssignmentForm, ProjectForm

# =========================
# ASSIGNMENT VIEWS
# =========================

@login_required
def assignment_list(request):
    # Start with assignments for the current user
    assignments = Assignment.objects.filter(user=request.user)

    # 🔍 SEARCH
    query = request.GET.get('q')
    if query:
        assignments = assignments.filter(Q(title__icontains=query) | Q(subject__icontains=query))

    # 🔍 FILTERING
    priority_filter = request.GET.get('priority')
    status_filter = request.GET.get('status')

    if priority_filter:
        assignments = assignments.filter(priority=priority_filter)

    if status_filter == 'completed':
        assignments = assignments.filter(completed=True)
    elif status_filter == 'pending':
        assignments = assignments.filter(completed=False)

    # 🔥 PRIORITY SORTING
    assignments = assignments.annotate(
        priority_order=Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            output_field=IntegerField(),
        )
    ).order_by('priority_order', 'deadline')

    return render(request, 'assignments/list.html', {'assignments': assignments})


@login_required
def add_assignment(request):
    if request.method == "POST":
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.user = request.user
            assignment.save()
            messages.success(request, "Assignment added successfully!")
            return redirect('assignment_list')
    else:
        form = AssignmentForm()
    return render(request, 'assignments/add.html', {'form': form})


@login_required
def complete_assignment(request, id):
    assignment = get_object_or_404(Assignment, id=id, user=request.user)
    assignment.completed = True
    assignment.save()
    messages.success(request, "Assignment marked as complete!")
    return redirect('assignment_list')


@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, user=request.user)
    return render(request, 'assignments/assignment_detail.html', {'assignment': assignment})


@login_required
def completed_assignments(request):
    assignments = Assignment.objects.filter(user=request.user, completed=True)
    return render(request, 'assignments/completed_assignments.html', {'assignments': assignments})


@login_required
def update_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk, user=request.user)

    if request.method == "POST":
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('assignment_list')
    else:
        form = AssignmentForm(instance=assignment)

    return render(request, 'assignments/update_assignment.html', {'form': form})


# =========================
# PROJECT VIEWS
# =========================

@login_required
def project_list(request):
    if request.method == "POST":
        project_id = request.POST.get("project_id")
        progress = request.POST.get("progress")
        project = get_object_or_404(Project, id=project_id, user=request.user)
        project.progress = int(progress)
        project.save()
        messages.success(request, f"Progress updated for project: {project.title}")
        return redirect('project_list')

    projects = Project.objects.filter(user=request.user)
    return render(request, 'projects/project_list.html', {'projects': projects})


@login_required
def create_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, "Project created successfully!")
            return redirect('project_list')
    else:
        form = ProjectForm()

    return render(request, 'projects/create_project.html', {'form': form})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)

    return render(request, 'projects/edit_project.html', {'form': form})