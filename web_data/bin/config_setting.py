from selenium import webdriver
from selenium.webdriver.edge.service import Service
from webdriver_manager.chrome import ChromeDriverManager


# Options for webdriver [add_experimental_option("detach",True)]
options_list = [ '--no-sandbox', 'headless', 'disable-infobars', 'start-maximized','--disable-extensions', '--disable-dev-shm-usage']

def get_driver():
    options = webdriver.ChromeOptions()
    add_options(options, options_list)
    return webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))

def add_options(options, options_list):
    for option in options_list:
        options.add_argument(option)

