from django.contrib import admin
from . import models
# Register your models here.
class Gamer_model(admin.ModelAdmin):
	list_display=('tg_id', 'status', 'game_status', 'fio')
	list_filter = ('status', 'game_status')
	search_fields = ('fio', 'tg_id')

class Target_model(admin.ModelAdmin):
	def get_killer(self, obj):
		return(obj.killer.fio)
	def get_target(self, obj):
		return(obj.target.fio)
	list_display=('get_killer', 'get_target', 'done', 'active')
	list_filter = ('done', 'active')
	search_fields = ('killer__fio', 'target__fio')

admin.site.register(models.Gamer, Gamer_model)
admin.site.register(models.InGameStatus)
admin.site.register(models.Targets, Target_model)
