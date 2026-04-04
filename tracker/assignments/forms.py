from django import forms
from .models import Assignment
from .models import Project

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['subject', 'title', 'description', 'deadline']

        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': '📚 Enter the subject name',
                'style': 'background-color: #e6f0ff; border: 1px solid #3399ff;'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control mb-3',
                'placeholder': '📝 Enter the title',
                'style': 'background-color: #e6f0ff; border: 1px solid #3399ff;'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control mb-3',
                'placeholder': '✏️ Enter the description',
                'rows': 4,
                'style': 'background-color: #e6f0ff; border: 1px solid #3399ff;'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control mb-3',
                'type': 'date',
                'style': 'background-color: #e6f0ff; border: 1px solid #3399ff;'
            }),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'github_url', 'progress']