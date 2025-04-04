from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import screen_brightness_control as sbc
import pyautogui
from typing import Optional, Tuple
from config import SystemControlSettings

class SystemController:
    def __init__(self, settings: SystemControlSettings):
        self.settings = settings
        self._init_audio()
        self._init_brightness()
        pyautogui.FAILSAFE = False
        
    def _init_audio(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_controller = cast(interface, POINTER(IAudioEndpointVolume))
            self.current_volume = self.volume_controller.GetMasterVolumeLevelScalar()
        except Exception as e:
            print(f"Error initializing audio controller: {str(e)}")
            self.volume_controller = None

    def _init_brightness(self):
        try:
            self.current_brightness = sbc.get_brightness()[0] / 100
        except Exception as e:
            print(f"Error initializing brightness control: {str(e)}")
            self.current_brightness = None

    def adjust_volume(self, value: float) -> Optional[float]:
        try:
            if self.volume_controller is None:
                raise Exception("Volume controller not initialized")
            value = max(0.0, min(1.0, value))
            self.volume_controller.SetMasterVolumeLevelScalar(value, None)
            self.current_volume = value
            return value
        except Exception as e:
            print(f"Error adjusting volume: {str(e)}")
            return None

    def adjust_brightness(self, value: float) -> Optional[float]:
        try:
            value = max(0.0, min(1.0, value))
            brightness_percent = int(value * 100)
            sbc.set_brightness(brightness_percent)
            self.current_brightness = value
            return value
        except Exception as e:
            print(f"Error adjusting brightness: {str(e)}")
            return None

    def media_control(self, action: str):
        try:
            if action == 'play_pause':
                pyautogui.press('playpause')
            elif action == 'next_track':
                pyautogui.press('nexttrack')
            elif action == 'prev_track':
                pyautogui.press('prevtrack')
            elif action == 'seek_forward':
                pyautogui.press('right')
            elif action == 'seek_backward':
                pyautogui.press('left')
        except Exception as e:
            print(f"Error in media control: {str(e)}")

    def get_system_status(self) -> Tuple[Optional[float], Optional[float]]:
        return self.current_volume, self.current_brightness
