from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class UserData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    swiss_data = models.JSONField(default=dict)
    knockout_data = models.JSONField(default=dict)
    
    def __str__(self):
        return str(self.user)
    

class VideoPost(models.Model):
    link = models.CharField(max_length=100)
    
    def __str__(self):
        return self.link
    
