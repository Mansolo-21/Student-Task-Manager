from django.db import models
from django.contrib.auth.models import User

class Assignment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    github_url = models.URLField()
    progress = models.IntegerField(default=0)  # 0 - 100
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name