from django.contrib import admin
from . import models
# Register your models here.

admin.site.register(models.Gamer)
admin.site.register(models.InGameStatus)
admin.site.register(models.Targets)