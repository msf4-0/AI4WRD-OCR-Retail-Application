import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

import streamlit as st
from streamlit_option_menu import option_menu
import videoAppProcessing as vp

st.set_page_config(page_title = "AIP-OCR", page_icon = 'resources/shrdc-logo_no-bg.png')

# Setting the header for the page
st.title("AI Pharmaceutical OCR Reader")

# Adding images and headers to app
st.sidebar.image("resources/MSF-logo.gif")

#add navigation option menu
with st.sidebar:
    selected_page  = option_menu(
        menu_title= None,
        options = ["Home", "Live video OCR"],
    )

if selected_page == "Live video OCR":
    vp.mainfunc()
    
elif selected_page == "Home":
    
    st.write("Developed and integrated by the MSF4.0 team at Selangor Human Resource Development Centre (SHRDC)")
