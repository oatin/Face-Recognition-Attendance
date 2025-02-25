from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ServiceConfig(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='configs')
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('service', 'key')

    def __str__(self):
        return f"{self.service.name} - {self.key}: {self.value}"
