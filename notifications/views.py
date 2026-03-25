from django.shortcuts import render
from assignments.models import Assignment
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required
def notifications(request):

    upcoming = Assignment.objects.filter(
        user=request.user,
        deadline__lt=timezone.now(),
        completed=False
    )

    return render(request, 'notifications/notifications.html', {'upcoming': upcoming})