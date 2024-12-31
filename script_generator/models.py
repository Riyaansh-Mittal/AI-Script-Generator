from django.db import models
from django.contrib.auth.models import User
from datetime import datetime


class BlogPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    generated_content = models.TextField()
    external_link = models.URLField(null=True, blank=True)  # URL for external links
    external_link_name = models.CharField(max_length=255, null=True, blank=True)  # Name for the link
    file_name = models.CharField(max_length=255, null=True, blank=True)  # Name for the file
    created_at = models.DateTimeField(default=datetime.now) # Automatically sets the current timestamp on creation

    def __str__(self):
        return self.title
