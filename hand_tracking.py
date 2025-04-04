import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, List, Optional

class HandTracker:
    def __init__(self, max_hands: int = 2, detection_confidence: float = 0.5, tracking_confidence: float = 0.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def find_hands(self, frame: np.ndarray, draw: bool = True) -> Tuple[np.ndarray, List]:
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.results = self.hands.process(frame_rgb)
            landmarks = []

            if self.results.multi_hand_landmarks:
                for hand_landmarks in self.results.multi_hand_landmarks:
                    if draw:
                        self.mp_draw.draw_landmarks(
                            frame, 
                            hand_landmarks, 
                            self.mp_hands.HAND_CONNECTIONS
                        )
                    landmarks.append(hand_landmarks)
            
            return frame, landmarks
        except Exception as e:
            print(f"Error in hand detection: {str(e)}")
            return frame, []

    def get_landmark_coordinates(self, frame: np.ndarray, hand_landmarks) -> List[Tuple[int, int]]:
        try:
            h, w, _ = frame.shape
            coordinates = []
            for landmark in hand_landmarks.landmark:
                cx, cy = int(landmark.x * w), int(landmark.y * h)
                coordinates.append((cx, cy))
            return coordinates
        except Exception as e:
            print(f"Error getting landmark coordinates: {str(e)}")
            return []