"""////////////////////////////////////////////////////////////////////////////////////////////////
installation notes:
place this file in the following folder and restart home assistant:
/config/custom_components/sensor

yaml configuration example:
sensor:
  - platform: my_ip
    

////////////////////////////////////////////////////////////////////////////////////////////////"""
import datetime
import logging
import asyncio
import traceback
import json
import requests
import voluptuous as vol
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity, async_generate_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.event import async_track_time_interval

REQUIREMENTS = []
DEPENDENCIES = []
_LOGGER = logging.getLogger(__name__)
DOMAIN = "sensor"
ENTITY_ID_FORMAT = DOMAIN + '.{}'
name = "External Ip"
api_url = "https://techblog.co.il/ip.php"

@callback
def send_api_request():
        api_response = requests.get(api_url)
        data = json.loads(api_response.text)
        return data['ip']
        
@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    _LOGGER.debug("starting platform setup")
    sensors = []
    sensors.append(GET_IP(hass, name, api_url))
    async_add_devices(sensors)
    return True

class GET_IP(Entity):
    """representation of the sensor entity"""
    def __init__(self, hass, name, url):
        """initialize the sensor entity"""
        self.entity_id = async_generate_entity_id(ENTITY_ID_FORMAT, name, hass=hass)
        self.hass = hass
        self._name = name
        self._url = url
        self._state = send_api_request()
        async_track_time_interval(hass, self.async_update_current, datetime.timedelta(seconds=600))
        _LOGGER.debug(self._name + " initiated")

    @property
    def name(self):
        """friendly name"""
        return self._name

    @property
    def should_poll(self):
        """entity should not be polled for updates"""
        return False

    @property
    def state(self):
        """sensor state"""
        return self._state

    @property
    def icon(self):
        """sensor icon"""
        return "mdi:ethernet"
        
    @asyncio.coroutine
    def async_update_current(self, call):
        """handling state updates"""
        self._state = send_api_request()
        yield from self.async_update_ha_state()