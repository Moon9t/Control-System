from dataclasses import dataclass
import numpy as np
from typing import Dict, List, Tuple

@dataclass
class GestureThresholds:
    pinch_distance: int = 40
    swipe_distance: int = 50
    vertical_gesture_distance: int = 100
    rotation_angle: int = 30

@dataclass
class SystemControlSettings:
    volume_step: float = 0.02
    brightness_step: float = 0.05
    media_seek_step: int = 5  # seconds

@dataclass
class AnimationSettings:
    particle_count: int = 50
    particle_max_speed: float = 2.0
    particle_size: int = 2
    particle_lifetime: int = 30
    hex_rotation_speed: float = 2.0

@dataclass
class ColorScheme:
    base: Dict[str, Tuple[int, int, int]] = None
    
    def __post_init__(self):
        self.base = {
            'default': (0, 255, 255),  # Cyan
            'volume_up': (0, 255, 100),  # Green-Cyan
            'volume_down': (0, 200, 255),  # Blue-Cyan
            'brightness_up': (255, 200, 0),  # Yellow
            'brightness_down': (255, 100, 0),  # Orange
            'swipe_left': (255, 0, 100),  # Pink
            'swipe_right': (200, 0, 255),  # Purple
            'pinch': (255, 50, 50),  # Red
            'rotate_clockwise': (150, 255, 150),  # Light Green
            'rotate_counterclockwise': (150, 150, 255),  # Light Blue
        }

@dataclass
class UISettings:
    primary_color: tuple = (0, 150, 255)  # Professional blue
    secondary_color: tuple = (0, 200, 200)  # Teal
    text_color: tuple = (240, 240, 240)  # Bright white
    accent_color: tuple = (255, 128, 0)  # Orange
    background_overlay: tuple = (0, 0, 0, 0.4)
    font_scale: float = 0.7
    thickness: int = 2
    show_grid: bool = True
    show_hexagons: bool = True
    show_glow: bool = True
    show_particles: bool = True
    show_data_vis: bool = True
    animation_settings: AnimationSettings = None
    color_scheme: ColorScheme = None

    def __post_init__(self):
        self.animation_settings = AnimationSettings()
        self.color_scheme = ColorScheme()

class Config:
    def __init__(self):
        self.gesture_thresholds = GestureThresholds()
        self.system_settings = SystemControlSettings()
        self.ui_settings = UISettings()


