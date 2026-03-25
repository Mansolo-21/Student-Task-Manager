from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignment_list, name='assignment_list'),
    path('add/', views.add_assignment, name='add_assignment'),
    path('complete/<int:id>/', views.complete_assignment, name='complete_assignment'),
    path('assignment/',views.add,name='assignment'),
    path('assignment/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),  # for detail page
    path('completed/', views.completed_assignments, name='completed_assignments'),
    path('assignment/update/<int:pk>/', views.update_assignment, name='update_assignment'),
    path('project_list', views.project_list, name='project_list'),
    path('create/', views.create_project, name='create_project'),
    path('projects/edit/<int:pk>/', views.edit_project, name='edit_project'),

]