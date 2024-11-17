from streamlit_webrtc import webrtc_streamer
import streamlit as st
import pandas as pd
import base64

image_path = r"C:\Users\emily\OneDrive\Desktop\a_helping_hand\space_background.jpg"

def set_background_image(image_path):
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

set_background_image(image_path)

st.title("A Helping Hand")
 
st.write("""
Complete the exercises to earn points
""")

col1, col2 = st.columns([1,2])

with col1:
    st.markdown("### Score")
    st.info("Display score here")

    st.markdown("Next exercise")
    st.info("Exercise here")

with col2:
    st.markdown("### You!")
    st.info("Participant Box")
    webrtc_streamer(key="streamer", sendback_audio=False)