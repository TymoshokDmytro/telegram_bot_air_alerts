import asyncio
import os
import random

from aiohttp_sse_client import client as sse_client

import requests
from dotenv import load_dotenv
from loguru import logger as log

from app.helpers import serialize_magic


class BaseAlertsAPIService:
    __slots__ = ("base_url", "_api_key")

    def __init__(self, api_key: str):
        self.base_url = os.getenv("API_BASE_URL", "https://alerts.com.ua")
        self._api_key = api_key


class AlertsAPIService(BaseAlertsAPIService):
    """ API wrapper to receive one state information for https://alerts.com.ua/"""

    def check_state_request(self, state_number: int = 25):  # 25 = Kyiv
        if not isinstance(state_number, int):
            log.error(f"Incorrect state_number type: {type(state_number)} value={state_number}")
            return
        try:
            alert_status = random.choice((True, False))
            log.debug(f"Retrieved alert status: {alert_status}")
            return alert_status

            # resp = requests.get(f"{self.base_url}/api/states/{state_number}", headers={"X-API-Key": self._api_key}, timeout=30)
            # if resp.status_code == 200:
            #     alert_status = resp.json()["state"]["alert"]
            #     log.debug(f"Retrieved alert status: {alert_status}")
            #     return alert_status
            # else:
            #     log.error(f"Got state status response with status_code={resp.status_code} | content={resp.content}")

        except Exception as e:
            log.error(f"State status request failed with error: {type(e)} {str(e)}")

        return


class AlertsSSEService(BaseAlertsAPIService):
    """ This uses the sse event stream from https://alerts.com.ua/ """

    async def _async_sse_processing(self, state_number):
        events_list = list()
        while True:
            async with sse_client.EventSource(
                    url=f"{self.base_url}/api/states/live/{state_number}",
                    headers={"X-API-Key": self._api_key}
            ) as event_source:
                try:
                    async for event in event_source:
                        if event.type != "ping":
                            log.info(f"Received event: type={event.type} | data_type={type(event.data)} | data={event.data}")
                            events_list.append(event)
                            serialize_magic(events_list, "events.pkl")
                except (ConnectionError, asyncio.exceptions.TimeoutError) as e:
                    log.error(f"Asyncio connection error: {type(e)} {str(e)}. Reconnecting")

    def process_sse_events(self, state_number: int = 25):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._async_sse_processing(state_number))

# if __name__ == '__main__':
#     load_dotenv("app/.env")
#     api_service = AlertsSSEService(api_key=os.getenv("ALERTS_API_KEY"))
#     api_service.process_sse_events()
