import os
import datetime
import cv2
import streamlit as st
import mediapipe as mp
import numpy as np
from PIL import Image
from playsound import playsound

# ---------- Utility Functions ----------
def calculate_angle(a, b, c):
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle

def count_time(time_interval):
    now = datetime.datetime.now()
    current_second = int(now.strftime("%S"))
    if current_second != st.session_state.last_second:
        st.session_state.last_second = current_second
        st.session_state.counter += 1
        if st.session_state.counter == time_interval + 1:
            st.session_state.counter = 0
            st.session_state.pose_number += 1
            playsound(os.path.join("bell.wav"))
            if st.session_state.pose_number > 3:
                st.session_state.pose_number = 1
    return st.session_state.counter, st.session_state.pose_number

def initialize_session_state():
    defaults = {
        "last_second": 0,
        "counter": 0,
        "pose_number": 1,
        "tracking": False
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def safe_load_image(path):
    return Image.open(path) if os.path.exists(path) else None

# ---------- Initialize Session State ----------
initialize_session_state()

# ---------- Load Images ----------
yoga_gif = safe_load_image("./gif/yoga.gif")

track1_images = [
    safe_load_image("./images/pranamasana2.png"),
    safe_load_image("./images/Eka_Pada_Pranamasana.png"),
    safe_load_image("./images/Ashwa_Sanchalanasana.webp"),
]

track2_images = [
    safe_load_image("./images/ardha_chakrasana.webp"),
    safe_load_image("./images/Utkatasana.png"),
    safe_load_image("./images/Veerabhadrasan_2.png"),
]

# ---------- Mediapipe Setup ----------
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# ---------- Streamlit UI ----------
st.sidebar.title("🏃 Yoga Pose Tracker")
app_mode = st.sidebar.selectbox("Choose the Mode", ["About", "Track 1", "Track 2"])
st.title("🧘‍♂️ Yoga Pose Training and Guidance")

if app_mode == "About":
    if yoga_gif:
        st.image(yoga_gif, width=400)
    else:
        st.warning("Yoga GIF not found at './gif/yoga.gif'")

    st.subheader("Instructions:")
    st.markdown("""
    - Ensure good lighting and space.
    - Provide webcam access.
    - Stand where your body is visible.
    - Follow pose images and guidance.
    """)

else:
    st.markdown(f"### {app_mode} - Pose Instructions")

    poses_info = {
        "Track 1": [
            ("Pranamasana", "Stand straight, bring palms together."),
            ("Eka Pada Pranamasana", "Balance on one leg."),
            ("Ashwa Sanchalanasana", "Step back into a lunge."),
        ],
        "Track 2": [
            ("Ardha Chakrasana", "Bend backwards with raised arms."),
            ("Utkatasana", "Sit into a squat with arms raised."),
            ("Veerabhadrasana 2", "Extend arms and bend one knee."),
        ]
    }

    images = track1_images if app_mode == "Track 1" else track2_images

    for i, (pose_name, description) in enumerate(poses_info[app_mode]):
        st.subheader(f"🧝 {pose_name}")
        if images[i]:
            st.image(images[i], width=300)
        else:
            st.warning(f"Image not found for: {pose_name}")
        st.write(description)
        st.markdown("---")

    col1, col2 = st.columns(2)
    if col1.button("▶️ Start Tracking"):
        st.session_state.tracking = True
    if col2.button("⏹ Stop Tracking"):
        st.session_state.tracking = False

    if st.session_state.tracking:
        st.success("Tracking is active. Make sure your webcam is on.")
        FRAME_WINDOW = st.empty()
        cap = cv2.VideoCapture(0)

        while st.session_state.tracking:
            ret, frame = cap.read()
            if not ret:
                st.error("Could not access webcam.")
                break

            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            image = cv2.resize(image, (800, 600))

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                                 landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                                  landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
                left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x,
                            landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
                right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,
                             landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]

                left_angle = calculate_angle(left_shoulder, left_hip, [0, 1])
                right_angle = calculate_angle(right_shoulder, right_hip, [0, 1])

                if left_angle > 100 and right_angle > 100:
                    cv2.putText(image, "Pose: Correct", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
                    count, pose_num = count_time(5)
                    cv2.putText(image, f"Time: {count}s", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
                else:
                    cv2.putText(image, "Pose: Incorrect", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    st.session_state.counter = 0

            FRAME_WINDOW.image(image, channels="BGR")

        cap.release()
        st.session_state.tracking = False
        st.success("Tracking stopped.")
