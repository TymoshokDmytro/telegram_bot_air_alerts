# -*- coding: utf-8 -*-
import os
import sys
import time
import traceback
from threading import Thread

import requests
import telebot
import uvicorn
from loguru import logger as log
from dotenv import load_dotenv

from app.alerts_api_service import AlertsAPIService
from app.healthcheck_server import app


def add_workdir_path(abs_file_path):
    return os.path.join(os.path.dirname(__file__), abs_file_path)


load_dotenv(add_workdir_path(".env"))
bot = telebot.TeleBot(os.environ["BOT_TOKEN"])
CHAT_ID = int(os.environ["CHAT_ID"])
POLLING_PERIOD_SEC = int(os.getenv("POLLING_PERIOD_SEC", 15))
STATE_NUMBER = int(os.getenv("STATE_NUMBER", 25))

log.remove()
os.makedirs(add_workdir_path("logs"), exist_ok=True)
log_format = "{time:YYYY-MM-DD} | {time:HH:mm:ss} | urls_check | {level: <5} | {function} | {message}"
log.add(sys.stdout, format=log_format, level="DEBUG")


# log.add(add_workdir_path("logs/log"), format=log_format, rotation="00:00", retention='14 days', level="DEBUG")


@bot.message_handler(commands=['start'])
def start(message):
    log.debug(f"Received /start from chat.id={message.chat.id}")
    bot.send_message(message.from_user.id, "Йобана русня 🤬")


def start_telegram_bot_app():
    alerts_api = AlertsAPIService(api_key=os.environ["ALERTS_API_KEY"])
    log.info(f"TelegramAirAlarmBot application started. CHAT_ID={CHAT_ID} | "
             f"POLLING_PERIOD_SEC={POLLING_PERIOD_SEC}")
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
                            bot.send_message(CHAT_ID, "Йобана русня 🤬")
                        else:  # The alarm is off | Вiдбiй повiтрянної тривоги
                            bot.send_message(CHAT_ID, "Вiдбiй повiтрянної тривоги. Слава Українi 🇺🇦")
                    except KeyboardInterrupt:
                        log.warning("Stopped by KeyboardInterrupt while sending the bot message")
                        bot.stop_bot()
                        exit()
                    except Exception as e:
                        log.error(f"While sending bot message exception happened: {type(e)} {str(e)}")
                    current_state_status = api_result
            time.sleep(POLLING_PERIOD_SEC)
    finally:
        log.info("TelegramAirAlarmBot application stopped")
        bot.stop_bot()


def send_periodical_request():
    url = os.getenv("REQUEST_URL")
    request_period = int(os.getenv("REQUEST_PERIOD", 600))
    log.info(f"{url=} | {request_period=}")
    if not url:
        log.error("No url defined to send requests to")
        return

    time.sleep(3)  # Waiting until server is up
    while True:
        try:
            requests.get(url)
        except Exception:
            log.error(traceback.format_exc())

        time.sleep(request_period)


if __name__ == '__main__':
    http_server_params = {
        "http": "h11",
        "loop": "uvloop",
        "port": 8000,
        "host": "0.0.0.0",
    }
    app.state.status = True
    http_server_thread = Thread(target=uvicorn.run, daemon=True, args=(app,), kwargs=http_server_params)
    http_server_thread.start()
    log.debug("Healthcheck server started on endpoint /health and 8000 port.")

    request_sending_thread = Thread(target=send_periodical_request, daemon=True)
    request_sending_thread.start()

    start_telegram_bot_app()
