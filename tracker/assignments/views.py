from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField, Q
from django.contrib import messages

from .models import Assignment, Project
from .forms import AssignmentForm, ProjectForm


# =========================
# ASSIGNMENT LIST
# =========================

@login_required
def assignment_list(request):

    role = request.user.profile.role

    if role == 'student':
        assignments = Assignment.objects.filter(assigned_to=request.user)

    elif role == 'teacher':
        assignments = Assignment.objects.filter(created_by=request.user)

    else:
        assignments = Assignment.objects.all()

    # SEARCH
    query = request.GET.get('q')
    if query:
        assignments = assignments.filter(
            Q(title__icontains=query) |
            Q(subject__icontains=query)
        )

    # FILTERING
    priority_filter = request.GET.get('priority')
    status_filter = request.GET.get('status')

    if priority_filter:
        assignments = assignments.filter(priority=priority_filter)

    if status_filter == 'completed':
        assignments = assignments.filter(completed=True)
    elif status_filter == 'pending':
        assignments = assignments.filter(completed=False)

    # PRIORITY SORTING
    assignments = assignments.annotate(
        priority_order=Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            output_field=IntegerField(),
        )
    ).order_by('priority_order', 'deadline')

    return render(request, 'assignments/list.html', {
        'assignments': assignments,
        'role': role
    })


# =========================
# CREATE ASSIGNMENT
# =========================

@login_required
def add_assignment(request):

    if request.user.profile.role != 'teacher':
        messages.error(request, "Only teachers can create assignments.")
        return redirect('assignment_list')

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES)

        if form.is_valid():
            assignment = form.save(commit=False)

            assignment.created_by = request.user

            assigned_student = request.POST.get('assigned_to')
            if assigned_student:
                assignment.assigned_to_id = assigned_student

            assignment.save()

            messages.success(request, "Assignment created successfully!")
            return redirect('assignment_list')

    else:
        form = AssignmentForm()

    return render(request, 'assignments/add.html', {
        'form': form
    })


# =========================
# COMPLETE ASSIGNMENT
# =========================

@login_required
def complete_assignment(request, id):

    assignment = get_object_or_404(
        Assignment,
        id=id,
        assigned_to=request.user
    )

    assignment.completed = True
    assignment.save()

    messages.success(request, "Assignment marked as complete!")
    return redirect('assignment_list')


# =========================
# ASSIGNMENT DETAIL
# =========================

@login_required
def assignment_detail(request, assignment_id):

    assignment = get_object_or_404(Assignment, id=assignment_id)

    role = request.user.profile.role

    if role == 'student' and assignment.assigned_to != request.user:
        messages.error(request, "Not allowed.")
        return redirect('assignment_list')

    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment
    })


# =========================
# COMPLETED ASSIGNMENTS
# =========================

@login_required
def completed_assignments(request):

    role = request.user.profile.role

    if role == 'student':
        assignments = Assignment.objects.filter(
            assigned_to=request.user,
            completed=True
        )

    elif role == 'teacher':
        assignments = Assignment.objects.filter(
            created_by=request.user,
            completed=True
        )

    else:
        assignments = Assignment.objects.filter(completed=True)

    return render(request, 'assignments/completed_assignments.html', {
        'assignments': assignments
    })


# =========================
# UPDATE ASSIGNMENT
# =========================

@login_required
def update_assignment(request, pk):

    if request.user.profile.role != 'teacher':
        messages.error(request, "Not allowed.")
        return redirect('assignment_list')

    assignment = get_object_or_404(
        Assignment,
        pk=pk,
        created_by=request.user
    )

    if request.method == "POST":
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)

        if form.is_valid():
            form.save()
            messages.success(request, "Assignment updated successfully!")
            return redirect('assignment_list')

    else:
        form = AssignmentForm(instance=assignment)

    return render(request, 'assignments/update_assignment.html', {
        'form': form
    })


# =========================
# PROJECT LIST
# =========================

@login_required
def project_list(request):

    if request.method == "POST":
        project_id = request.POST.get("project_id")
        progress = request.POST.get("progress")

        project = get_object_or_404(
            Project,
            id=project_id,
            user=request.user
        )

        project.progress = int(progress)
        project.save()

        messages.success(request, f"Progress updated for project: {project.name}")
        return redirect('project_list')

    projects = Project.objects.filter(user=request.user)

    return render(request, 'projects/project_list.html', {
        'projects': projects
    })


# =========================
# CREATE PROJECT
# =========================

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

    return render(request, 'projects/create_project.html', {
        'form': form
    })


# =========================
# EDIT PROJECT
# =========================

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

    return render(request, 'projects/edit_project.html', {
        'form': form
    })