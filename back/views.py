from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Gamer, InGameStatus, Targets
from django.utils.timezone import now
import random

import telebot
from telebot import types
import time
from datetime import timedelta, datetime

token = '1311687849:AAG-dFBYGETpeklPjJWmeWZqA0Lh42qbzNw'
bot = telebot.TeleBot(token)

main_url = 'https://bfceef340c22.ngrok.io/api/'

SERVER_IP = '80.240.25.179'
SERVER_PORT = '8443'

bot.remove_webhook()
time.sleep(1)
bot.set_webhook(url = main_url, allowed_updates=['message', 'callback_query'])
#bot.set_webhook(url = f'https://{SERVER_IP}:{SERVER_PORT}',certificate = open('YOURPUBLIC.pem') , allowed_updates=['message', 'edited_channel_post', 'callback_query','pre_checkout_query'])
print('set_webhook')

@api_view(['POST'])
def update_handler(request):
	data = request.data
	return Response(status = status.HTTP_200_OK)
	print(data)
	if('message' in data.keys()):
		user_mes = data['message']['text']
		user_id = data['message']['from']['id']
		last_time = check_user_last_time(user_id)
		print(last_time)
		if(last_time['ok'] and last_time['status']):
			if(last_time['user_status'] == 'waiting' or last_time['user_status'] == 'none'):
				if(user_mes == '/start'):
					ans = register_gamer(user_id)
					if(ans['ok']):
						reply_mes = 'Чтобы принять участие в игре нажмите "Участвовать"'
						keyboard = create_inline_keyboard([[['Участвовать','take_part']]])
					else:
						reply_mes = 'Вы уже участвуете в игре'
						keyboard = create_default_keyboard([[['Подтвердить смерть']],[['Напомнить цель']]], False)
					bot.send_message(user_id, reply_mes, reply_markup = keyboard)
					return Response(status = status.HTTP_200_OK)

				elif(last_time['is_admin'] and user_mes == '/start_game'):
					ans = start_game()
					if(ans['ok']):
						keyboard = create_default_keyboard([[['Подтвердить смерть']],[['Напомнить цель']]], False)
						for n in ans['nots']:
							bot.send_message(n[0],f'Ваша цель: {n[1]}', reply_markup = keyboard)
						reply_mes = 'Игра успешно начата'
						bot.send_message(user_id, reply_mes)
					else:
						bot.send_message(user_id, ans['error'])
					return Response(status = status.HTTP_200_OK)

				elif(last_time['is_admin'] and user_mes == '/stats'):
					ans = get_top()
					if(ans['ok']):
						reply_mes = '\n'.join(list(map(lambda ob:f'{ob[0]} - {ob[1]}',ans['top'])))
						bot.send_message(user_id, reply_mes)
					return Response(status = status.HTTP_200_OK)

				elif(last_time['user_game_status'] == 'in_game' and user_mes == 'Подтвердить смерть'):
					ans = become_dead(user_id)
					if(ans['ok'] and not ans['final']):
						reply_mes = 'Вы были убиты и ваша цель переходит к другому игроку'
						bot.send_message(user_id, reply_mes)
						bot.send_message(ans['nots'][0],f'Поздравляем!\nВаша новая цель: {ans["nots"][1]}')
					else:
						reply_mes = 'Игра была завершена'
						for n in ans['nots']:
							bor.send_message(n, reply_mes)
					return Response(status = status.HTTP_200_OK)

				elif(last_time['user_game_status'] == 'in_game' and user_mes == 'Напомнить цель'):
					ans = get_target(user_id)
					if(ans['ok']):
						reply_mes = f'Напоминание\nВаша цель:{ans["target"]}\nБаллы:{ans["result"]}'
						bot.send_message(user_id, reply_mes)
						return Response(status = status.HTTP_200_OK)

			elif(last_time['user_status'] == 'adding_fio'):
				ans = add_fio(user_id, user_mes)
				reply_mes = 'Игроки с некорректными данными будут удалены'
				bot.send_message(user_id, reply_mes)

	elif('callback_query' in data.keys()):
		user_mes = data['callback_query']['data']
		user_id = data['callback_query']['from']['id']
		message_id = data['callback_query']['message']['message_id']
		bot.delete_message(user_id, message_id)
		last_time = check_user_last_time(user_id)
		if(last_time['ok'] and last_time['status']):
			if(user_mes == 'take_part'):
				ans = take_part_game(user_id)
				if(ans['ok']):
					reply_mes = 'Введите Фамилию и Имя'
				else:
					reply_mes = ans['error']
				bot.send_message(user_id, reply_mes)
				return Response(status = status.HTTP_200_OK)

	return Response(status = status.HTTP_200_OK)

def get_top():
	users = Gamer.objects.filter(game_status = False)
	top = []
	for user in users:
		top.append([user.fio, Targets.objects.filter(killer = user, active = False, done = True).count()])
	sorted(top, reverse = True, key = lambda ob:ob[1])
	top = top[:10]
	return({'ok':True, 'top':top})

def get_target(user_id):
	user = Gamer.objects.filter(tg_id = user_id).first()
	target = Targets.objects.filter(killer = user, active = True)
	result = Targets.objects.filter(killer = user, active = False, done = True).count()
	return({'ok':True, 'target':target, 'result':result})

def become_dead(user_id):
	user = Gamer.objects.filter(tg_id = user_id).first()
	user.game_status = 'dead'
	user.save()
	you_target = Targets.objects.filter(target = user, active = True).first()
	you_target.active = False
	you_target.done = True
	you_target.save()
	you_killer = Targets.objects.filter(killer = user, active = True).first()
	you_killer.active = False
	you_killer.save()
	if(Targets.objects.filter(active = True).count() == 2):
		return({'ok':True, 'final':True, 'nots':list(map(lambda ob:ob.tg_id, Gamer.objects.all()))})	
	Targets.create(target = you_killer.target, killer = you_target.killer)
	return({'ok':True, 'final':False, 'nots':[you_target.killer.tg_id,you_killer.target.fio]})

def start_game():
	gm = InGameStatus.objects.all().first()
	if(not gm.is_game):
		# gm.is_game = True
		# gm.save()
		gamers = list(Gamer.objects.filter(game_status = 'in_game', user = None))
		random.shuffle(gamers)
		notifications = []
		for i in range(len(gamers)):
			Targets.objects.create(killer = gamers[i], target = gamers[(i+1)%len(gamers)])
			notifications.append([gamers[i].tg_id, gamers[(i+1)%len(gamers)].fio])
		return({'ok':True,'nots':notifications})
	return({'ok':False,'error':'Игра уже идет'})

def add_fio(user_id, user_mes):
	user = Gamer.objects.filter(tg_id = user_id).first()
	user.status = 'waiting'
	user.fio = user_mes
	user.game_status = 'in_game'
	user.save()
	return({'ok':True})

def take_part_game(user_id):
	gm = InGameStatus.objects.all().first()
	if(not gm.is_game):
		user = Gamer.objects.filter(tg_id = user_id)
		if(user.exists()):
			user = user.first()
			if(user.game_status == None):
				user.status = 'adding_fio'
				user.save()
				return({'ok':True})
			return({'ok':False,'error':'Вы уже участвуете в игре'})
		return({'ok':False,'error':'Пользователь не найден'})
	return({'ok':False,'error':'Игра уже идет'})

def register_gamer(user_id):
	user = Gamer.objects.filter(tg_id = user_id)
	if(not user.exists()):
		Gamer.objects.create(tg_id = user_id, status = 'waiting')
		return({'ok':True})
	user = user.first()
	if(user.game_status == None):
		return({'ok':True})
	return{'ok':False}

def check_user_last_time(user_id):
	user = Gamer.objects.filter(tg_id = user_id)
	is_admin = False
	if(user.exists()):
		user = user.first()
		if(user.user != None):
			if(user.user.is_staff):
				is_admin = True
		last = now()
		if(user.last_time != None):
			time_status = (user.last_time + timedelta(seconds=1))<last
		else:
			time_status = True
		if(time_status == True):
			user.last_time = last
			user.save()
		return({'ok':True,'status':time_status, 'user_status':user.status, 'user_game_status':user.game_status, 'is_admin':is_admin})
	return({'ok':True,'status':True, 'user_status':'none', 'user_game_status':'none', 'is_admin':is_admin})

def create_inline_keyboard(mas):
	markup = types.InlineKeyboardMarkup()
	for row in mas:
		new_row = []
		for btn in row:
			new_row.append(types.InlineKeyboardButton(text = btn[0], callback_data = btn[1]))
		markup.add(*new_row)
	return(markup)

def create_default_keyboard(mas, one_time):
	markup = types.ReplyKeyboardMarkup(one_time_keyboard = one_time, resize_keyboard = True)
	for row in mas:
		new_row = []
		for btn in row:
			new_row.append(types.KeyboardButton(btn))
		markup.row(*new_row)
	return markup
