from datetime import datetime
import pytz


def now_paris():
    return datetime.now(pytz.timezone("Europe/Paris"))
