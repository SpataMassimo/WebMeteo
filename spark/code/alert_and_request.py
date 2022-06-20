import telepot
import json
from pyspark.sql.functions import *

def restart_condition(class_prediction):
     if class_prediction == "nd":
          return "True"
     return "False"

def alert_condition(class_prediction, count_alert):
     if class_prediction == "nuvoloso":
          if (count_alert == 1):
               send_alert()
               return (count_alert + 1)
          else:
               return(count_alert + 1)
               
     else:
          return 0

def send_alert():
    token = '5366631076:AAE5RW3T8datNDqBoWTGpGqJsgtwbeWunUU'
    chat_id= -1001683360839
    message = "TEST  WEBAPP - .....ALLERTA METEO..... - Catania - Maltempo con possibili precipitazioni...."

    bot = telepot.Bot(token)
    bot.sendMessage(chat_id, message)

    print("SEND ALERT TO TELEGRAM")
    print("----------------------------------------------------")

def send_restart_request(value, spark):
    req = {"restart_request":value}
    df = spark.createDataFrame([req])

    df.select(to_json(struct("*")).alias("value")) \
        .selectExpr("CAST(value AS STRING)") \
        .write \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "10.0.100.23:9092") \
        .option("topic", "restart_request") \
        .option("partition", 1).save()