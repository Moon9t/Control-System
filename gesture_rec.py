from typing import List, Tuple, Dict, Optional
import numpy as np
from config import GestureThresholds
import math

class GestureRecognizer:
    def __init__(self, thresholds: GestureThresholds):
        self.thresholds = thresholds
        self.gestures = {
            'pinch': self._detect_pinch,
            'swipe_left': self._detect_swipe_left,
            'swipe_right': self._detect_swipe_right,
            'volume_up': self._detect_volume_up,
            'volume_down': self._detect_volume_down,
            'brightness_up': self._detect_brightness_up,
            'brightness_down': self._detect_brightness_down,
            'rotate_clockwise': self._detect_rotation_clockwise,
            'rotate_counterclockwise': self._detect_rotation_counterclockwise
        }
        self.previous_coordinates = None
        self.gesture_cooldown = 0
        self.gesture_history = []
        self.min_gesture_confidence = 0.7
        
    def _calculate_confidence(self, value: float, threshold: float) -> float:
        """Calculate confidence score for a gesture based on how well it meets the threshold"""
        return min(1.0, value / threshold) if value > threshold else 0.0

    def recognize_gesture(self, coordinates: List[Tuple[int, int]]) -> Optional[str]:
        try:
            if not coordinates or self.gesture_cooldown > 0:
                self.gesture_cooldown = max(0, self.gesture_cooldown - 1)
                return None

            # Calculate confidence for each gesture
            gesture_confidences = {}
            for gesture_name, detect_func in self.gestures.items():
                confidence = detect_func(coordinates)
                if confidence > self.min_gesture_confidence:
                    gesture_confidences[gesture_name] = confidence

            # Update gesture history
            if gesture_confidences:
                self.gesture_history.append(max(gesture_confidences.items(), key=lambda x: x[1]))
            if len(self.gesture_history) > 3:
                self.gesture_history.pop(0)

            self.previous_coordinates = coordinates
            
            # Return most confident gesture with temporal smoothing
            if gesture_confidences and len(self.gesture_history) >= 2:
                most_common = max(set(g for g, _ in self.gesture_history), 
                                key=lambda g: sum(1 for x, _ in self.gesture_history if x == g))
                self.gesture_cooldown = 8  # Reduced cooldown for more responsive controls
                return most_common
            return None

        except Exception as e:
            print(f"Error in gesture recognition: {str(e)}")
            return None

    def _calculate_angle(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        return math.degrees(math.atan2(p2[1] - p1[1], p2[0] - p1[0]))

    def _detect_rotation_clockwise(self, coordinates: List[Tuple[int, int]]) -> float:
        try:
            if self.previous_coordinates is None:
                return 0.0

            prev_angle = self._calculate_angle(
                self.previous_coordinates[0],
                self.previous_coordinates[8]
            )
            current_angle = self._calculate_angle(
                coordinates[0],
                coordinates[8]
            )
            
            angle_diff = (current_angle - prev_angle) % 360
            return self._calculate_confidence(angle_diff, self.thresholds.rotation_angle)
        except Exception:
            return 0.0

    def _detect_rotation_counterclockwise(self, coordinates: List[Tuple[int, int]]) -> float:
        try:
            if self.previous_coordinates is None:
                return 0.0

            prev_angle = self._calculate_angle(
                self.previous_coordinates[0],
                self.previous_coordinates[8]
            )
            current_angle = self._calculate_angle(
                coordinates[0],
                coordinates[8]
            )
            
            angle_diff = (prev_angle - current_angle) % 360
            return self._calculate_confidence(angle_diff, self.thresholds.rotation_angle)
        except Exception:
            return 0.0

    def _detect_pinch(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            thumb_tip = coordinates[4]
            index_tip = coordinates[8]
            middle_tip = coordinates[12]
            ring_tip = coordinates[16]
            pinky_tip = coordinates[20]
            palm_center = coordinates[0]
            
            # Calculate pinch distance
            pinch_distance = np.sqrt(
                (thumb_tip[0] - index_tip[0])**2 + 
                (thumb_tip[1] - index_tip[1])**2
            )
            
            # Check if other fingers are folded (closer to palm)
            others_folded = (
                middle_tip[1] > palm_center[1] and
                ring_tip[1] > palm_center[1] and
                pinky_tip[1] > palm_center[1]
            )
            
            return pinch_distance < self.thresholds.pinch_distance and others_folded
        except Exception:
            return False

    def _detect_swipe_left(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            if self.previous_coordinates is None:
                return False
            
            palm_center = coordinates[0]
            prev_palm_center = self.previous_coordinates[0]
            
            # Check if hand is open by verifying finger spread
            fingers_spread = self._check_fingers_spread(coordinates)
            
            horizontal_movement = palm_center[0] - prev_palm_center[0]
            return horizontal_movement < -self.thresholds.swipe_distance and fingers_spread
        except Exception:
            return False

    def _detect_swipe_right(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            if self.previous_coordinates is None:
                return False
            
            palm_center = coordinates[0]
            prev_palm_center = self.previous_coordinates[0]
            
            # Check if hand is open by verifying finger spread
            fingers_spread = self._check_fingers_spread(coordinates)
            
            horizontal_movement = palm_center[0] - prev_palm_center[0]
            return horizontal_movement > self.thresholds.swipe_distance and fingers_spread
        except Exception:
            return False

    def _check_fingers_spread(self, coordinates: List[Tuple[int, int]]) -> bool:
        """Helper method to check if fingers are spread (open hand)"""
        try:
            palm_center = coordinates[0]
            finger_tips = [coordinates[i] for i in [8, 12, 16, 20]]  # Index to pinky tips
            
            # Check if all fingers are raised above palm
            all_raised = all(tip[1] < palm_center[1] for tip in finger_tips)
            
            # Check if fingers have horizontal spacing
            finger_x_coords = [tip[0] for tip in finger_tips]
            min_spacing = 10  # Minimum pixel spacing between fingers
            properly_spaced = all(finger_x_coords[i] - finger_x_coords[i-1] > min_spacing 
                                for i in range(1, len(finger_x_coords)))
            
            return all_raised and properly_spaced
        except Exception:
            return False

    def _detect_volume_up(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            palm_center = coordinates[0]
            middle_finger_tip = coordinates[12]
            middle_finger_base = coordinates[9]
            index_tip = coordinates[8]
            ring_tip = coordinates[16]
            
            # Check if middle finger is raised and others are lower
            middle_raised = middle_finger_tip[1] < palm_center[1] - self.thresholds.vertical_gesture_distance
            index_lower = index_tip[1] > middle_finger_base[1]
            ring_lower = ring_tip[1] > middle_finger_base[1]
            
            return middle_raised and index_lower and ring_lower
        except Exception:
            return False

    def _detect_volume_down(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            palm_center = coordinates[0]
            middle_finger_tip = coordinates[12]
            middle_finger_base = coordinates[9]
            index_tip = coordinates[8]
            ring_tip = coordinates[16]
            
            # Check if middle finger is lowered and others are higher
            middle_lowered = middle_finger_tip[1] > palm_center[1] + self.thresholds.vertical_gesture_distance
            index_higher = index_tip[1] < middle_finger_tip[1]
            ring_higher = ring_tip[1] < middle_finger_tip[1]
            
            return middle_lowered and index_higher and ring_higher
        except Exception:
            return False

    def _detect_brightness_up(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            palm_center = coordinates[0]
            index_tip = coordinates[8]
            index_base = coordinates[5]
            middle_tip = coordinates[12]
            
            # Check if index finger is raised on right side and others are lower
            index_raised = index_tip[1] < palm_center[1] - self.thresholds.vertical_gesture_distance
            on_right_side = index_tip[0] > palm_center[0]
            middle_lower = middle_tip[1] > index_base[1]
            
            return index_raised and on_right_side and middle_lower
        except Exception:
            return False

    def _detect_brightness_down(self, coordinates: List[Tuple[int, int]]) -> bool:
        try:
            palm_center = coordinates[0]
            index_tip = coordinates[8]
            index_base = coordinates[5]
            middle_tip = coordinates[12]
            
            # Check if index finger is lowered on right side and others are higher
            index_lowered = index_tip[1] > palm_center[1] + self.thresholds.vertical_gesture_distance
            on_right_side = index_tip[0] > palm_center[0]
            middle_higher = middle_tip[1] < index_tip[1]
            
            return index_lowered and on_right_side and middle_higher
        except Exception:
            return False




