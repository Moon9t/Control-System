# Gesture Control System

A computer vision-based system that allows users to control system volume, brightness, and media playback using hand gestures. Built with Python, OpenCV, and MediaPipe.

## Features

- **Real-time Hand Tracking**: Accurate hand landmark detection using MediaPipe
- **Gesture Recognition**: Supports multiple gestures:
  - Volume Control (Up/Down)
  - Brightness Control (Up/Down)
  - Media Playback (Play/Pause, Next/Previous Track)
  - Rotation Gestures for Fine Control
- **Visual Feedback**: 
  - Dynamic particle effects
  - Real-time data visualization
  - Animated grid and hexagon patterns
  - Color-coded gesture feedback
  - System status overlay

## Requirements

- Python 3.7+
- OpenCV
- MediaPipe
- NumPy
- pycaw (for audio control)
- screen_brightness_control
- pyautogui
- comtypes

## Installation

```bash
# Clone the repository
git clone [www.github.com/Moon9t/Control-System]  

# Install dependencies
pip install opencv-python mediapipe numpy pycaw screen-brightness-control pyautogui comtypes
```

## Usage

1. Run the main application:
```bash
python main.py
```

2. Supported Gestures:
- 🖐️ Swipe Left/Right: Previous/Next Track
- ☝️ Single Finger Up/Down: Brightness Control
- ✌️ Middle Finger Up/Down: Volume Control
- 👌 Pinch: Play/Pause
- 🔄 Rotate Hand: Fine Brightness Control

3. Press ESC to exit the application

## Configuration

Adjust settings in `config.py`:
- Gesture recognition thresholds
- System control sensitivity
- UI and animation settings
- Color schemes

## Project Structure

- `main.py`: Application entry point and main loop
- `hand_tracking.py`: Hand detection and landmark tracking
- `gesture_rec.py`: Gesture recognition algorithms
- `sys_control.py`: System control interface
- `ui_feedback.py`: Visual feedback and UI rendering
- `config.py`: Configuration settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[MIT License](LICENSE)

## Acknowledgments

- MediaPipe for hand tracking
- OpenCV for image processing
- Contributors and maintainers
