import os

import requests
from loguru import logger as log


class AlertsAPIService:
    """ API wrapper to receive one state information for https://alerts.com.ua/"""
    __slots__ = ("base_url", "_api_key")

    def __init__(self, api_key: str):
        self.base_url = os.getenv("API_BASE_URL", "https://alerts.com.ua")
        self._api_key = api_key

    def check_state_request(self, state_number: int = 25):  # 25 = Kyiv
        if not isinstance(state_number, int):
            log.error(f"Incorrect state_number type: {type(state_number)} value={state_number}")
            return
        try:
            # return random.choice((True, False))
            resp = requests.get(f"{self.base_url}/api/states/{state_number}", headers={"X-API-Key": self._api_key}, timeout=30)
            if resp.status_code == 200:
                alert_status = resp.json()["state"]["alert"]
                log.debug(f"Retrieved alert status: {alert_status}")
                return alert_status
            else:
                log.error(f"Got state status response with status_code={resp.status_code} | content={resp.content}")

        except Exception as e:
            log.error(f"State status request failed with error: {type(e)} {str(e)}")

        return
