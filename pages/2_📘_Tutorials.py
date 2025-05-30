import streamlit as st
import requests
from streamlit_lottie import st_lottie
from PIL import Image

# -------------------------------
# Function to load Lottie animation
# -------------------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# -------------------------------
# Load Lottie animation
# -------------------------------
lottie_workout = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_M9p23l.json")

# -------------------------------
# Load images for exercises
# -------------------------------
images = {
    "Bicep Curls": Image.open("./images/dumbbell.webp"),
    "Squats": Image.open("./images/squats.jpg"),
    "Pushups": Image.open("./images/pushups.jpeg"),
    "Shoulder Press": Image.open("./images/shoulder.jpeg"),
}

# -------------------------------
# Load exercise GIFs
# -------------------------------
exercise_gifs = {
    "Bicep Curls": "./gif/bicep.gif",
    "Squats": "./gif/squats.gif",
    "Pushups": "./gif/pushups.gif",
    "Shoulder Press": "./gif/shoulder.gif",
}

# -------------------------------
# Exercise steps
# -------------------------------
exercise_steps = {
    "Bicep Curls": [
        "Stand up straight with a dumbbell in each hand.",
        "Keep elbows close to the torso and rotate palms forward.",
        "Curl the weights up while contracting your biceps.",
        "Pause at the top, then slowly lower back to starting position.",
        "Repeat for desired reps.",
    ],
    "Squats": [
        "Stand with feet slightly wider than shoulder-width apart.",
        "Engage core and keep back straight.",
        "Bend knees and push hips back as if sitting into a chair.",
        "Lower until thighs are parallel to the ground.",
        "Push through heels to return to standing position.",
    ],
    "Pushups": [
        "Start in a high plank position.",
        "Lower your chest to the ground, keeping elbows close.",
        "Push back up to the starting position.",
        "Keep core engaged throughout the movement.",
        "Modify by dropping to knees if needed.",
    ],
    "Shoulder Press": [
        "Stand with feet shoulder-width apart, holding dumbbells at shoulders.",
        "Press weights overhead until arms are fully extended.",
        "Pause at the top, then lower back to the start.",
        "Keep head and neck stationary.",
        "Maintain controlled movements throughout.",
    ],
}

# -------------------------------
# Sidebar Navigation
# -------------------------------
st.sidebar.title("Fitness Tutorials 🏋️‍♂️")
app_mode = st.sidebar.radio("Choose an Exercise", ["About", "Bicep Curls", "Squats", "Pushups", "Shoulder Press"])

# -------------------------------
# Main Page Title
# -------------------------------
st.markdown(
    """
    <div style="background-color:#025246;padding:10px;border-radius:10px;">
    <h2 style="color:white;text-align:center;">Fitness Tutorial Hub</h2>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# About Section
# -------------------------------
if app_mode == "About":
    st.write("---")
    st.header("Welcome to Your Workout Guide!")
    st.write("Watch video tutorials and follow step-by-step guides to perfect your form.")

    if lottie_workout:
        st_lottie(lottie_workout, height=250, key="workout")

    # Display exercise tutorials
    exercises = {
        "Bicep Curls": (
            "Get armed with knowledge! Watch this bicep curl tutorial and unlock the secret to sleeve-busting strength!",
            "https://youtu.be/ykJmrZ5v0Oo"
        ),
        "Squats": (
            "Get lower, get stronger! Dive into this squat tutorial and unlock the power of a rock-solid foundation!",
            "https://youtu.be/YaXPRqUwItQ"
        ),
        "Pushups": (
            "Push your limits, pump up your power! Join us for this push-up tutorial and unleash your inner strength!",
            "https://youtu.be/IODxDxX7oi4"
        ),
        "Shoulder Press": (
            "Elevate your strength, shoulder to shoulder! Don't miss this shoulder press tutorial to reach new heights of power!",
            "https://youtu.be/qEwKCR5JCog"
        ),
    }

    for name, (desc, link) in exercises.items():
        with st.container():
            image_col, text_col = st.columns((1, 2))
            with image_col:
                st.image(images.get(name, None), width=300)
            with text_col:
                st.subheader(name)
                st.write(desc)
                st.markdown(f"[Watch Video ▶]({link})")

# -------------------------------
# Exercise Tutorial Pages
# -------------------------------
else:
    exercise_name = app_mode
    st.markdown(f"## {exercise_name}")
    st.write("Follow these steps to perfect your form:")

    col1, col2 = st.columns((2, 1))

    with col1:
        st.write("### Steps:")
        for step in exercise_steps.get(exercise_name, []):
            st.write(f"✅ {step}")

    with col2:
        gif_path = exercise_gifs.get(exercise_name)
        if gif_path:
            st.image(gif_path)
        else:
            st.warning("GIF not found for this exercise.")

# -------------------------------
# Sidebar Footer
# -------------------------------
st.sidebar.write("---")
st.sidebar.info("Designed for fitness enthusiasts to learn and improve form! 💪")