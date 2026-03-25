from django.shortcuts import render,redirect
from assignments.models import Assignment
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from django.http import HttpResponse
from django.template.loader import render_to_string
import pdfkit 




@login_required
def dashboard(request):
    # ===== BASIC STATS =====
    total = Assignment.objects.filter(user=request.user).count()
    completed = Assignment.objects.filter(user=request.user, completed=True).count()
    pending = Assignment.objects.filter(user=request.user, completed=False).count()

    # ===== ALERTS =====
    now = timezone.now()
    warning_time = now + timedelta(days=2)

    near_due = Assignment.objects.filter(
        user=request.user,
        completed=False,
        deadline__lte=warning_time,
        deadline__gte=now
    )

    overdue = Assignment.objects.filter(
        user=request.user,
        completed=False,
        deadline__lt=now
    )

    alerts_count = near_due.count() + overdue.count()

    # ===== CHART DATA =====
    today = timezone.now().date()

    # Find Sunday of the current week
    days_since_sunday = today.weekday() + 1  # Monday=0 -> Sunday=6
    sunday = today - timedelta(days=days_since_sunday % 7)

    labels = []
    created_data = []
    completed_data = []

    # Loop from Sunday to Saturday
    for i in range(7):
        day = sunday + timedelta(days=i)
        labels.append(day.strftime("%a"))

        count_created = Assignment.objects.filter(
            user=request.user,
            deadline__date=day
        ).count()

        count_completed = Assignment.objects.filter(
            user=request.user,
            completed=True,
            deadline__date=day
        ).count()

        created_data.append(count_created)
        completed_data.append(count_completed)

    # ===== FINAL CONTEXT =====
    context = {
        'total': total,
        'completed': completed,
        'pending': pending,

        'near_due': near_due,
        'overdue': overdue,
        'alerts_count': alerts_count,

        'labels': labels,
        'created_data': created_data,
        'completed_data': completed_data
    }

    return render(request, 'dashboard/index.html', context)

@login_required
def profile_view(request):
    user = request.user

    # Recent assignments (e.g., last 5)
    recent_assignments = Assignment.objects.filter(user=user).order_by('-deadline')[:5]

    context = {
        'user': user,
        'recent_assignments': recent_assignments,
        'today': timezone.now().date(),  # for overdue calculation in template
    }
    return render(request, 'dashboard/profile.html', context)

@login_required
def edit_profile_view(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'dashboard/edit_profile.html', {'user': request.user})


@login_required
def generate_report(request):
    # ===== Get assignments =====
    assignments = Assignment.objects.filter(user=request.user)

    # ===== Chart data =====
    today = timezone.now().date()
    days_since_sunday = today.weekday() + 1
    sunday = today - timedelta(days=days_since_sunday % 7)

    labels = []
    created_data = []
    completed_data = []

    for i in range(7):
        day = sunday + timedelta(days=i)
        labels.append(day.strftime("%a"))

        created = assignments.filter(deadline__date=day).count()
        completed = assignments.filter(completed=True, deadline__date=day).count()

        created_data.append(created)
        completed_data.append(completed)

    chart_data = zip(labels, created_data, completed_data)

    # ===== Render HTML =====
    html_content = render_to_string('dashboard/report_template.html', {
        'assignments': assignments,
        'chart_data': chart_data,
        'user': request.user,
    })

    # ===== Generate PDF =====
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    pdf = pdfkit.from_string(html_content, False, configuration=config)

    # ===== Return response =====
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="weekly_report.pdf"'
    return response
