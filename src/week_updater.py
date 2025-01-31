from datetime import datetime
import config

from apscheduler.schedulers.background import BackgroundScheduler


def start_week_updating():
    def week_update():
        if config.week == 0:
            config.week = 1
        else:
            config.week = 0
        print(f"Обновлена неделя на {config.week}", datetime.now())

    scheduler = BackgroundScheduler()
    scheduler.add_job(week_update, 'cron', day_of_week='sat', hour=18, minute=0)
    scheduler.start()
