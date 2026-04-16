from django.contrib import admin
from .models import Profile, Assignment, Project

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):

    list_display = ('title', 'subject', 'deadline', 'completed', 'created_at')
    list_filter = ('subject', 'completed')
    search_fields = ('title', 'subject')


admin.site.register(Profile)

admin.site.register(Project)