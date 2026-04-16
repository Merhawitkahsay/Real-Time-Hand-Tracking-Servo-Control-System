# IMPORT REQUIRED LIBRARIES

import cv2                 # OpenCV: image processing and camera handling
import mediapipe as mp    # MediaPipe: hand tracking
import serial             # Serial: communication with Arduino
import time               # Time: delays and timing control


# SERIAL COMMUNICATION SETUP

arduino = serial.Serial('COM4', 9600)  # Connect to Arduino
time.sleep(2)                          # Wait for connection to stabilize


# MEDIAPIPE HAND TRACKING SETUP

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils


# FUNCTION: COUNT RAISED FINGERS

def count_fingers(hand_landmarks):
    """
    Counts how many fingers are raised.

    Logic:
    - Compares fingertip with lower joint
    - If tip is higher → finger is raised
    """

    tips = [8, 12, 16, 20]  # Finger tip indices
    count = 0

    for tip in tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1

    return count


# CAMERA INITIALIZATION

cap = cv2.VideoCapture(0)


# SYSTEM STATE VARIABLES

active = False

# Gesture smoothing variables
gesture_history = []       # Stores last detected gestures
history_length = 5         # Number of frames to stabilize


# MAIN LOOP

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    h, w, _ = img.shape

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    command_text = "NO HAND"


    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:

            # Draw landmarks
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            # Count fingers
            finger_count = count_fingers(handLms)

            # Add to history
            gesture_history.append(finger_count)

            # Keep only last N frames
            if len(gesture_history) > history_length:
                gesture_history.pop(0)

            # Get stable gesture (average)
            stable_gesture = round(sum(gesture_history) / len(gesture_history))


            # GESTURE CONTROL LOGIC

            if stable_gesture >= 3:
                active = True

            elif stable_gesture == 2:
                # HOME RESET
                arduino.write(b"HOME\n")
                command_text = "HOME RESET"
                active = False

            else:
                active = False


            # HAND POSITION TRACKING

            lm = handLms.landmark[9]
            cx, cy = int(lm.x * w), int(lm.y * h)

            cv2.circle(img, (cx, cy), 10, (255, 0, 0), -1)


            # SERVO CONTROL

            if active:
                base_angle = int((cx / w) * 180)
                arm_angle = int((cy / h) * 180)

                data = f"{base_angle},{arm_angle}\n"
                arduino.write(data.encode())

                command_text = f"ACTIVE: {base_angle}, {arm_angle}"

            else:
                arduino.write(b"STOP\n")
                command_text = "STOPPED"


    else:
        # SAFETY: No hand detected
        arduino.write(b"STOP\n")
        command_text = "NO HAND (SAFE STOP)"

        # Reset gesture history to avoid false triggers
        gesture_history.clear()


    # DISPLAY TEXT

    cv2.putText(img, command_text, (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)


    # SHOW VIDEO

    cv2.imshow("Hand Servo Control", img)


    # EXIT CONDITION (ESC key)

    if cv2.waitKey(1) == 27:
        break


# CLEANUP

cap.release()
cv2.destroyAllWindows()