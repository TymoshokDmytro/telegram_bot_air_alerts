# -*- coding: utf-8 -*-
import os
import sys
import time

import telebot
from loguru import logger as log
from dotenv import load_dotenv

from app.alerts_api_service import AlertsAPIService

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
bot = telebot.TeleBot(os.environ["BOT_TOKEN"])
CHAT_ID = int(os.getenv("CHAT_ID", 240650925))
POLLING_PERIOD_SEC = int(os.getenv("POLLING_PERIOD_SEC", 10))
STATE_NUMBER = int(os.getenv("STATE_NUMBER", 25))


def add_workdir_path(abs_file_path):
    return os.path.join(os.path.dirname(__file__), abs_file_path)


log.remove()
os.makedirs(add_workdir_path("logs"), exist_ok=True)
log_format = "{time:YYYY-MM-DD} | {time:HH:mm:ss} | urls_check | {level: <5} | {function} | {message}"
log.add(sys.stdout, format=log_format, level="DEBUG")
log.add(add_workdir_path("logs/log"), format=log_format, rotation="00:00", retention='14 days', level="DEBUG")


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.from_user.id, "Йобана русня 🤬")


# bot.send_message(-760220586, f"Йобана русня 🤬")

if __name__ == '__main__':
    alerts_api = AlertsAPIService(api_key=os.environ["ALERTS_API_KEY"])

    api_result = alerts_api.check_state_request(state_number=STATE_NUMBER)
    if not isinstance(api_result, bool):
        log.error(f"Got None from check_state. Aborting.")
        exit(1)

    current_state_status = api_result

    if current_state_status is True:
        try:
            bot.send_message(CHAT_ID, f"Йобана русня 🤬")
        except Exception as e:
            log.error(f"While sending bot message exception happened: {type(e)} {str(e)}")
    time.sleep(POLLING_PERIOD_SEC)
    try:
        while True:
            api_result = alerts_api.check_state_request(state_number=STATE_NUMBER)
            if isinstance(api_result, bool):
                if api_result is not current_state_status:
                    try:
                        if api_result is True:  # The alarm is triggered | Повiтряна тривога
                            bot.send_message(CHAT_ID, f"Йобана русня 🤬")
                        else:  # The alarm is off | Вiдбiй повiтрянної тривоги
                            bot.send_message(CHAT_ID, f"Вiдбiй повiтрянної тривоги. Слава Українi 🇺🇦")
                    except KeyboardInterrupt:
                        log.warning("Stopped by KeyboardInterrupt while sending the bot message")
                        bot.stop_bot()
                        exit()
                    except Exception as e:
                        log.error(f"While sending bot message exception happened: {type(e)} {str(e)}")
                    current_state_status = api_result
            time.sleep(POLLING_PERIOD_SEC)
    except KeyboardInterrupt:
        bot.stop_bot()
    finally:
        bot.stop_bot()
