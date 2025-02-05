from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

import config


def start_week_updating():
    def week_update():
        if config.week == 0:
            config.week = 1
        else:
            config.week = 0
        print(f"Обновлена неделя на {config.week}", datetime.now())

    scheduler_week_type = BackgroundScheduler()
    scheduler_week_type.add_job(week_update, 'cron', day_of_week='sat', hour=18, minute=0)
    scheduler_week_type.start()


def start_users_monitoring():
    def update_users_per_day():
        print(f"Запросов сегодня: {config.users_per_day}")
        config.users_per_day = 0

    scheduler_users_requests_per_day = BackgroundScheduler()
    scheduler_users_requests_per_day.add_job(update_users_per_day, 'cron', hour=23, minute=45)
    scheduler_users_requests_per_day.start()
