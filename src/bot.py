# -*- coding: utf-8 -*-
import telebot
import json
import requests
import time
from telebot import types
import urllib.parse
import pdb

token = "350061682:AAE6T7Gq_9Wj9jafF8HBXdSPYg0QRB2Xyi0"
bot = telebot.TeleBot(token)
subjects_url = "http://yatut.herokuapp.com/subjects.json"
global attendances_url
attendances_url = "http://yatut.herokuapp.com/subjects/%s/attendances.json"
def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content

@bot.message_handler(commands=["help"])
def handle_help(message):
	bot.send_message(message.chat.id, "Это бот для проверки посещаемости. Отправьте мне команду /attendance чтобы получить список доступных занятий")	

def get_json_from_url(url):
	content = get_url(url)
	sub_dic = json.loads(content)
	return sub_dic

@bot.message_handler(commands=["attendance"])
def get_subjects(message):
	sub_list = get_json_from_url(subjects_url)
	if len(sub_list) == 1:
		bot.send_message(message.chat.id, "Здесь только один предмет")	
		i = sub_list[0]['id']
		name = sub_list[0]['name']
		lst = {i:name}
	else:
		lst = {d['id']:d['name'] for d in sub_list}
	keyboard = types.InlineKeyboardMarkup()	
	keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=str(id)) for id, name in lst.items()])
	bot.send_message(message.chat.id, "Выбери предмет", reply_markup=keyboard)
	

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
	sub_list = get_json_from_url(subjects_url)
	lst = {d['id']:d['name'] for d in sub_list}
	global subject_id
	subject_id = c.data

	name = lst[int(c.data)]
	bot.send_message(
	chat_id=c.message.chat.id,
	text = "Вы выбрали %s" % name)
	keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
	button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
	keyboard.add(button_geo)
	bot.send_message(c.message.chat.id, "Теперь отправьте мне ваше местоположение", reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def handle_location(message):
	headers = {"Content-Type": "application/json"}
	try:
		subject_id
	except NameError:
		bot.send_message(message.chat.id, "Сперва выберите предмет. Для этого введите команду /subjects")
	else:
		att_url = attendances_url % subject_id
		payload = {"first_name": message.chat.first_name,"last_name": message.chat.last_name,"longitude": message.location.longitude,"latitude": message.location.latitude}
		r = requests.post(att_url, headers=headers, data = json.dumps(payload))

		if (r.status_code == 403):
			bot.send_message(message.chat.id, "Проверка местоположения неуспешна. Вы не в зоне радиуса. Попробуйте подойти ближе к зоне радиусе и заново пройдите проверку")		
		elif (r.status_code == 201):
			bot.send_message(message.chat.id, "Проверка местоположения успешна")

		
@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

if __name__ == "__main__":
     bot.polling(none_stop=True)

