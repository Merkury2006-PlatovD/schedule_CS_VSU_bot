import os
import time

import telebot

from db_controller import DBController
from handlers import register_handlers
from parser.excell_converter import ScheduleParser
from week_updater import start_week_updating

# токен бота
bot = telebot.TeleBot(token=os.getenv("BOT_TOKEN"))
# создание парсера
sch_parser = ScheduleParser('src/parser/schedule.xlsx')
DBController.start_db_control(os.path.join(os.getenv("RAILWAY_VOLUME_MOUNT_PATH"), "bot_data.sql"))
register_handlers(bot, sch_parser)

start_week_updating()


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
