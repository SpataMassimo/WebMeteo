import os
import time
import base64
from io import BytesIO
from PIL import Image
from json import loads
from kafka import KafkaConsumer
from fluent import sender
from fluent import event

time_schedule = 30000
path_save = "images/"

topic = os.getenv("KAFKA_TOPIC", "restart_request")
consumer = KafkaConsumer(topic, bootstrap_servers=['10.0.100.23:9092'], \
    auto_offset_reset='latest',  enable_auto_commit=True, consumer_timeout_ms=time_schedule, \
    value_deserializer=lambda x: loads(x.decode('utf-8')))


def meteo():
	os.environ['TZ'] = 'Europe/Rome'
	time.tzset()
	
	files_images = os.listdir(path_save)
	for file in files_images:
		name_file = path_save + str(file)
		image = Image.open(name_file)
		send_image(image, name_file)
		for message in consumer:
			message = message.value
			if (message['restart_request'] == "True"):
				print("RESTART REQUEST")
				print("----------------------")
				print("RELOAD DRIVER")
				print("----------------------")
				#Here code for reload driver
				# 
				#  
			if (message['restart_request'] == "False"):
				print("NO RESTART REQUEST")
				print("----------------------")
	
	# images_input = load_images(path_save)
	# try:
	# 	image = Image.open(images_input[0])
	# 	send_image(image, images_input[0])
	# except:
	# 	print("NO IMAGE TO SEND")

	#count_image = 1
	# for message in consumer:
	# 	message = message.value
	# 	time.sleep(time_schedule)
	# 	if (count_image < len(images_input)):	
	# 		if (message['restart_request'] == "True"):
	# 			print("RESTART REQUEST")
	# 			print("----------------------")
	# 			print("RELOAD DRIVER")
	# 			print("----------------------")
	# 			#Here code for reload driver
	# 			# 
	# 			#  
	# 			image = Image.open(images_input[count_image])
	# 			send_image(image)
	# 		if (message['restart_request'] == "False"):
	# 			print("NO RESTART REQUEST")
	# 			print("----------------------")
	# 			image = Image.open(images_input[count_image])
	# 			send_image(image)
	# 	count_image = count_image + 1
	
	print("NO MORE IMAGE TO SEND!!!")
	

def send_image(image, name_img):
	buffered = BytesIO()
	image.save(buffered, format="PNG")
	image_string = base64.b64encode(buffered.getvalue()).decode()
	print("IMAGE SEND TO FLUENTD")
	print("Image: " +name_img)
	print("------------------------------------------------")	
	sender.setup('WebMeteo', host='fluentd', port=24224)
	event.Event('image',{"Image":image_string})

# def load_images(path_save):
# 	images = []
# 	files_images = os.listdir(path_save)
# 	for file in files_images:
# 		images.append((path_save + str(file)))
# 	return images

if __name__ == "__main__":
    meteo()