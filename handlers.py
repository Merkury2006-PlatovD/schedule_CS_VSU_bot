from datetime import datetime

import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from telebot import TeleBot
from parser import ScheduleParser
from utils import get_subgroup_keyboard, get_group_keyboard, get_course_keyboard, get_persistent_keyboard
from db_controller import DBController


def register_handlers(bot: TeleBot, sch_parser: ScheduleParser):
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

    def set_bot_commands_menu():
        bot.set_my_commands([
            telebot.types.BotCommand("start", "Начать работу с ботом"),
            telebot.types.BotCommand("help", "Получить помощь"),
            telebot.types.BotCommand("info", "Узнать информацию о себе"),
            telebot.types.BotCommand("updateinfo", "Поменять информацию о себе")
        ])

    @bot.message_handler(commands=['start'])
    def handle_start(message):
        """
        Слушает команду "/start" и выполняет действия в зависимости от результата user_exists(user_id). Начинает работу всего бота.

        Args:
            message: экземпляр telebot.types.Message.
        """
        set_bot_commands_menu()
        user_id = message.from_user.id

        if not DBController.user_exists(user_id):
            DBController.add_user(user_id)
            bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())
        else:
            bot.send_message(user_id, "Ты уже зарегистрирован!")
            bot.send_message(user_id, "На какой день тебе нужно расписание?", reply_markup=get_persistent_keyboard())

    @bot.message_handler(commands=['updateinfo'])
    def handle_profile_update(message):
        """
        Слушает команду "/updateinfo" и регистрирует/изменяет данные о пользователе в БД.

        Args:
            message: экземпляр telebot.types.Message.
        """
        user_id = message.from_user.id
        if not DBController.user_exists(user_id):
            DBController.add_user(user_id)
        bot.send_message(user_id, "Привет! Выбери свой курс:", reply_markup=get_course_keyboard())

    @bot.message_handler(commands=['help'])
    def handle_help(message):
        """
        Слушает команду "/help" и выводит пользователю справочную информацию.

        Args:
            message: экземпляр telebot.types.Message.
        """
        bot.send_message(message.from_user.id, "Привет! Я помогу тебе с расписанием: \n"
                                               "•  Напиши команду /start, чтобы я узнал информацию о тебе и твоем расписании\n"
                                               "•  Напиши команду /updateinfo, чтобы изменить информацию о тебе\n"
                                               "•  Напиши команду /info, чтобы узнать краткую информацию о тебе.")

    @bot.message_handler(commands=['info'])
    def handle_help(message):
        user_id = message.from_user.id
        course, group, subgroup = DBController.get_user_data(user_id)
        bot.send_message(message.from_user.id, "Информация о тебе: \n"
                                               f"Твой курс: {course}\n"
                                               f"Твоя группа: {group}\n"
                                               f"Твоя подгруппа: {subgroup}")

    @bot.message_handler(
        func=lambda message: message.text not in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница",
                                                  "📅 Суббота"])
    def handle_error_message(message):
        user_id = message.from_user.id
        bot.send_message(user_id, "Привет! Напиши /start для запуска бота или /help для более подробной информации")

    @bot.message_handler(
        func=lambda message: message.text in ["📅 Понедельник", "📅 Вторник", "📅 Среда", "📅 Четверг", "📅 Пятница",
                                              "📅 Суббота"])
    def handle_schedule_request(message):
        days_map = {"📅 Понедельник": 0, "📅 Вторник": 1, "📅 Среда": 2, "📅 Четверг": 3, "📅 Пятница": 4, "📅 Суббота": 5}
        user_id = message.from_user.id
        day = days_map[message.text]
        course, group, subgroup = DBController.get_user_data(user_id)
        schedule = sch_parser.get_lessons_on_day(sch_parser.find_required_col(course, group, subgroup),
                                                 day, week)
        out_data_formated = f"📅 *Расписание занятий на {message.text.split(" ")[-1]}:*\n\n"

        for key, val in schedule.items():
            if val is None or val.strip() == "":
                val = "— Нет пары —"

            out_data_formated += f"🕒 *{key}*\n📖 {val}\n\n"

        bot.send_message(user_id, out_data_formated, parse_mode="Markdown")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("course_"))
    def handle_course(call):
        user_id = call.from_user.id
        course = int(call.data.split("_")[1])

        DBController.update_user(user_id, "course", course)
        keyboard = get_group_keyboard()
        bot.send_message(user_id, "Теперь выбери свою группу:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("group_"))
    def handle_group(call):
        user_id = call.from_user.id
        group = int(call.data.split("_")[1])

        DBController.update_user(user_id, "group_num", group)
        keyboard = get_subgroup_keyboard()
        bot.send_message(user_id, "Теперь выбери свою подгруппу:", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("subgroup_"))
    def handle_subgroup(call):
        user_id = call.from_user.id
        subgroup = int(call.data.split("_")[1])

        DBController.update_user(user_id, "subgroup", subgroup)
        bot.send_message(user_id, "Отлично! Данные сохранены.")
        bot.send_message(user_id, "На какой день тебе нужно расписание?", reply_markup=get_persistent_keyboard())
