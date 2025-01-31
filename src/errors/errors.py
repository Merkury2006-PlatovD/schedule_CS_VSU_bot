class ScheduleParserFindError(Exception):
    """ Ошибка нахождения курса+группы+подгруппы в файле"""
    def __init__(self, message="ScheduleParserFindError parser didn't find required column", error_code=None):
        super().__init__(message)
        self.message = message