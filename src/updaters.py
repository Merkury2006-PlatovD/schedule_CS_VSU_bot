from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

import config
from db_controller import DBController


def start_week_updating():
    def week_update():
        last_week = DBController.get_current_week_type()
        print(f"Обновлена неделя c {last_week}")
        if last_week == 0:
            DBController.update_current_week_type(1)
        else:
            DBController.update_current_week_type(0)
        print(f"Обновлена неделя на {DBController.get_current_week_type()}", datetime.now())

    scheduler_week_type = BackgroundScheduler()
    scheduler_week_type.add_job(week_update, 'cron', day_of_week='sat', hour=18, minute=0)
    scheduler_week_type.start()


def start_users_monitoring():
    def update_users_per_day():
        print(f"Запросов сегодня: {DBController.get_users_per_day()}")
        DBController.set_users_per_day(0)

    scheduler_users_requests_per_day = BackgroundScheduler()
    scheduler_users_requests_per_day.add_job(update_users_per_day, 'cron', hour=21, minute=45)
    scheduler_users_requests_per_day.start()
