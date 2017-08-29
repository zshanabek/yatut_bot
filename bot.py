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
attendances_url = "http://yatut.herokuapp.com/subjects/1/attendances.json"

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    sub_dic = json.loads(content)
    return sub_dic


@bot.message_handler(commands=["subjects"])
def get_subjects(message):
	
	sub_list = get_json_from_url(subjects_url)

	lst = {d['id']:d['name'] for d in sub_list}
	# print(lst)
	# # for i in sub_dict:
	# for key, value in lst.items():
	# 	print(str(key) + " " +value)

	# pdb.set_trace()
	keyboard = types.InlineKeyboardMarkup()	
	keyboard.add(*[types.InlineKeyboardButton(text=name, callback_data=str(id)) for id, name in lst.items()])
	bot.send_message(message.chat.id, "Выбери предмет", reply_markup=keyboard)
	

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
	print(c.data)
	sub_list = get_json_from_url(subjects_url)
	lst = {d['id']:d['name'] for d in sub_list}
	name = lst[int(c.data)]
	bot.edit_message_text(
	chat_id=c.message.chat.id,
	message_id = c.message.message_id,
	text = "You chose %s" % name,
	parse_mode="Markdown")

@bot.message_handler(commands=["location"])
def geophone(message):
	keyboard = types.ReplyKeyboardMarkup()
	button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
	keyboard.add(button_geo)
	bot.send_message(message.chat.id, "Поделись местоположением, жалкий человечишка!", reply_markup=keyboard)

@bot.message_handler(content_types=["location"])
def handle_location(message):
	headers = {"Content-Type": "application/json"}
	payload = {"first_name": message.chat.first_name,"last_name": message.chat.last_name,"longitude": message.location.longitude,"latitude": message.location.latitude}
	r = requests.post(attendances_url, headers=headers, data = json.dumps(payload))
	bot.send_message(message.chat.id, message.location.latitude)
	print(r.json())

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

if __name__ == "__main__":
     bot.polling(none_stop=True)

