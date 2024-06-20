from django.db import models

# Create your models here.
class upload_video(models.Model):
    title=models.CharField(max_length=100)
    video=models.FileField(upload_to='upload/')
    subfile=models.FileField(blank=True)
    
    def __str__(self):
        return self.title