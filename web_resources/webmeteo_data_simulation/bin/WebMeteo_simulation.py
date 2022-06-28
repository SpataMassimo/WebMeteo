import os
import time
import random
from json import loads
from kafka import KafkaConsumer
from fluent import sender
from fluent import event

time_schedule = 60000
path_save = "images/"

topic = os.getenv("KAFKA_TOPIC", "restart_request")
consumer = KafkaConsumer(topic, bootstrap_servers=['10.0.100.23:9092'], \
    auto_offset_reset='latest',  enable_auto_commit=True, consumer_timeout_ms=time_schedule, \
    value_deserializer=lambda x: loads(x.decode('utf-8')))


def meteo():
	os.environ['TZ'] = 'Europe/Rome'
	time.tzset()	
	send_data()

	while(True):
		time.sleep(30)
		send_data()

def send_data():
	cond = ["SERENO","NUVOLOSO", "PIOGGIA"]
	day = time.strftime("%Y-%m-%d %H:%M:%S")
	temperature = random.randint(-10 , 60)
	humidity = random.randint(0,100)
	visibility = random.randint(0,15)
	wind = random.randint(1,30)
	pressure = random.randint(900, 1150)
	condition = random.choice(cond)
	sender.setup('WebMeteo', host='fluentd', port=24224)
	event.Event('data',{"City":"Catania", "Schedule":day, "Temperature":temperature, "Humidity":humidity, "Visibility":visibility, "Wind":wind, "Pressure":pressure, "Condition":condition})
	
if __name__ == "__main__":
    meteo()