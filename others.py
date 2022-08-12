import threading
from turtle import width
import PIL
import cv2
from cv2 import mulTransposed
import streamlit as st
import numpy as np
from PIL import Image
import PIL
from streamlit_webrtc import webrtc_streamer,VideoHTMLAttributes
import av
import cv2
import imutils
import pytesseract
from  pytesseract import Output


def stm_print_text(some_text):
    st.write(some_text)

def mainApp():

    muted = st.checkbox("Mute")

    st.title("OpenCV Live video enhancement App")
    
    brightness_amount = st.sidebar.slider("Brightness", min_value=-100, max_value=100, value=0)

    rotation_amount = st.sidebar.slider("Rotation", min_value=0, max_value=360, value=0)

    enhance = st.checkbox("Enhance")

    # output = "Your Output: "

    # st.write(output)

    def video_frame_callback(frame):

        img = frame.to_ndarray(format="bgr24")

        img = cv2.convertScaleAbs(img, beta=brightness_amount)

        img = imutils.rotate(img,rotation_amount)

        if enhance == True:
            img = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)

        #convert the format to rgb for tesseract
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        #test code to create the cropping function
        ocr_output = pytesseract.image_to_data(img, output_type=Output.DICT)

        # word_list = []

        # #print(ocr_output)

        # #populate list
        # for length in range(0,len(ocr_output["text"])):
        #     word_list.append("")

        # for length in range(0,len(ocr_output["text"])):
        #     if ocr_output["text"][length] != "":
        #         word_list[ocr_output["block_num"][length]] += " " + ocr_output["text"][length]

        # print(word_list)
        # #get the summary of the block numbers
        # block_num_sim_list = []
        # for i in ocr_output["block_num"]:
        #     if i not in block_num_sim_list:
        #         block_num_sim_list.append(i)

        # confidence_level = 80.0

        # bounding_box_list = []

        # length_of_block_num = len(ocr_output['block_num'])

        # #populate empty list
        # for i in range(0,length_of_block_num):
        #     bounding_box_list.append([])
        #     bounding_box_list[i].append(0)
        #     bounding_box_list[i].append(0)
        #     bounding_box_list[i].append(0)
        #     bounding_box_list[i].append(0)
        
        # #loop for the image boxes
        # for blk_number in block_num_sim_list:
        #     for i in range(0,length_of_block_num):
        #         if ocr_output["text"][i] != "":
        #             if ocr_output["block_num"][i] == blk_number:
        #                 #index 0 = x
        #                 bounding_box_list[blk_number][0] += ocr_output["left"][i]
        #                 #index 1 = y
        #                 bounding_box_list[blk_number][1] += ocr_output["top"][i]
        #                 #index 2 = w
        #                 bounding_box_list[blk_number][2] += ocr_output["width"][i]
        #                 #index 3 = h
        #                 bounding_box_list[blk_number][3] += ocr_output["height"][i]

        # print(bounding_box_list)

        # for item in bounding_box_list:
        #     if item != [0, 0, 0, 0]:
        #         print(item)
        #         cv2.rectangle(img, (bounding_box_list[blk_number][0], bounding_box_list[blk_number][1]), (bounding_box_list[blk_number][0] + bounding_box_list[blk_number][2], bounding_box_list[blk_number][1] + bounding_box_list[blk_number][3]), (0, 255, 0), 2)

        # print(ocr_output)

        #Your thread creation code:
        # thread = threading.Thread(target=stm_print_text, args=(output_to_show))
        # get_script_run_ctx()
        # thread.start()

        #stm_print_text(output_to_show)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_streamer(key="example", 
        video_frame_callback=video_frame_callback,
        video_html_attrs=VideoHTMLAttributes(
        autoPlay=True, controls=True, style={"width": "100%"}, muted=muted)
    )



