from pymidicontroller.classes.controller import ControllerExtension
from pymidicontroller.extensions.common import translate
from dataclasses import dataclass
import requests
import json

@dataclass()
class Client:
    uri: str
    token: str

    def post_data(self,data,domain,service):
        headers = {
            'Authorization': f'Bearer {self.token}', 
            'Content-Type': 'application/json'
        }
        # print(data)
        requests.post(f'{self.uri}/api/services/{domain}/{service}', headers=headers, data=json.dumps(data))
        return True

@dataclass()
class Light(ControllerExtension):
    entity_id: str = None
    client: Client = None

    def __post_init__(self):
        super().__post_init__()
        if self.client == None:
            import sys; sys.exit('No client registered')
        self.set_metadata('update_frequency', 1)
        self.set_attribute('colour_mode', 'hs')
        self.set_metadata('init', True)

    def update(self, attribute, value): #Optional if you need to do further processing on the value
        self.set_metadata('post_flag', True)
        super().update(attribute, value)

    def execute(self):
        if not self.get_metadata('init'):
            self.first_run()
        
        post_flag = self.get_metadata('post_flag')
        if post_flag:
            transition = self.get_metadata('update_frequency')
            brightness = translate(self.get_attribute('brightness_channel'),0,127,0,255)

            data = {}
            data['brightness'] = round(brightness)
            data['transition'] = transition
            data['entity_id'] = self.entity_id

            colour_mode = self.get_attribute('colour_mode')
            if colour_mode == 'rgb':
                red = translate(self.get_attribute('red_channel'),0,127,0,255)
                green = translate(self.get_attribute('green_channel'),0,127,0,255)
                blue = translate(self.get_attribute('blue_channel'),0,127,0,255)
                data['rgb_color'] = (
                    round(red), 
                    round(green), 
                    round(blue)
                )

            elif colour_mode == 'hs':
                hue = translate(self.get_attribute('hue_channel'),0,127,0,360)
                saturation = translate(self.get_attribute('saturation_channel'),0,127,0,100)
                data['hs_color'] = (
                    round(hue), 
                    round(saturation)
                )
            post_data = self.client.post_data(data, 'light', 'turn_on')
            self.set_metadata('post_flag', not post_data)
            self.get_attribute('colour_mode')
            return not post_data
        return False

    def change_colour_mode(self):
        current_colour_mode = self.get_attribute('colour_mode')
        colour_modes = ['hs', 'rgb']

        current_colour_mode_index = colour_modes.index(current_colour_mode)
        new_colour_mode = colour_modes[(current_colour_mode_index + 1) % len(colour_modes)]
        self.set_attribute('colour_mode', new_colour_mode)
        # print(f"Color mode set to: {self.get_attribute('colour_mode')}")

@dataclass
class Switch(ControllerExtension):
    entity_id: str = None
    client: Client = None

    def __post_init__(self):
        super().__post_init__()
        self.set_metadata('update_frequency', 0.1)
        if self.client == None:
            import sys; sys.exit('No client registered')

    def update(self, attribute, value):
        last_button_state = self.get_attribute('button_state')

        button_state = 1 if value > 0 else 0
        
        if last_button_state == 0 and button_state == 1:
            self.set_metadata('post_flag', True)
        self.set_attribute('button_state', button_state)
        super().update(attribute, value)

    def execute(self):
        post_flag = self.get_metadata('post_flag')
        if post_flag:
            
            data = {}
            data['entity_id'] = self.entity_id

            post_data = self.client.post_data(data, 'switch', 'toggle')
            self.set_metadata('post_flag', not post_data)
            return not post_data
        return False
