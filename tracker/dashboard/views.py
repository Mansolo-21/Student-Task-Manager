from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import pdfkit
from assignments.models import Assignment


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from assignments.models import Assignment
from notifications.models import Notification


@login_required
def dashboard(request):

    role = request.user.profile.role

    # ===== BASE QUERY =====
    if role == 'student':
        assignments = Assignment.objects.filter(assigned_to=request.user)

    elif role == 'teacher':
        assignments = Assignment.objects.filter(created_by=request.user)

    else:
        assignments = Assignment.objects.all()

    # ===== STATS =====
    total = assignments.count()
    completed = assignments.filter(completed=True).count()
    pending = assignments.filter(completed=False).count()

    # ===== ALERTS =====
    now = timezone.now()
    warning_time = now + timedelta(days=2)

    near_due = assignments.filter(
        completed=False,
        deadline__lte=warning_time,
        deadline__gte=now
    )

    overdue = assignments.filter(
        completed=False,
        deadline__lt=now
    )

    alerts_count = near_due.count() + overdue.count()

    # ===== WEEKLY CHART =====
    today = timezone.now().date()
    days_since_sunday = today.weekday() + 1
    sunday = today - timedelta(days=days_since_sunday % 7)

    labels = []
    total_data = []
    completed_data = []

    for i in range(7):
        day = sunday + timedelta(days=i)
        labels.append(day.strftime("%a"))

        day_assignments = assignments.filter(deadline__date=day)

        total_data.append(day_assignments.count())

        completed_data.append(
            day_assignments.filter(completed=True).count()
        )

    # ===== NOTIFICATIONS =====
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    # ===== CONTEXT =====
    context = {
        'total': total,
        'completed': completed,
        'pending': pending,
        'near_due': near_due,
        'overdue': overdue,
        'alerts_count': alerts_count,

        'labels': labels,
        'total_data': total_data,
        'completed_data': completed_data,

        # notifications
        'notifications': notifications,
        'unread_count': unread_count,
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

    role = request.user.profile.role

    if role == 'student':
        assignments = Assignment.objects.filter(assigned_to=request.user)

    elif role == 'teacher':
        assignments = Assignment.objects.filter(created_by=request.user)

    else:
        assignments = Assignment.objects.all()

    total = assignments.count()

    today = timezone.now().date()
    days_since_sunday = today.weekday() + 1
    sunday = today - timedelta(days=days_since_sunday % 7)

    labels = []
    created_data = []
    completed_data = []

    for i in range(7):
        day = sunday + timedelta(days=i)
        labels.append(day.strftime("%a"))

        created_data.append(assignments.filter(deadline__date=day).count())
        completed_data.append(assignments.filter(completed=True, deadline__date=day).count())

    chart_data = zip(labels, created_data, completed_data)

    html_content = render_to_string('dashboard/report_template.html', {
        'assignments': assignments,
        'chart_data': chart_data,
        'user': request.user,
        'total': total
    })

    pdf = pdfkit.from_string(html_content, False)

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="weekly_report.pdf"'
    return response