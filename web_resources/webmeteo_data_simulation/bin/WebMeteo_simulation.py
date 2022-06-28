import os
import time
import random
from fluent import sender
from fluent import event

time_schedule = 60000
cond = ["SERENO", "NUVOLOSO", "PIOGGIA"]

def meteo():
	os.environ['TZ'] = 'Europe/Rome'
	time.tzset()

	while(True):
		send_data()
		time.sleep(30)

def send_data():
	day = time.strftime("%Y-%m-%d %H:%M:%S")
	temperature = random.randint(-10, 60)
	humidity = random.randint(0, 100)
	visibility = random.randint(0, 15)
	wind = random.randint(1, 30)
	pressure = random.randint(900, 1150)
	condition = random.choice(cond)
	
	sender.setup('WebMeteo', host='fluentd', port=24224)
	event.Event('data',{"City":"Catania", "Schedule":day, "Temperature":temperature, "Humidity":humidity, "Visibility":visibility, "Wind":wind, "Pressure":pressure, "Condition":condition})
	
if __name__ == "__main__":
    meteo()
