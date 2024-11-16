from streamlit_webrtc import webrtc_streamer
import streamlit as st
import pandas as pd

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