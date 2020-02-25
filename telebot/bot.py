import requests
import telebot
from telebot import apihelper
from datetime import datetime
from bs4 import BeautifulSoup
from typing import List, Tuple

access_token = '1004359824:AAEgBBGWqb0y2eDqXyHONN6Lcf8b35Vb6Zk'
bot = telebot.TeleBot(access_token)


day_b = {'/monday': 0,
		 '/tuesday': 1,
		 '/wednesday': 2,
		 '/thursday': 3,
		 '/friday': 4,
		 '/saturday': 5,
		 '/sunday': 6}

day_rus = {0 : 'Понедельник',
		   1 : 'Вторник',
		   2 : 'Среда',
		   3 : 'Четверг',
		   4 : 'Пятница',
		   5 : 'Суббота',
		   6 : 'Воскресенье'}

day_c = {0: '1day',
		 1: '2day',
		 2: '3day',
		 3: '4day',
		 4: '5day',
		 5: '6day',
		 6: '7day'}
now = datetime.today()


def get_page(group: str) -> str:
	week = datetime.date(now).isocalendar()[1]
	if week % 2 == 0:
		week = '2'
	else:
		week = '1'
	url = '{domain}/{group}/{week}/raspisanie_zanyatiy_{group}.htm'.format(
	domain='http://www.ifmo.ru/ru/schedule/0',
	week=week,
	group=group
	)
	response = requests.get(url)
	web_page = response.text
	return web_page


def parse_schedule_for_a_day(web_page, day_p):
	soup = BeautifulSoup(web_page, "html5lib")

	# Получаем таблицу с расписанием на конкретный день
	schedule_table = soup.find("table", attrs={"id": day_p})

	# Исключение, если в этот день нет пар
	if not schedule_table:
		return

	# Время проведения занятий
	times_list = schedule_table.find_all("td", attrs={"class": "time"})
	times_list = [time.span.text for time in times_list]

	# Место проведения занятий
	locations_list = schedule_table.find_all("td", attrs={"class": "room"})
	locations_list = [room.span.text for room in locations_list]

	# Номер аудитории
	aud_list = schedule_table.find_all("td", attrs={"class": "room"})
	aud_list = [aud.dd.text for aud in aud_list]

	# Название дисциплин и имена преподавателей
	lessons_list = schedule_table.find_all("td", attrs={"class": "lesson"})
	lessons_list = [lesson.text.split('\n\n') for lesson in lessons_list]
	lessons_list = [', '.join([info for info in lesson_info if info]) for lesson_info in lessons_list]

	return times_list, locations_list, lessons_list, aud_list


@bot.message_handler(commands=['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'])
def get_schedule(message):
	""" Получить расписание на указанный день """
	try:
		day, group = message.text.split()
	except:
		bot.send_message(message.chat.id, 'Это что такое? Напишите пожалуйста нормально, я вас не понимаю')
		return None
	day_print = day_b.get(day)
	day_p = day_c.get(day_print)
	web_page = get_page(group)
	schedule_for_day = parse_schedule_for_a_day(web_page, day_p)
	if not schedule_for_day:
		bot.send_message(message.chat.id, 'Всё в порядке, пар нет.\nМожно отдыхать')
		return None
	times_lst, locations_lst, lessons_lst, aud_lst = schedule_for_day
	resp = ''
	day_rus_print = day_rus.get(day_print)
	resp += '📖📖📖 <b>{}</b> \n'.format(day_rus_print)
	for time, location, lesson, aud in zip(times_lst, locations_lst, lessons_lst, aud_lst):
		resp += '\n\n <b>{}</b>, {} <i>{}</i> {} \n\n'.format(time, location, lesson, aud)
	bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['near'])
def get_near_lesson(message):
	""" Получить ближайшее занятие """
	try:
		_, group = message.text.split()
	except:
		bot.send_message(message.chat.id, 'Это что такое? Напишите пожалуйста нормально, я вас не понимаю')
	return None
	now = datetime.now()
	day = datetime.weekday(now)
	day_p = day_c.get(day)
	time_p = tuple([now.hour, now.minute])
	count_minute_now = (time_p[0] * 60) + time_p[1]
	web_page = get_page(group)
	schedule_for_day = parse_schedule_for_a_day(web_page, day_p)
	for i in  day_c:
		if not schedule_for_day:
			day += 1
			day_p = day_c.get(day)
			time_p = tuple([now.hour, now.minute])
			count_minute_now = (time_p[0] * 60) + time_p[1]
			web_page = get_page(group)
			schedule_for_day = parse_schedule_for_a_day(web_page, day_p)
		return 
	times_lst, locations_lst, lessons_lst, aud_lst = schedule_for_day
	for i in range(len(times_lst)):
		time_s = times_lst[i].split('-')
		time_s = datetime.strptime(time_s[0], '%H:%M')
		time_s = tuple([time_s.hour, time_s.minute])
		count_minute_s = (time_s[0] * 60) + time_s[1]
	if count_minute_now < count_minute_s:
		resp = '⏰ Следущая пара:\n \n\n <b>{}</b>, {} <i>{}</i> {} \n\n'.format(times_lst[i], locations_lst[i],
		lessons_lst[i], aud_lst[i])
	return bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['tommorow'])
def get_tommorow(message):
	""" Получить расписание на следующий день """
	try:
		day, group = message.text.split()
	except:
		bot.send_message(message.chat.id, 'Это что такое? Напишите пожалуйста нормально, я вас не понимаю')
		return None
	now = datetime.today()
	now = now.weekday()
	lom = (float(now) + 1) % 7
	day_p = day_c.get(lom)
	web_page = get_page(group)
	schedule_for_day = parse_schedule_for_a_day(web_page, day_p)
	if not schedule_for_day:
		bot.send_message(message.chat.id, 'Всё в порядке, пар нет.\nМожно отдыхать')
		return None
	times_lst, locations_lst, lessons_lst, aud_lst = schedule_for_day
	resp = ''
	day_rus_print = day_rus.get(lom)
	resp += '📖📖📖 <b>{}</b> \n'.format(day_rus_print)
	for time, location, lesson, aud in zip(times_lst, locations_lst, lessons_lst, aud_lst):
		resp += '\n\n <b>{}</b>, {} <i>{}</i> {} \n\n'.format(time, location, lesson, aud)
	bot.send_message(message.chat.id, resp, parse_mode='HTML')


@bot.message_handler(commands=['all'])
def get_all_schedule(message):
	""" Получить расписание на всю неделю для указанной группы """
	try:
		day, group = message.text.split()
	except:
		bot.send_message(message.chat.id, 'Это что такое? Напишите пожалуйста нормально, я вас не понимаю')
		return None
	for lom in day_b.values():
		day_p = day_c.get(lom)
		web_page = get_page(group)
		schedule_for_day = parse_schedule_for_a_day(web_page, day_p)
		if not schedule_for_day:
			bot.send_message(message.chat.id, 'Всё в порядке, пар нет.\nМожно отдыхать')
			return None
		times_lst, locations_lst, lessons_lst, aud_lst = schedule_for_day
		resp = ''
		day_rus_print = day_rus.get(lom)
		resp += '📖📖📖 <b>{}</b> \n'.format(day_rus_print)
		for time, location, lesson, aud in zip(times_lst, locations_lst, lessons_lst, aud_lst):
			resp += '\n\n <b>{}</b>, {} <i>{}</i> {} \n\n'.format(time, location, lesson, aud)
		bot.send_message(message.chat.id, resp, parse_mode='HTML')


if __name__ == '__main__':
	bot.polling(none_stop=True)

