from __future__ import print_function
from dataclasses import dataclass, field
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, COMError
from pymidicontroller.classes.controller import ControllerExtension
from pymidicontroller.extensions.common import translate


@dataclass()
class Device(ControllerExtension):
    """Device"""
    min: float = -65.25
    max: float = 0

    def __post_init__(self):
        super().__post_init__()
        self.set_metadata('update_frequency', 0)

    def update(self, attribute, value): #Optional if you need to do further processing on the value
        self.set_metadata('post_flag', True)
        super().update(attribute, value)

    def get_device(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        return volume

    def execute(self):
        post_flag = self.get_metadata('post_flag')
        if post_flag:
            translated_volume = translate(self.get_attribute('value'),0,127,self.min,self.max)
            device = self.get_device()
            try:
                device.SetMasterVolumeLevel(translated_volume, None)
            except COMError as ce:
                print(ce)
                pass
            self.set_metadata('post_flag', False)

@dataclass()
class Application(ControllerExtension):
    """Application"""
    application: str = 'default'
    min: float = 0
    max: float = 1
    
    def __post_init__(self):
        super().__post_init__()
        self.set_metadata('update_frequency', 0)

    def update(self, attribute, value): #Optional if you need to do further processing on the value
        self.set_metadata('post_flag', True)
        super().update(attribute, value)

    def get_session(self):
        session_list = []
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process and session.Process.name() == self.application:
                session_list.append(volume)
        return session_list

    def execute(self):
        post_flag = self.get_metadata('post_flag')
        if post_flag:
            translated_volume = translate(self.get_attribute('value'),0,127,self.min,self.max)
            for application in self.get_session():
                application.SetMasterVolume(translated_volume, None)
                self.set_metadata('post_flag', False)