from django.db import models
from django.contrib.auth.models import User

class Gamer(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE, null = True, blank = True)
	tg_id = models.CharField(max_length = 50)
	status = models.CharField(max_length = 50)
	game_status = models.CharField(max_length = 50, null = True, blank = True)
	last_time = models.DateTimeField(null = True, blank = True)
	fio = models.TextField(null = True, blank = True)
	
	def __str__(self):
		return(f'{self.tg_id} - {self.fio} - {self.game_status}')

class Targets(models.Model):
	killer = models.ForeignKey(Gamer, on_delete = models.CASCADE, related_name = 'gamer_killer')
	target = models.ForeignKey(Gamer, on_delete = models.CASCADE, related_name = 'gamer_target')
	done = models.BooleanField(default = False)
	active = models.BooleanField(default = True)

	def __str__(self):
		return(f'{self.killer} - {self.target} - {self.done} - {self.active}')

class InGameStatus(models.Model):
	is_game = models.BooleanField(default = False)