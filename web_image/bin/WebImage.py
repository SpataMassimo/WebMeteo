import os
import time
import base64
from io import BytesIO
from PIL import Image
from json import loads
from config_setting import *
from kafka import KafkaConsumer
from fluent import sender
from fluent import event

url_image = "https://www.skylinewebcams.com/en/webcam/italia/sicilia/catania/centro-di-catania.html"
time_schedule = 120000
path_save = "images/"

topic = os.getenv("KAFKA_TOPIC", "restart_request")
try:
    consumer = KafkaConsumer(topic, bootstrap_servers=['10.0.100.23:9092'], \
        auto_offset_reset='latest',  enable_auto_commit=True, consumer_timeout_ms=time_schedule, \
        value_deserializer=lambda x: loads(x.decode('utf-8')))
except:
    print("KAFKA BROKER NOT FOUND")

def meteo():
    os.environ['TZ'] = 'Europe/Rome'
    time.tzset()
    
    #Load driver
    driver = load_driver(url_image)
    
    #Video
    image_element = get_video_element(driver)
    send_screenshoot(image_element)
    
    while True:
        try: 
            for message in consumer:
                message = message.value
                if (message['restart_request'] == "True"):
                    print("RESTART REQUEST")
                    print("----------------------")
                    print("QUIT DRIVER")
                    driver.quit()
                    print("----------------------")
                    print("RELOAD DRIVER")
                    print("----------------------")
                    driver = load_driver(url_image)
                    image_element = get_video_element(driver)
                if (message['restart_request'] == "False"):
                    print("NO RESTART REQUEST")
                    print("----------------------")
            send_screenshoot(image_element)
        except:
            print("KAFKA BROKER ERROR")
            time.sleep(120)
            send_screenshoot(image_element)

def send_screenshoot(image_element):
    day = time.strftime("%Y-%m-%d %H:%M:%S")
    image_name = day + ".png"
    image_path = path_save + image_name
    image_element.screenshot(image_path)
    image = Image.open(image_path)
    #Resize image, based on model input size
    size = (720,390)
    image = image.resize(size)
    #Convert image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    image_string = base64.b64encode(buffered.getvalue()).decode()
    sender.setup('WebMeteo', host='fluentd', port=24224)
    event.Event('image',{"Image":image_string, "Schedule": day})
    #Remove image from disk
    os.unlink(image_path)
    
if __name__ == "__main__":
    meteo()