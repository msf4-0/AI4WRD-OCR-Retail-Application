import streamlit as st
import multiappclass as mtc
import medicine_ocr_reading,others

# #main function to run the apps
def mainfunc():
    # create a class object for the multiapp
    lvlapp = mtc.MultiApp()

    #add pages to the menu
    lvlapp.add_app("Medicine OCR Reading", medicine_ocr_reading.mainApp)
    lvlapp.add_app("Others", others.mainApp)
    
    lvlapp.run()