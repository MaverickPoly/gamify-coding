from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    xp = models.IntegerField(default=0)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    

class Project(models.Model):
    DIFFICULTY_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    )
    FIELD_CHOICES = (
        ('backend', 'Backend'),
        ('game_dev', 'Game Development'),
        ('mobile_app', 'Mobile App Development'),
        ('desktop_app', 'Desktop App Development'),
        ('frontend', 'Frontend'),
        ('misc', 'Miscellaneous'),
        ('starter', 'Starter'),
        ('ai_ml', 'AI & Machine Learning'),
    )

    title = models.CharField(max_length=300)
    description = models.TextField()
    programming_language = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    field = models.CharField(max_length=20, choices=FIELD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class CompletedProject(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="completed_projects")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    completion_date = models.DateTimeField(auto_now_add=True)
    github_link = models.URLField(blank=True)

    class Meta:
        unique_together = ('user', 'project')  # Prevent duplicate completions

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Award XP based on difficulty
        xp_map = {'Beginner': 10, 'Intermediate': 30, 'Advanced': 50}
        self.user.profile.xp += xp_map[self.project.difficulty]
        self.user.profile.save()

    def __str__(self):
        return f"{self.user.username} completed {self.project.title}"
