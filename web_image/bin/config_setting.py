from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Options for webdriver 
options_list = [ '--no-sandbox', 'headless', 'disable-infobars', 'start-maximized','--disable-extensions', '--disable-dev-shm-usage']

#Return the driver with the options
def get_driver():
    options = webdriver.ChromeOptions()
    add_options(options, options_list)
    return webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

#Add options to the driver
def add_options(options, options_list):
    for option in options_list:
        options.add_argument(option)

#Load driver
def load_driver(url):
    driver = get_driver()
    #GET Request of the web page we are going to inspect
    driver.get(url)
    #Accept Cookies button
    cookies_button_xpath = "//*[@id=\"trigPref\"]/div/div/div[3]/a"
    try:
        driver.find_element(By.XPATH, cookies_button_xpath).click()
    except:
        print("No cookies")
    try:
        #Start video button
        start_video_xpath = """//div[@class='player-poster clickable']"""
        driver.find_element(By.XPATH, start_video_xpath).click()
    except:
        print("No video to start")
        exit(1)

    #Espand video fullscreen button
    try:
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,"""//button[@aria-label='fullscreen']//*[name()='svg']"""))).click()
        #WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH,"""//button[@aria-label='fullscreen']//*[name()='svg']"""))).click()
        #WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By."""/html[1]/body[1]/div[2]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/div[3]/button[1]/*[name()='svg'][1]"""))).click()
    except:
        print("Expand button not found")
        exit(1)

    return driver

#Return the element associated to the video
def get_video_element(driver):
    #Video
    image_element = driver.find_element(By.XPATH, "(//video)[1]")
    return image_element