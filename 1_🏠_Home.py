import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
import os

# ---------- Page Configuration ----------
st.set_page_config(page_title="AI Fitness Trainer", page_icon="💪", layout="wide")

# ---------- Inject Internal CSS ----------
st.markdown("""
    <style>
    /* Contact form styling */
    input[type=message], input[type=email], input[type=text], textarea {
        width: 100%;
        padding: 12px;
        border: 1px solid #ccc;
        border-radius: 4px;
        box-sizing: border-box;
        margin-top: 6px;
        margin-bottom: 16px;
        resize: vertical;
    }
    button[type=submit] {
        background-color: #04AA6D;
        color: white;
        padding: 12px 20px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    button[type=submit]:hover {
        background-color: #1c42ca;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------- Utility Functions ----------
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except requests.exceptions.RequestException:
        return None

# ---------- Load Assets ----------
lottie_intro = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_FYx0Ph.json")
lottie_music = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ikk4jhps.json")
lottie_podcast = load_lottieurl("https://assets8.lottiefiles.com/packages/lf20_JjpNLdaKYX.json")

image_path = os.path.join("models", "images", "home.jpg")
img_home = Image.open(image_path) if os.path.exists(image_path) else None

# ---------- Header ----------
with st.container():
    st.subheader("Hello, welcome to our website 👋")
    st.title("AI Fitness Trainer")
    st.write("Step into a fitter future: Welcome to your fitness revolution!")

# ---------- About Us ----------
with st.container():
    st.write("---")
    st.header("About us 👇")

    left_col, right_col = st.columns(2)
    with left_col:
        st.write("""
        - We provide **personalized fitness assistance** wherever you are.
        - Much **cheaper than traditional gyms** and tailored to your goals.
        - Whether you're a **beginner** or **pro**, we help you **achieve results fast**.

        **Join us today** and revolutionize your fitness journey! 💪
        """)
    with right_col:
        if lottie_intro:
            st_lottie(lottie_intro, height=300, key="intro")
        else:
            st.warning("⚠️ Failed to load intro animation.")

# ---------- Music ----------
with st.container():
    st.write("---")
    st.header("Get fit, Jam on, Repeat 🎧")

    img_col, text_col = st.columns((1, 2))
    with img_col:
        if lottie_music:
            st_lottie(lottie_music, height=300, key="music")
        else:
            st.warning("⚠️ Music animation not available.")
    with text_col:
        st.subheader("Workout Music 🎵")
        st.write("Power up your workout with the ultimate music fuel!")
        st.markdown("[🎶 Listen on Spotify](https://open.spotify.com/playlist/6N0Vl77EzPm13GIOlEkoJn?si=9207b7744d094bd3)")

# ---------- Podcast ----------
with st.container():
    img_col, text_col = st.columns((1, 2))
    with img_col:
        if lottie_podcast:
            st_lottie(lottie_podcast, height=300, key="podcast")
        else:
            st.warning("⚠️ Podcast animation not available.")
    with text_col:
        st.subheader("Fitness Podcasts 🎙️")
        st.write("Take your workouts to the next level with our immersive fitness podcast!")
        st.markdown("[🎧 Listen on Spotify](https://open.spotify.com/playlist/09Ig7KfohF5WmU9RhbDBjs?si=jyZ79y3wQgezrEDHim0NvQ)")

# ---------- Contact ----------
with st.container():
    st.write("---")
    st.header("Get In Touch With Us! 📩")

    contact_form = """
    <form action="https://formsubmit.co/c722428e42528bf09a0c149f6b7d3909" method="POST">
        <input type="hidden" name="_captcha" value="false">
        <input type="text" name="name" placeholder="Your name" required>
        <input type="email" name="email" placeholder="Your email" required>
        <textarea name="message" placeholder="Your message here" required></textarea>
        <button type="submit">Send</button>
    </form>
    """

    left_col, right_col = st.columns(2)
    with left_col:
        st.markdown(contact_form, unsafe_allow_html=True)
    with right_col:
        st.write("📬 Reach out to us anytime. We’d love to hear from you!")

# ---------- Display Home Image ----------
if img_home:
    st.image(img_home, caption="Train at home with AI", use_column_width=True)
else:
    st.warning("⚠️ Image 'home.jpg' not found in 'models/images/'.")
