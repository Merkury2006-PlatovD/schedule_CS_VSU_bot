from handlers import register_handlers
from parser.excell_converter import ScheduleParser


class BotController:
    bot = None

    @classmethod
    def set_bot(cls, bot):
        cls.bot = bot

    @classmethod
    def refresh_bot(cls):
        sch_parser = ScheduleParser(f'/tmp/schedule.xlsx')
        cls.bot.message_handlers.clear()
        cls.bot.callback_query_handlers.clear()
        cls.bot.inline_handlers.clear()
        cls.bot.polling_thread = None  # Если бот запущен в polling
        register_handlers(cls.bot, sch_parser)
