import cv2
import numpy as np
from typing import Optional, Tuple, List
from config import UISettings
import time
import math

class Particle:
    def __init__(self, pos, velocity, color, lifetime):
        self.pos = np.array(pos, dtype=float)
        self.velocity = np.array(velocity, dtype=float)
        self.color = color
        self.lifetime = lifetime
        self.age = 0
        
class UIFeedback:
    def __init__(self, settings: UISettings):
        self.settings = settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.particles: List[Particle] = []
        self.hex_rotation = 0
        self.current_color = self.settings.color_scheme.base['default']
        self.target_color = self.current_color
        self.data_points = []  # For real-time data visualization
        self.last_frame_time = time.time()
        
    def _update_timing(self):
        current_time = time.time()
        dt = current_time - self.last_frame_time
        self.last_frame_time = current_time
        return dt

    def draw_system_status(self, frame: np.ndarray, 
                          gesture: Optional[str],
                          volume: Optional[float],
                          brightness: Optional[float]):
        try:
            dt = self._update_timing()
            
            # Update color based on gesture
            if gesture:
                self.target_color = self.settings.color_scheme.base.get(
                    gesture, self.settings.color_scheme.base['default'])
            
            # Smooth color transition
            self.current_color = tuple(map(lambda x, y: int(x + (y - x) * 0.1),
                                         self.current_color, self.target_color))
            
            # Draw background elements
            self._draw_animated_grid(frame, dt)
            self._draw_animated_hexagons(frame, dt)
            
            # Update and draw particles
            if self.settings.show_particles:
                self._update_particles(dt)
                self._draw_particles(frame)
            
            # Create overlay for UI elements
            overlay = frame.copy()
            
            # Draw UI elements
            self._draw_gesture_info(overlay, gesture)
            self._draw_volume_control(overlay, volume)
            self._draw_brightness_control(overlay, brightness)
            self._draw_help_overlay(overlay)
            
            # Draw data visualization
            if self.settings.show_data_vis:
                self._update_data_visualization(volume, brightness)
                self._draw_data_visualization(overlay)
            
            # Apply overlay with transparency
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
            
            # Add glow effect
            if self.settings.show_glow:
                self._add_glow_effect(frame)
            
            # Add gesture-triggered particles
            if gesture and self.settings.show_particles:
                self._add_gesture_particles(frame, gesture)
                
        except Exception as e:
            print(f"Error drawing UI feedback: {str(e)}")

    def _draw_animated_grid(self, frame: np.ndarray, dt: float):
        h, w = frame.shape[:2]
        time_offset = time.time() * 0.5
        
        # Animated vertical lines
        for x in range(0, w, 50):
            offset = math.sin(time_offset + x * 0.01) * 5
            alpha = 0.3 - (abs(w//2 - x) / w)
            if alpha > 0:
                color = tuple(map(lambda x: int(x * alpha), self.current_color))
                cv2.line(frame, 
                        (int(x + offset), 0), 
                        (int(x - offset), h),
                        color, 1, 
                        lineType=cv2.LINE_AA)
        
        # Animated horizontal lines
        for y in range(0, h, 50):
            offset = math.cos(time_offset + y * 0.01) * 5
            alpha = 0.3 - (abs(h//2 - y) / h)
            if alpha > 0:
                color = tuple(map(lambda x: int(x * alpha), self.current_color))
                cv2.line(frame, 
                        (0, int(y + offset)), 
                        (w, int(y - offset)),
                        color, 1, 
                        lineType=cv2.LINE_AA)

    def _draw_animated_hexagons(self, frame: np.ndarray, dt: float):
        h, w = frame.shape[:2]
        self.hex_rotation += self.settings.animation_settings.hex_rotation_speed * dt
        
        centers = [(50, 50), (w-50, 50), (50, h-50), (w-50, h-50)]
        radius = 30
        
        for center in centers:
            points = []
            for i in range(6):
                angle = self.hex_rotation + i * (2 * np.pi / 6)
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                points.append([int(x), int(y)])
            
            points = np.array(points)
            cv2.polylines(frame, [points], True, 
                         self.current_color, 2, 
                         lineType=cv2.LINE_AA)
            
            # Inner hexagon
            points_inner = np.array([[center[0] + (radius*0.7) * np.cos(angle + self.hex_rotation),
                                    center[1] + (radius*0.7) * np.sin(angle + self.hex_rotation)]
                                   for angle in np.linspace(0, 2*np.pi, 7)[:-1]], np.int32)
            cv2.polylines(frame, [points_inner], True, 
                         self.current_color, 1, 
                         lineType=cv2.LINE_AA)

    def _update_particles(self, dt: float):
        # Update existing particles
        self.particles = [p for p in self.particles if p.age < p.lifetime]
        for particle in self.particles:
            particle.pos += particle.velocity * dt * 60
            particle.age += 1
            
    def _draw_particles(self, frame: np.ndarray):
        for particle in self.particles:
            alpha = 1 - (particle.age / particle.lifetime)
            color = tuple(map(lambda x: int(x * alpha), particle.color))
            pos = tuple(map(int, particle.pos))
            cv2.circle(frame, pos, 
                      self.settings.animation_settings.particle_size,
                      color, -1)

    def _add_gesture_particles(self, frame: np.ndarray, gesture: str):
        h, w = frame.shape[:2]
        color = self.settings.color_scheme.base[gesture]
        
        for _ in range(10):  # Add burst of particles
            angle = np.random.uniform(0, 2*np.pi)
            speed = np.random.uniform(1, self.settings.animation_settings.particle_max_speed)
            velocity = np.array([np.cos(angle), np.sin(angle)]) * speed
            
            particle = Particle(
                pos=(w//2, h//2),
                velocity=velocity,
                color=color,
                lifetime=self.settings.animation_settings.particle_lifetime
            )
            self.particles.append(particle)

    def _update_data_visualization(self, volume: Optional[float], brightness: Optional[float]):
        if volume is not None and brightness is not None:
            self.data_points.append((volume, brightness))
            if len(self.data_points) > 100:  # Keep last 100 points
                self.data_points.pop(0)

    def _draw_data_visualization(self, frame: np.ndarray):
        if not self.data_points:
            return
            
        h, w = frame.shape[:2]
        graph_w, graph_h = 200, 100
        graph_x, graph_y = w - graph_w - 20, h - graph_h - 20
        
        # Draw graph background
        cv2.rectangle(frame, 
                     (graph_x, graph_y), 
                     (graph_x + graph_w, graph_y + graph_h),
                     (0, 0, 0), -1)
        cv2.rectangle(frame, 
                     (graph_x, graph_y), 
                     (graph_x + graph_w, graph_y + graph_h),
                     self.current_color, 1)
        
        # Draw data points
        points = []
        for i, (vol, _) in enumerate(self.data_points):
            x = graph_x + (i * graph_w // 100)
            y = graph_y + graph_h - int(vol * graph_h)
            points.append((x, y))
            
        if len(points) > 1:
            cv2.polylines(frame, [np.array(points)], False, 
                         self.current_color, 1, 
                         lineType=cv2.LINE_AA)

    def _add_glow_effect(self, frame: np.ndarray):
        blur = cv2.GaussianBlur(frame, (21, 21), 0)
        frame[:] = cv2.addWeighted(frame, 1.2, blur, -0.2, 0)

    def _draw_gesture_info(self, frame: np.ndarray, gesture: Optional[str]):
        gesture_text = f"GESTURE DETECTED: {gesture.upper() if gesture else 'NONE'}"
        # Draw text background
        text_size = cv2.getTextSize(gesture_text, self.font, 
                                  self.settings.font_scale, 
                                  self.settings.thickness)[0]
        cv2.rectangle(frame, (10, 10), 
                     (text_size[0] + 20, 45), 
                     (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), 
                     (text_size[0] + 20, 45), 
                     self.settings.primary_color, 1)
        
        # Draw text
        cv2.putText(frame, gesture_text, (15, 35), 
                    self.font, self.settings.font_scale,
                    self.settings.primary_color if gesture else self.settings.text_color,
                    self.settings.thickness)

    def _draw_volume_control(self, frame: np.ndarray, volume: Optional[float]):
        if volume is not None:
            # Draw modern volume bar
            bar_height = int(120 * volume)
            # Background
            cv2.rectangle(frame, (50, 150), (85, 400), 
                         (0, 0, 0), -1)
            cv2.rectangle(frame, (50, 150), (85, 400), 
                         self.settings.primary_color, 1)
            # Fill
            cv2.rectangle(frame, (50, 400 - bar_height), 
                         (85, 400), self.settings.primary_color, -1)
            
            # Volume text with background
            text = f"VOL {int(volume * 100)}%"
            cv2.rectangle(frame, (40, 420), (95, 450), 
                         (0, 0, 0), -1)
            cv2.putText(frame, text, (45, 440), 
                       self.font, 0.5, self.settings.text_color, 1)

    def _draw_brightness_control(self, frame: np.ndarray, brightness: Optional[float]):
        if brightness is not None:
            # Draw modern horizontal brightness bar
            bar_width = int(120 * brightness)
            # Background
            cv2.rectangle(frame, (150, 50), (400, 85), 
                         (0, 0, 0), -1)
            cv2.rectangle(frame, (150, 50), (400, 85), 
                         self.settings.secondary_color, 1)
            # Fill
            cv2.rectangle(frame, (150, 50), 
                         (150 + bar_width, 85), 
                         self.settings.secondary_color, -1)
            
            # Brightness text with background
            text = f"BRT {int(brightness * 100)}%"
            cv2.rectangle(frame, (150, 90), (220, 120), 
                         (0, 0, 0), -1)
            cv2.putText(frame, text, (155, 110), 
                       self.font, 0.5, self.settings.text_color, 1)

    def _draw_help_overlay(self, frame: np.ndarray):
        help_text = [
            "SYSTEM CONTROLS",
            "↑/↓ Hand - Volume",
            "←/→ Swipe - Track",
            "Pinch - Play/Pause",
            "Rotate - Brightness",
            "ESC - Exit"
        ]
        
        # Draw help panel background
        h, w = frame.shape[:2]
        panel_width = 200
        cv2.rectangle(frame, 
                     (w - panel_width - 10, 130), 
                     (w - 10, 320), 
                     (0, 0, 0), -1)
        cv2.rectangle(frame, 
                     (w - panel_width - 10, 130), 
                     (w - 10, 320), 
                     self.settings.secondary_color, 1)
        
        # Draw help text
        y_offset = 160
        for i, text in enumerate(help_text):
            color = self.settings.secondary_color if i == 0 else self.settings.text_color
            cv2.putText(frame, text,
                       (w - panel_width, y_offset + i * 30),
                       self.font, 0.5, color, 1)



