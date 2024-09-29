from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.TextField(blank=True)
    following = models.TextField(blank=True)

class Post(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="poster")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    likeUser = models.TextField(blank=True)
    likeCount = models.PositiveIntegerField(default=0)
    
    def serialize(self):
        return {
            "user": self.user.username,
            "body": self.body,
            "timestamp": self.timestamp.strftime("%b %d %Y, %I:%M %p"),
        }
    def __str__(self):
        return f"Post ID: {self.id}"