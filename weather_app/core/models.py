from django.db import models

# Create your models here.

class City(models.Model):
    name = models.CharField(max_length = 255)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name
