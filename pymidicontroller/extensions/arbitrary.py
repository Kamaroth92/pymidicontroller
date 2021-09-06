from pymidicontroller.classes.controller import ControllerExtension
from dataclasses import dataclass

@dataclass
class Toggle(ControllerExtension):       
    func: any = None

    def __post_init__(self):
        super().__post_init__()
        self.set_metadata('update_frequency', 1)
        self.set_metadata('init', True)

    def update(self, attribute, value): #Optional if you need to do further processing on the value
        last_button_state = self.get_attribute('button_state')
        button_state = 1 if value > 0 else 0
        
        if last_button_state == 0 and button_state == 1: #Low to high
            self.set_metadata('post_flag', True)
        self.set_attribute('button_state', button_state)
        super().update(attribute, value)

    def execute(self):
        post_flag = self.get_metadata('post_flag')
        if post_flag:
            self.func()
            self.set_metadata('post_flag', False)
        return False
