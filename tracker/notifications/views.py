from django.shortcuts import render
from assignments.models import Assignment
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from django.shortcuts import get_object_or_404, redirect
from notifications.models import Notification


@login_required
def notifications(request):

    upcoming = Assignment.objects.filter(
        user=request.user,
        deadline__lt=timezone.now(),
        completed=False
    )

    return render(request, 'notifications/notifications.html', {'upcoming': upcoming})


@login_required
def mark_notification_read(request, id):

    notification = get_object_or_404(
        Notification,
        id=id,
        user=request.user
    )

    notification.is_read = True
    notification.save()

    return redirect('dashboard')