from dataclasses import dataclass, field
from time import time, sleep
import mido
import sys

from pymidicontroller.extensions import common

@dataclass()
class ControlClass:
    """Midi control class values"""
    channel: int
    control: int
    target: all = None
    data: all = 'value'
    
    value: float = 0
    lower_left: int = 0
    upper_right: int = 127

@dataclass
class ControllerExtension:
    """The minimum required values for an extension to work with a Controller class"""
    attributes: dict = field(default_factory = lambda: ({}))
    metadata: dict = field(default_factory = lambda: ({
        'update_frequency': 1,
        'last_exec_time': 0,
        'post_data': None
    }))
    min_value: int = 0
    max_value: int = 255

    def __post_init__(self):    
        execute_function_exists = "execute" in dir(self)
        if not execute_function_exists:
            import sys; sys.exit(f"{type(self)} requires an 'execute' function.")

        update_function_exists = "update" in dir(self)
        if not update_function_exists:
            import sys; sys.exit(f"{type(self)} requires an 'update' function.")

    def set_attribute(self, key, value):
        return self._set_value_in_dict(self.attributes, key, value)

    def set_metadata(self, key, value):
        return self._set_value_in_dict(self.metadata, key, value)

    def get_attribute(self, key):
        return self._get_value_from_dict(self.attributes, key)

    def get_metadata(self, key):
        return self._get_value_from_dict(self.metadata, key)

    def _get_value_from_dict(self, dict, key):
        if key in dict:
            return dict[key]
        else:
            return 0

    def _set_value_in_dict(self, dict, key, value):
        dict[key] = value
        if key in dict and dict[key] == value:
            return True
        else:
            return False

    def update(self, attribute, value):
        return self.set_attribute(attribute, value)

    def invoke(self):
        current_time = time()
        last_post_time = self.get_metadata('last_exec_time')
        update_frequency = self.get_metadata('update_frequency')
        time_check = current_time - last_post_time <= update_frequency
        if not time_check:
            target_execution = self.execute()
            self.set_metadata('last_exec_time', current_time)
            return target_execution
        return False

@dataclass()
class Controller:
    """Midi controller"""
    name: str
    controls: list[ControlClass] = field(default_factory=list)
    update_rate: float = 0.01

    is_connected: bool = False
    initialized: bool = False

    def init(self):
        if self.name in mido.get_input_names():
            midi_device = mido.open_input(self.name)
            self.initialized = True
            self.check_connection()
            print(f'Device {self.name} connected.')
            return midi_device
        else:
            return None

    def check_connection(self):
        if self.initialized and self.name in mido.get_input_names():
            self.is_connected = True
        else:
            self.is_connected = False
            self.initialized = False

    def get_controls(self):
        return self.controls

    def register_mapping(self, channel, control, target, data=None):
        cc = ControlClass(channel, control, target, data)
        self.controls.append(cc)

    def update_control(self, channel, control, value):
        channel = channel+1
        for cc in self.get_controls():
            if cc.channel == channel and cc.control == control:
                if cc.data == None:
                    cc.data = 'value'
                cc.target.update(cc.data, value)

    def loop(self):
        midi_device = None

        while True:
            try:
                self.check_connection()
                while not self.is_connected:
                    midi_device = self.init()

                ignore_list = []
                for message in common.reversed_iterator(midi_device.iter_pending()):
                    formatted_message = vars(message)
                    if formatted_message['type'] == 'control_change':
                        control = formatted_message['control']
                        value = formatted_message['value']
                        channel = formatted_message['channel']
                        if f'{channel}:{control}' not in ignore_list:
                            self.update_control(channel, control, value)
                            ignore_list.append(f'{channel}:{control}')
                ignore_list = []
                for cc in self.get_controls():
                    target = cc.target
                    if target not in ignore_list:
                        target.invoke()
                        ignore_list.append(target)

                sleep(self.update_rate)
            except KeyboardInterrupt:
                print('Exiting...')
                sys.exit()