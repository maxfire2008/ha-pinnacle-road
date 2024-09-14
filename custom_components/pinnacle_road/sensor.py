import requests
import re
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

# Lookup table for gate information (Temporary: 5 gates)
GATE_INFO = {
    0: {"name": "Bracken Lane (Gate 1)", "lat": -42.917, "lon": 147.261},
    1: {"name": "Below The Springs (Gate 2)", "lat": -42.912, "lon": 147.253},
    2: {"name": "The Springs (Gate 3)", "lat": -42.914, "lon": 147.246},
    3: {"name": "The Chalet (Gate 4)", "lat": -42.890, "lon": 147.236},
    4: {"name": "Big Bend (Gate 5)", "lat": -42.890, "lon": 147.221},
}


URL = "https://hccapps.hobartcity.com.au/PinnacleRoad/"


class PinnacleRoadSensor(SensorEntity):
    def __init__(self):
        self._state = None
        self._gate_closed = None
        self._gate_name = None
        self._gate_lat = None
        self._gate_lon = None
        self._next_update = None
        self._last_update = None
        self._reason_for_closure = None
        self._walking_distance_to_snow = None

    @property
    def name(self):
        return "Pinnacle Road Status"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {
            "gate_closed": self._gate_closed,
            "gate_name": self._gate_name,
            "gate_lat": self._gate_lat,
            "gate_lon": self._gate_lon,
            "next_update": self._next_update,
            "last_update": self._last_update,
            "reason_for_closure": self._reason_for_closure,
            "walking_distance_to_snow": self._walking_distance_to_snow,
        }

    def update(self):
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                content = response.text

                # Regex to extract the gate status
                closed_gate_match = re.search(r"var closedGate = (\d+);", content)
                if closed_gate_match:
                    closed_gate_id = int(closed_gate_match.group(1))
                    if closed_gate_id == 1:
                        self._state = "Road Open"
                    else:
                        self._state = f"Road Closed at Gate {closed_gate_id - 2}"

                    # Update gate info
                    gate_info = GATE_INFO.get(closed_gate_id - 2, {})
                    self._gate_name = gate_info.get("name", "Unknown")
                    self._gate_lat = gate_info.get("lat", "Unknown")
                    self._gate_lon = gate_info.get("lon", "Unknown")

                # Regex to extract Next Update, Last Update, Reason for Closure, and Walking Distance to Snow
                self._next_update = (
                    re.search(
                        r"<strong>Next update:</strong>\s*([\d\w\s:-/]+)<br />", content
                    )
                    .group(1)
                    .strip()
                )
                self._last_update = (
                    re.search(
                        r"<strong>Last update:</strong>\s*([\d\w\s:-/]+)<br />", content
                    )
                    .group(1)
                    .strip()
                )
                self._reason_for_closure = (
                    re.search(
                        r"<strong>Reason for closure:</strong><span>(.*?)</span>",
                        content,
                    )
                    .group(1)
                    .strip()
                )
                self._walking_distance_to_snow = (
                    re.search(
                        r"<strong>Walking distance to snow:</strong>\s*(N/A|\d+\s*km)<br />",
                        content,
                    )
                    .group(1)
                    .strip()
                )

            else:
                _LOGGER.error(
                    f"Failed to fetch data from {URL}. Status code: {response.status_code}"
                )

        except Exception as e:
            _LOGGER.error(f"Error fetching Pinnacle Road data: {e}")
