#import opencv2
import threading, cv2
import imutils

#import streamlit functions
import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoHTMLAttributes

#import OCR model pytesseract and functions
import pytesseract
from  pytesseract import Output

#import MQTT 
import paho.mqtt.client as paho

#import json
import json

#import regular expressions
import re
import string

#list of symbols for preprocessing
list_of_symbols = ["™","®","©","&trade;","&reg;","&copy;","&#8482;","&#174;","&#169;","\n"]


def remove_duplicates(list_of_numbers):
    """
    Function to remove duplicate block numbers for bounding box
    :param list of numbers:
    :return: List without duplicates
    """
    return list(dict.fromkeys(list_of_numbers))

def on_publish():
    """
    Function to indicate MQTT was successful o the commandline
    :return: null
    """
    print("MQTT data published \n")
    pass

def textpreprocessing(textprocess):
    """
    Function to clean and preprocess list of text
    :param list of words:
    :return: List of cleaned words
    """
    #uppercase all the letters
    text_to_process = textprocess.upper()

    #remove the punctuations
    text_to_process = "".join([char for char in text_to_process if char not in string.punctuation])

    #remove other symbols
    for symbol in list_of_symbols:
        text_to_process = text_to_process.replace(symbol," ")

    #remove unicode
    text_to_process = text_to_process.encode("ascii", "ignore")
    text_to_process = text_to_process.decode()

    return text_to_process

def dosagepreprocessing(textprocess):
    """
    Function to clean words to get the dosage
    :param list of numbers:
    :return: dosage or empty string
    """
    #uppercase all the letters
    text_to_process = textprocess.upper()

    #remove the punctuations
    text_to_process = "".join([char for char in text_to_process if char not in string.punctuation])

    #use try or it will error
    try:
        #use regex
        text_to_process = re.search("(\d+)(MG)", text_to_process).group()
    except:
        text_to_process = ""
            
    return text_to_process

def mainApp():

    #check the session state and set default values
    if 'mqtt_user_input_broker' not in st.session_state:
        st.session_state.mqtt_user_input_broker = "broker.hivemq.com"

    if "mqtt_user_input_topic" not in st.session_state:
        st.session_state.mqtt_user_input_topic = "sample"

    if "mqtt_user_input_port" not in st.session_state:
        st.session_state.mqtt_user_input_port = 1883
    if "mqtt_connection_status" not in st.session_state:
        st.session_state.mqtt_connection_status = False

    #app header
    st.subheader("OpenCV live video enhancement and OCR App")
    
    #mqtt controls
    mqtt_user_status_answer = st.checkbox("Connect MQTT communication")  

    #mqtt expander for settings
    if mqtt_user_status_answer:
        with st.expander("MQTT Configurations"):
            with st.form("mqtt_config_form",clear_on_submit=False):

                mqtt_user_broker = st.text_input("Broker")
                mqtt_user_port = st.number_input("Port", value=1883)
                mqtt_user_topic = st.text_input("Topic")

                submitted = st.form_submit_button("Configure")
                if submitted:
                    st.info(f"MQTT Configurations saved, Broker: {st.session_state.mqtt_user_input_broker}, Port: {st.session_state.mqtt_user_input_port}\n, Topic: {st.session_state.mqtt_user_input_topic}")
                    #mqtt config
                    st.session_state.mqtt_user_input_broker = mqtt_user_broker
                    st.session_state.mqtt_user_input_port = mqtt_user_port
                    st.session_state.mqtt_user_input_topic = mqtt_user_topic
                    st.session_state.mqtt_connection_status = False
    #warning containers
    warning_containers = st.empty()

    #container
    img_container = {"img":None}

    #thread lock
    lock = threading.Lock()

    #streamlit webrtc to start the live video feed
    def video_frame_callback(frame):

        img = frame.to_ndarray(format="bgr24")

        with lock:
            img_container["img"] = img

        return frame

    #streamlit webrtc to set the live feed process and configuration
    ctx = webrtc_streamer(key="example", 
        video_frame_callback=video_frame_callback,
        video_html_attrs=VideoHTMLAttributes(
        autoPlay=True, controls=True, style={"width": "100%","height" : "100%"}, muted=True)
    )

    #streamlit UI components for augmentation
    enhance = st.sidebar.checkbox("Enhance")
    resize_status = st.sidebar.checkbox("Resize")
    brightness_amount = st.sidebar.slider("Brightness", min_value=-100, max_value=100, value=0)
    rotation_amount = st.sidebar.slider("Rotation", min_value=-360, max_value=360, value=0)
    st.sidebar.write("Crop")

    #cropping collapsible UI menu
    with st.sidebar.expander("Crop Configurations"):
        #the max value is kept in mind with the size of image this value can change
        crop_height_start = st.slider("Width Start", min_value=0,max_value=640,value=0)
        crop_height_end = st.slider("Width End", min_value=0,max_value=640,value=640)

        if(crop_height_start >= crop_height_end):
            st.warning("Height Start cannot be larger than or equal to Height End")

        crop_width_start = st.slider("Height Start", min_value=0,max_value=480,value=0)
        crop_width_end = st.slider("Height End", min_value=0,max_value=480,value=480)
        
        if(crop_width_start >= crop_width_end):
            st.warning("Width Start cannot be larger than or equal to Height End")

    #container to put the processed image
    image_output_container  = st.empty()

    #container to write 
    text_output_container = st.empty()

    #while loop to process every frame
    while ctx.state.playing:
        with lock:
            img = img_container["img"]
        if img is None:
            continue

        if enhance == True:
            img = cv2.detailEnhance(img, sigma_s=12, sigma_r=0.15)

        #convert to grey
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        img = cv2.convertScaleAbs(img, beta=brightness_amount)

        img = imutils.rotate(img,rotation_amount)

        #convert the format to rgb 
        #img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        #cropping and resizing 
        if(crop_height_start < crop_height_end and crop_width_start < crop_width_end):
            img = img[crop_width_start:crop_width_end,crop_height_start:crop_height_end]
            if resize_status:
                img = cv2.resize(img,(640,480))

        #start mqtt connection
        if mqtt_user_status_answer == True and st.session_state.mqtt_connection_status == False:
            try:
                print(st.session_state.mqtt_user_input_broker)
                print(st.session_state.mqtt_user_input_port)
                print(st.session_state.mqtt_user_input_topic)
                print(st.session_state.mqtt_connection_status)

                mqttclient = paho.Client()
                mqttclient.on_publish = on_publish
                mqttclient.connect(st.session_state.mqtt_user_input_broker,st.session_state.mqtt_user_input_port)
                st.session_state.mqtt_connection_status =True
            except:
                with warning_containers.container():
                    st.error("MQTT Client could not connect. Check input port, broker and topic")

        #using pytesseract to get prediction for each frame
        ocr_output = pytesseract.image_to_data(img, output_type=Output.DICT)

        #process the block number for bounding box
        word_list_range = ocr_output["block_num"]
        word_list_range = remove_duplicates(word_list_range)
        word_list_range = len(word_list_range)

        #list to store words
        word_list = []

        #populate list
        for length in range(0,word_list_range):
            word_list.append([])
            for x in range(0,2):
                word_list[length].append("")
            word_list[length].append(0.0)
        
        #use the block number as index to connect the block number to the word belonging to it 
        for length in range(0,len(ocr_output["text"])):
            if ocr_output["text"][length] != "":
                word_list[ocr_output["block_num"][length]][0] += " " + ocr_output["text"][length]
                word_list[ocr_output["block_num"][length]][1] += " " + ocr_output["conf"][length]

        #calculate confidence average
        for x  in range(0,len(word_list)):
            average = 0.0
            if word_list[x][1] != "":
                confidence = word_list[x][1]
                confidence_list = confidence.split(" ")
                confidence_list.pop(0)

                for y in confidence_list:
                    average+=float(y)
                average = average/len(confidence_list)
                word_list[x][2] =  average  

        #get the best confidence words
        output_to_show = ""
        best_confidence = 0.0
        for num in  range(0,word_list_range):
            if best_confidence < word_list[num][2]:
                best_confidence = word_list[num][2]
                output_to_show = word_list[num][0]
            
        #process the data
        mqtt_drugname = textpreprocessing(output_to_show)

        #dosage preprocessing
        mqtt_dosage = dosagepreprocessing(output_to_show)

        #mqtt message decode to json for mqtt
        mqtt_message = json.dumps({"drug_name":mqtt_drugname,"drug_dosage":mqtt_dosage})


        #mqtt publishing
        if mqtt_user_status_answer == True and st.session_state.mqtt_connection_status == True:
            try:
                mqttclient.publish(st.session_state.mqtt_user_input_topic,mqtt_message)
            except:
                with warning_containers.container():
                    st.error("MQTT Client could not Publish. Check input port, broker and topic")

        #using streamlit container 
        with text_output_container.container():
            #UI clear labels
            st.markdown("**__OCR Textput with best confidence:__**")
            st.write(mqtt_drugname)  

        #bounding box
        n_boxes = len(ocr_output['level'])
        for i in range(n_boxes):
            (x, y, w, h) = (ocr_output['left'][i], ocr_output['top'][i], ocr_output['width'][i], ocr_output['height'][i])
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        #show what frame does the OCR see
        with image_output_container.container():
            #UI clear labels
            st.markdown("**__Image Frame sent to OCR model:__**")
            st.image(img)

        
        