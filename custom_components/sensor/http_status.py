"""////////////////////////////////////////////////////////////////////////////////////////////////
This sensor checks the status of network objects such as Computers, Routers, Servers, Esp8266 based sensors, Smart TV and more
The sensor is checking the object status by using fping commans wich needs to be installs.
to install fping, run the fallowing command:
sudo apt-get install fping --yes

Date: 26/04/2018
Author: Tomer Klein & Tomer Figenblat 

installation notes:
place this file in the following folder and restart home assistant:
/config/custom_components/sensor

yaml configuration example:
sensor:
  - platform: device_status
    host: Required - host ipaddress / FQDN (google.com etc)
    name: Optional - Friendly Entity name
    

////////////////////////////////////////////////////////////////////////////////////////////////"""
import datetime
import logging
import requests
import re
import subprocess
import voluptuous as vol
from homeassistant.helpers.entity import Entity, generate_entity_id # TomerF: change async_generate_entity_id to generate_entity_id
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import DOMAIN, PLATFORM_SCHEMA # TomerF: imported DOMAIN instead of setting it manually
# from homeassistant.helpers.event import async_track_time_interval # TomerF: methods that starts with 'async' are meant to by used with asyncio
from homeassistant.const import (CONF_HOST, CONF_NAME, CONF_SCAN_INTERVAL, CONF_ICON, CONF_DEVICES)


REQUIREMENTS = []
DEPENDENCIES = []
_LOGGER = logging.getLogger(__name__)
#DEFAULT_NAME = 'Check Status' # TomerFi: no need for a default name after switching to slugs, will use slug id as a name.
SCAN_INTERVAL_DEFAULT = datetime.timedelta(seconds=10)
DEFAULT_ICON = "mdi:desktop-classic"
#DOMAIN = "sensor" # TomerF: no need for that, imported it from homeassistant.components.sensor.DOMAIN instead.
PLATFORM_NAME = "http_status"
ENTITY_ID_FORMAT = DOMAIN + '.' + PLATFORM_NAME + '_{}' # TomerFi: added the platform name to the entity id format, its not a must but its the best practice
"""
# TomerF: OLD Schema
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
})
"""
DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_NAME): cv.string, # TomerF: deleted the default=DEFAULT_NAME key, if it has a default value its not really optional it will always exists
    vol.Required(CONF_ICON, default=DEFAULT_ICON): cv.icon # TomerF: changed Optional to Requiered, changed validation to cv.icon instead of cv.string
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL_DEFAULT): cv.positive_timedelta,
    vol.Required(CONF_DEVICES):
        vol.Schema({cv.slug: DEVICE_SCHEMA})
})

"""
# TomerF: Old setup
def setup_platform(hass, config, add_devices, discovery_info=None):
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    icon = config.get(CONF_ICON)
    sensors = []
    sensors.append(CHECK_STATUS(hass, name, host, icon, config))
    add_devices(sensors)
    return True
"""
def setup_platform(hass, config, add_devices, discovery_info=None):
    
    scan_interval = config.get(CONF_SCAN_INTERVAL) # TomerF: not doing anything with this, but added it for the example sake
    devices = config.get(CONF_DEVICES)

    entities = []

    for slug_id, config in devices.items():
        name = config.get(CONF_NAME, None)
        host = config.get(CONF_HOST)
        icon = config.get(CONF_ICON)
        
        device = CHECK_STATUS(slug_id, hass, name, host, icon)

        entities.append(device)

    add_devices(entities, True)
    return True

def get_http_status(host):
    r = requests.get(host)
    status = r.status_code
    if status==200 or status==401:
        return 'up'
    else:
        return 'down'

class CHECK_STATUS(Entity):
    """representation of the sensor entity"""
    def __init__(self, slug_id, hass, name, host, icon):
        # TomerF: deleted 'config, discovery_info=None' from the __init__ arguments, there is no use for them
        """initialize the sensor entity"""
        # TomerF: added slug id as a parmeter and turned it to entity id
        self.entity_id = generate_entity_id(ENTITY_ID_FORMAT, slug_id, hass=hass)
        self.hass = hass
        self._name = name
        self._host = host
        self._icon = icon # TomerF: you're not using self._icon anywhere...
        self._state = get_http_status(host)
        # self.update() #TomerF: there is no need for that since we are calling 'add_devices(entities, True)' the True means that entity will get updated right after initializtion

    @property
    def name(self):
        """friendly name"""
        return self._name

    @property
    def host(self):
        """host"""
        # TomerF: you are not using this property anywhere.
        return self._host

    @property
    def should_poll(self):
        """entity should not be polled for updates"""
        # TomerF: changed to true.
        return True

    @property
    def state(self):
        """sensor state"""
        return self._state

    @property
    def icon(self):
        """sensor icon"""
        if self._state == 'up':
            return 'mdi:upload-network'
        else:
            return 'mdi:close-network'
            
        return self._icon
     
    def update(self):
        """handling state updates"""
        self._state = get_http_status(self._host)
        #yield from self.async_update_ha_state() # TomerF: no need for update_ha_state if should_poll is true and not in asyncio mode