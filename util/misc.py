import datetime
import time

def get_unix_now() -> str:
    now_unix = time.mktime(datetime.datetime.now().timetuple())
    now_unix = int(now_unix)
    return f'<t:{now_unix}:R>'