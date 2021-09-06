# pymidicontroller

## Introduction

Easily map device and application controls to a midi controller  
Example video availble here: https://streamable.com/ie5jtt

This library is ideally not only easy to use but also easy to extend with additional targets.
Currently included targets are:  
  * Homeassistant (via REST API)
  * Windows Volume Mixer (via [pycaw](https://github.com/AndreMiras/pycaw))

**Note: This library is in need of refactoring as the way things were done was changed multiple times during the devlopment, therefore please be aware that there may be upcoming breaking changes.**

## Installation
Clone the repo and run ```pip install .``` from the cloned directory.

## Usage
The following shows my currently in-use implementation of the library. It demonstrates both the volumemixer and homeassistant extensions as well as how you may decide to control multiple targets with the same controlclass. (i.e. same slider controlling multiple application audios, or multiple lights)

```python
from pymidicontroller.classes.controller import Controller
from pymidicontroller.extensions import *
import mido

my_midi_controller = "WORLDE easy CTRL"  ##CHANGEME
homeassistant_uri = "https://my-home-assistant"  ##CHANGEME
homeassistant_token = "3fs0eXAsfOiJKV1QiL...."  ##CHANGEME

if __name__ == '__main__':
dev = my_midi_controller
names = mido.get_input_names()
device_name = None
if dev != None:
    for name in names:
        if name.startswith(dev):
            device_name = name

device = Controller(device_name)

homeassistant_client = homeassistant.Client(homeassistant_uri, homeassistant_token)

#Create controllable objects
bedroom_lights = homeassistant.Light(entity_id='light.bedroom_lights', client=homeassistant_client)
circadian_lighting = homeassistant.Switch(entity_id='switch.circadian_lighting_circadian_lighting', client=homeassistant_client)
power_switch_02 = homeassistant.Switch(entity_id='switch.iot_kem_02_plug', client=homeassistant_client)
cycle_color_mode = arbitrary.Toggle(func=bedroom_lights.change_colour_mode)

master_volume = volumemixer.Device()
spoitfy_volume = volumemixer.Application(application='Spotify.exe')
discord_volume = volumemixer.Application(application='Discord.exe')
tarkov_volume = volumemixer.Application(application='EscapeFromTarkov.exe')
r6_volume = volumemixer.Application(application='RainbowSix.exe')

#Create controllers and map them to controllable objects
#device.register_mapping(CHANNEL, CONTROL, TARGET, EXTRA_DATA)

device.register_mapping(1, 21, bedroom_lights,'brightness_channel')
device.register_mapping(1, 8, bedroom_lights,'red_channel')
device.register_mapping(1, 9, bedroom_lights,'green_channel')
device.register_mapping(1, 9, bedroom_lights,'hue_channel')
device.register_mapping(1, 10, bedroom_lights,'blue_channel')
device.register_mapping(1, 10, bedroom_lights,'saturation_channel')

device.register_mapping(1, 29, power_switch_02)
device.register_mapping(1, 30, cycle_color_mode)
device.register_mapping(1, 31, circadian_lighting)

device.register_mapping(1, 11, master_volume)
device.register_mapping(1, 3, spoitfy_volume)
device.register_mapping(1, 4, discord_volume)
device.register_mapping(1, 5, tarkov_volume)
device.register_mapping(1, 5, r6_volume)

device.loop()
```

## Future Plans
  * **WRITE DOCUMENTATION**
  * **ADD ERROR HANDLING**
  * Add Spotify functionality via [spotipy](https://github.com/plamere/spotipy)
  * Add Discord functionality via [discord.py](https://github.com/Rapptz/discord.py)
  * Add the ability to get the current state of each control on initialization. I believe this will require a midi controller with the sys_ex function to support this but I know pretty little about sys_ex messages.
  * Add functionality to change between channels or banks without relying on the controller to have a bank switch.
