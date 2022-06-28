import os
import time
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
# from config_setting import *
from fluent import sender
from fluent import event

def meteo():

    os.environ['TZ'] = 'Europe/Rome'
    time.tzset()

    url_data = "http://www.meteoam.it/ta/infoStazione/LICC/catania_fontana_rossa"
    time_schedule = 30

    # #WebDriver associated with the browser type
    # driver = get_driver()
    
    # #GET Request of the web page we are going to inspect
    # driver.get(url_data)

    
    # tmp = """/html[1]/body[1]/div[5]/div[1]/section[1]/div[2]/section[1]/div[1]/div[1]/div[1]/table[2]/tbody[1]/tr[1]/td[1]/p[1]"""
    # hmd = """/html[1]/body[1]/div[5]/div[1]/section[1]/div[2]/section[1]/div[1]/div[1]/div[1]/table[2]/tbody[1]/tr[2]/td[1]/p[1]"""
    # wnd ="""/html[1]/body[1]/div[5]/div[1]/section[1]/div[2]/section[1]/div[1]/div[1]/div[1]/table[2]/tbody[1]/tr[3]/td[2]/p[1]"""
    # prs = """/html[1]/body[1]/div[5]/div[1]/section[1]/div[2]/section[1]/div[1]/div[1]/div[1]/table[2]/tbody[1]/tr[4]/td[1]/p[1]"""
    # vsb = """/html[1]/body[1]/div[5]/div[1]/section[1]/div[2]/section[1]/div[1]/div[1]/div[1]/table[2]/tbody[1]/tr[5]/td[1]/p[1]"""
    # cnd = """/html[1]/body[1]/div[5]/div[1]/section[1]/div[2]/section[1]/div[1]/div[1]/div[1]/table[2]/tbody[1]/tr[6]/td[1]/p[1]"""

    while True:
        #Load resource with BeautifulSoup
        try:
            page = requests.get(url_data, timeout=20)
            while (page.status_code != 200):
                page = requests.get(url_data, timeout=20)
        except:
            time.sleep(3)
            continue
        soup = BeautifulSoup(page.text, 'html.parser')

        #send_datas(driver, cnd, tmp, hmd, prs, vsb, wnd)
        send_datas(soup)
        
        time.sleep(int(time_schedule))
        #driver.refresh()
        

def send_datas(soup):  #(driver, cnd, tmp, hmd, prs, vsb, wnd):
    
    day = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        #condition = driver.find_element(By.XPATH, cnd).text
        condition = soup.find(id = "tempoinatto-dati").findAll("p")[7].text
        condition = str(condition).upper()
    except:
        condition = None
    try:
        #temperature = driver.find_element(By.XPATH, tmp).text
        temperature = soup.find(id = "tempoinatto-dati").findAll("p")[0].text
        temperature = int(temperature)
    except:
        temperature =  -999
    try:
        #wind = driver.find_element(By.XPATH, wnd).text
        wind = soup.find(id = "tempoinatto-dati").findAll("p")[4].text
        wind = int(wind)
    except:
        wind = -999
    try:
        #humidity = driver.find_element(By.XPATH, hmd).text
        humidity = soup.find(id = "tempoinatto-dati").findAll("p")[2].text
        humidity = int(humidity)
    except:
        humidity = -999
    try:
        #visibility = driver.find_element(By.XPATH, vsb).text
        visibility = soup.find(id = "tempoinatto-dati").findAll("p")[6].text
        visibility = int(visibility[1:-3])
    except: 
        visibility = -999
    try:
        #pressure = driver.find_element(By.XPATH, prs).text
        pressure = soup.find(id = "tempoinatto-dati").findAll("p")[5].text
        pressure = int(pressure)
    except: 
        pressure = -999

    sender.setup('WebMeteo', host='fluentd', port=24224)
    event.Event('data',{"City":"Catania", "Schedule":day, "Temperature":temperature, \
         "Humidity":humidity, "Visibility":visibility, "Wind":wind, "Pressure":pressure, "Condition":condition})

if __name__ == "__main__":
    meteo()
