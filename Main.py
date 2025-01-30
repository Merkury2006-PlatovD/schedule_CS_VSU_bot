import os
import sqlite3
import time

from apscheduler.schedulers.background import BackgroundScheduler
from telebot import types
import telebot
from datetime import datetime
from parser import ScheduleParser

bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

conn = sqlite3.connect('database/bot_data.sql', check_same_thread=False)
cursor = conn.cursor()
sch_parser = ScheduleParser('schedule.xlsx')

# Создание таблицы
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    course INTEGER,
    group_num INTEGER,
    subgroup INTEGER
);
""")

# Сохранение изменений и закрытие соединения
conn.commit()


def user_exists(user_id):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id=?)", (user_id,))
    return cursor.fetchone()[0]


def add_user(user_id):
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()


def update_user(user_id, column, value):
    cursor.execute(f"UPDATE users SET {column} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()


def get_user_data(user_id):
    cursor.execute("SELECT course, group_num, subgroup FROM users WHERE user_id = ?", (user_id,))
    return cursor.fetchone()


# Запуск бота
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    if not user_exists(user_id):
        add_user(user_id)
        bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
    else:
        bot.send_message(user_id, "Ты уже зарегистрирован!")
        bot.send_message(user_id, "На какой день тебе нужно расписание?", reply_markup=get_persistent_keyboard())


@bot.message_handler(commands=['updateinfo'])
def handle_profile_update(message):
    user_id = message.from_user.id
    if not user_exists(user_id):
        add_user(user_id)
    bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())

@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(message.from_user.id, "Привет! Я помогу тебе с расписанием: \n"
                                           "•  Напиши команду /start, чтобы я узнал информацию о тебе и твоем расписании\n"
                                           "•  Напиши команду /updateinfo, чтобы изменить информацию о тебе\n"
                                           "•  Напиши команду /info, чтобы узнать краткую информацию о тебе.")

@bot.message_handler(commands=['info'])
def handle_help(message):
    user_id = message.from_user.id
    course, group, subgroup = get_user_data(user_id)
    bot.send_message(message.from_user.id, "Информация о тебе: \n"
                                            f"Твой курс: {course}\n"
                                            f"Твоя группа: {group}\n"
                                            f"Твоя подгруппа: {subgroup}")

@bot.message_handler(func=lambda message: message.text not in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница", "📅 Суббота"])
def handle_error_message(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Привет! Напиши /start для запуска бота или /help для более подробной информации")


@bot.message_handler(func=lambda message: message.text in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница", "📅 Суббота"])
def handle_schedule_request(message):
    days_map = {"📅 Понедельник": 0, "📅 Вторник": 1, "📅 Среда": 2, "📅 Четверг": 3, "📅 Пятница": 4, "📅 Суббота": 5}
    user_id = message.from_user.id
    day = days_map[message.text]
    course, group, subgroup = get_user_data(user_id)
    schedule = sch_parser.get_lessons_on_day(sch_parser.find_required_col(course, group, subgroup),
                                             day, week)
    out_data_formated = "📅 *Расписание занятий:*\n\n"

    for key, val in schedule.items():
        if val is None or val.strip() == "":
            val = "— Нет пары —"

        out_data_formated += f"🕒 *{key}*\n📖 {val}\n\n"

    bot.send_message(user_id, out_data_formated, parse_mode="Markdown")


@bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
def handle_course(call):
    user_id = call.from_user.id
    course = int(call.data.split("_")[1])

    update_user(user_id, "course", course)
    keyboard = get_group_keyboard()
    bot.send_message(user_id, "Теперь выбери свою группу:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
def handle_group(call):
    user_id = call.from_user.id
    group = int(call.data.split("_")[1])

    update_user(user_id, "group_num", group)
    keyboard = get_subgroup_keyboard()
    bot.send_message(user_id, "Теперь выбери свою подгруппу:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("subgroup_"))
def handle_subgroup(call):
    user_id = call.from_user.id
    subgroup = int(call.data.split("_")[1])

    update_user(user_id, "subgroup", subgroup)
    bot.send_message(user_id, "Отлично! Данные сохранены.")
    bot.send_message(user_id, "На какой день тебе нужно расписание?", reply_markup=get_persistent_keyboard())


def get_persistent_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("📅 Понедельник"),
        types.KeyboardButton("📅 Вторник"),
        types.KeyboardButton("📅 Среда"),
        types.KeyboardButton("📅 Четверг"),
        types.KeyboardButton("📅 Пятница"),
        types.KeyboardButton("📅 Суббота")
    )
    return keyboard


def get_course_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for i in range(1, 5):
        keyboard.add(types.InlineKeyboardButton(text=str(i), callback_data=f"course_{i}"))
    return keyboard


def get_group_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    for i in range(1, 18):
        keyboard.add(types.InlineKeyboardButton(text=str(i), callback_data=f"group_{i}"))
    return keyboard


def get_subgroup_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text="1", callback_data="subgroup_1"))
    keyboard.add(types.InlineKeyboardButton(text="2", callback_data="subgroup_2"))
    return keyboard


def week_update():
    global week
    if week == 0:
        week = 1
    else:
        week = 0
    print(f"Обновлена неделя на {week}", datetime.now())


week = 0
scheduler = BackgroundScheduler()
scheduler.add_job(week_update, 'cron', day_of_week='sat', hour=18, minute=0)
scheduler.start()


def main():
    while True:
        try:
            print("Бот запущен")
            bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
