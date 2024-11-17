""" Streamlit UI for 'a helping hand' app. """

# Standard library imports
import base64

# Imports
import streamlit as st
from streamlit_webrtc import webrtc_streamer

IMG_PATH = r"C:\Users\emily\OneDrive\Desktop\a_helping_hand\images\space_background.jpg"

def set_background_image(image_path):
    """ Adds background space image."""

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
        }}
        <style>
        """,
        unsafe_allow_html=True
    )

set_background_image(IMG_PATH)

st.markdown(
    """
    <style>
    .stApp {
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("A Helping Hand")
st.write("""
Complete the exercises to earn points
""")

col1, col2 = st.columns([1,2])

with col1:
    st.markdown("### Score")
    st.markdown("## 0")

    st.markdown("### Next exercise")
    st.image("C:/Users/emily/OneDrive/Desktop/a_helping_hand/images/Thumb_Up.png")

with col2:
    st.markdown("### You!")
    webrtc_streamer(key="streamer", sendback_audio=False)
