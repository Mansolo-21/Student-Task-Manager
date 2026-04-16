from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

    def __str__(self):
        return f"{self.user.username} - {self.role}"
    

class Assignment(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    assigned_to = models.ForeignKey(
    User,
    on_delete=models.CASCADE,
    related_name='assigned_assignments',
    null=True,   # ✅ TEMPORARY FIX
    blank=True   # ✅ TEMPORARY FIX
)

    subject = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    completed = models.BooleanField(default=False)

    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    file = models.FileField(upload_to='assignments/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['deadline']

    @property
    def is_overdue(self):
        return self.deadline < timezone.now() and not self.completed

    @property
    def time_remaining(self):
        if self.deadline > timezone.now():
            return self.deadline - timezone.now()
        return None


class Project(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    github_url = models.URLField()

    # Progress (0 - 100)
    progress = models.IntegerField(default=0)

    # ✅ Optional priority
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='MEDIUM'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # 🔥 PRO FEATURE 4: Auto ordering
    class Meta:
        ordering = ['-created_at']

    # 🔥 PRO FEATURE 5: Clamp progress (VERY IMPORTANT)
    def save(self, *args, **kwargs):
        if self.progress > 100:
            self.progress = 100
        elif self.progress < 0:
            self.progress = 0

        super().save(*args, **kwargs)

    # 🔥 PRO FEATURE 6: Completion check
    @property
    def is_completed(self):
        return self.progress == 100
    

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)


    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()