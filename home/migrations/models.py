from django.db import models

class IoTInput(models.Model):
    temperature = models.FloatField()
    pH = models.FloatField()
    conductivity = models.FloatField()
    dissolved_oxygen = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Data Entry at {self.created_at}"