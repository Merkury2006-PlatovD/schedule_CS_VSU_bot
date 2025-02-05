import os
import time

import telebot

import config
from db_controller import DBController
from handlers import register_handlers
from parser.excell_converter import ScheduleParser
from updaters import start_week_updating, start_users_monitoring

# токен бота
bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))

# подключение бд

DBController.start_db_control(config.db_path)
# создание парсера и подключение хэндлеров к боту
sch_parser = ScheduleParser('src/parser/schedule.xlsx')
register_handlers(bot, sch_parser)

# старт обновлений состояний переменных из config
start_week_updating()
start_users_monitoring()


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
