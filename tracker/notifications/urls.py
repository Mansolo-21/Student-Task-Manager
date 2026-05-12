from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications, name='notifications'),
    path('notification/read/<int:id>/', views.mark_notification_read, name='mark_notification_read'),

]