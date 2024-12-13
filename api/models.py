from django.db import models
from members.models import Member

class TokenLog(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    token = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)

class RefreshToken(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    token = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()