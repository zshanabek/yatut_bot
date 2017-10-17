# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json
import requests
import time
import urllib.parse
import pdb
import datetime
from tzwhere import tzwhere
import pytz
import logging
import emoji
logger = telebot.logger


token = "350061682:AAE6T7Gq_9Wj9jafF8HBXdSPYg0QRB2Xyi0"
bot = telebot.TeleBot(token)

# telebot.logger.setLevel(logging.INFO) 
# telebot.logger.setLevel(logging.DEBUG)
global attendances_url
attendances_url = "http://yatut.herokuapp.com/subjects/%s/attendances.json"
events_list = []
events_objects = []
@bot.message_handler(commands=["start"])
def handle_start(message):
	bot.send_message(message.chat.id, "Это бот для проверки посещаемости. Отправьте команду /attendance чтобы получить список доступных занятий")	
	buttons = ['{} Список событий'.format(emoji.emojize(':bell:')),
               '{} Веб-сайт'.format(emoji.emojize(':computer:', use_aliases=True)),
               '{} FAQ'.format(emoji.emojize(':question:', use_aliases=True))
              ]
	bot.send_message(message.chat.id, "Выберите из списка одну из услуг", reply_markup=create_keyboard( False, buttons, 1))

@bot.message_handler(content_types=['text'])
def reply_to(message):
	if message.text == '{} Список событий'.format(emoji.emojize(':bell:')):
		global events_list		
		events_list = get_events()
		text = 'Выберите событие'
		bot.send_message(message.chat.id, text, reply_markup=create_keyboard(False, events_list+ ['{} Главная'.format(emoji.emojize(':house:'))], 2))
	elif message.text == '{} Главная'.format(emoji.emojize(':house:')):
		buttons = ['{} Список событий'.format(emoji.emojize(':bell:')),
               '{} Веб-сайт'.format(emoji.emojize(':computer:', use_aliases=True)),
               '{} FAQ'.format(emoji.emojize(':question:', use_aliases=True))
              ]
		bot.send_message(message.chat.id, "Выберите из списка одну из услуг", reply_markup=create_keyboard(False, buttons, 1))

	elif message.text in events_list:
		for e in events_objects:
			if e["name"] == message.text:
				detailInfo=["Проверить посещаемость"]
				text = "Название события: "+ e["name"] + "\n" + "Адрес: " +e["address"] +"\n" + "Радиус: " +str(e["radius"])
				bot.send_message(message.chat.id, text, reply_markup=create_keyboard(False, detailInfo+['{} Главная'.format(emoji.emojize(':house:'))], 1))
				bot.send_venue(message.chat.id, latitude=e["latitude"], longitude=e["longitude"], title=e["name"], address=e["address"])

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
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
	att_url = attendances_url % subject_id
	lat = message.location.latitude
	lng = message.location.longitude
	zone = tzwhere.tzwhere()
	timezone_str = zone.tzNameAt(lat, lng)
	timezone = pytz.timezone(timezone_str)
	time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	payload = {"first_name": message.chat.first_name,"last_name": message.chat.last_name,
	"longitude": lng,"latitude": lat,
	"created_at": time}
	r = requests.post(att_url, headers=headers, data = json.dumps(payload))

	if (r.status_code == 403):
		bot.send_message(message.chat.id, "Ваши координаты: {0}, {1}. Проверка местоположения неуспешна. Вы не в зоне радиуса. Попробуйте подойти к центру аудитории и заново пройти проверку.".format(lat,lng))
	elif (r.status_code == 201):
		bot.send_message(message.chat.id, "Ваши координаты: {0}, {1}. Проверка местоположения успешно пройдена.".format(lat,lng))


def create_keyboard(getLocation, words=None, width=None):
	keyboard = types.ReplyKeyboardMarkup(row_width=width, resize_keyboard = True)
	for word in words:
		keyboard.add(types.KeyboardButton(text=word, request_location=getLocation))
	return keyboard


def get_events():
	events_url = "http://yatut.herokuapp.com/subjects.json"
	response = requests.get(url=events_url)
	global events_objects 
	events_objects = response.json()

	for d in events_objects:
		events_list.append(d['name'])
	return events_list


if __name__ == "__main__":
     bot.polling(none_stop=True)

