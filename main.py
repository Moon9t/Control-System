import cv2
import numpy as np
from hand_tracking import HandTracker
from gesture_rec import GestureRecognizer
from sys_control import SystemController
from ui_feedback import UIFeedback
from config import Config
from typing import Optional

class GestureControlApp:
    def __init__(self):
        self.config = Config()
        self.config.ui_settings.show_particles = True  # Enable particle effects
        self.config.ui_settings.show_data_vis = True   # Enable data visualization
        self.hand_tracker = HandTracker()
        self.gesture_recognizer = GestureRecognizer(self.config.gesture_thresholds)
        self.system_controller = SystemController(self.config.system_settings)
        self.ui_feedback = UIFeedback(self.config.ui_settings)
        self.cap = None
        self.window_name = 'Gesture Control'

    def initialize_camera(self, camera_id: int = 0) -> bool:
        try:
            self.cap = cv2.VideoCapture(camera_id)
            if not self.cap.isOpened():
                raise Exception("Failed to open camera")
            
            # Set camera resolution to maximum supported
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            
            # Create fullscreen window
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            return True
        except Exception as e:
            print(f"Error initializing camera: {str(e)}")
            return False

    def handle_gesture(self, gesture: str):
        volume, brightness = self.system_controller.get_system_status()
        
        if gesture == 'volume_up' and volume is not None:
            self.system_controller.adjust_volume(volume + self.config.system_settings.volume_step)
        elif gesture == 'volume_down' and volume is not None:
            self.system_controller.adjust_volume(volume - self.config.system_settings.volume_step)
        elif gesture == 'brightness_up' and brightness is not None:
            self.system_controller.adjust_brightness(brightness + self.config.system_settings.brightness_step)
        elif gesture == 'brightness_down' and brightness is not None:
            self.system_controller.adjust_brightness(brightness - self.config.system_settings.brightness_step)
        elif gesture == 'swipe_left':
            self.system_controller.media_control('prev_track')
        elif gesture == 'swipe_right':
            self.system_controller.media_control('next_track')
        elif gesture == 'pinch':
            self.system_controller.media_control('play_pause')
        elif gesture == 'rotate_clockwise':
            self.system_controller.adjust_brightness(brightness + self.config.system_settings.brightness_step * 2)
        elif gesture == 'rotate_counterclockwise':
            self.system_controller.adjust_brightness(brightness - self.config.system_settings.brightness_step * 2)

    def run(self):
        if not self.initialize_camera():
            return

        try:
            while True:
                success, frame = self.cap.read()
                if not success:
                    print("Failed to read frame from camera")
                    break

                # Flip frame horizontally for more intuitive interaction
                frame = cv2.flip(frame, 1)

                # Process hand tracking
                frame, landmarks = self.hand_tracker.find_hands(frame)
                
                if landmarks:
                    coordinates = self.hand_tracker.get_landmark_coordinates(frame, landmarks[0])
                    gesture = self.gesture_recognizer.recognize_gesture(coordinates)
                    
                    if gesture:
                        self.handle_gesture(gesture)

                    # Update UI
                    volume, brightness = self.system_controller.get_system_status()
                    self.ui_feedback.draw_system_status(frame, gesture, volume, brightness)

                # Scale frame to fit screen while maintaining aspect ratio
                screen_h, screen_w = cv2.getWindowImageRect(self.window_name)[2:]
                frame_h, frame_w = frame.shape[:2]
                scale = min(screen_w/frame_w, screen_h/frame_h)
                frame = cv2.resize(frame, None, fx=scale, fy=scale)

                cv2.imshow(self.window_name, frame)
                if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
                    break

        except Exception as e:
            print(f"Error in main loop: {str(e)}")
        finally:
            if self.cap is not None:
                self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    app = GestureControlApp()
    app.run()


