from dotenv import dotenv_values
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

config = dotenv_values()

# INITIALIZE EDGE BROWSER WEB DRIVER WITH REMOTE DEBUGGER
options = webdriver.EdgeOptions()
options.add_experimental_option("debuggerAddress", "127.0.0.1:9014")
driver = webdriver.Edge(options=options)

# LOGIN
driver.get('https://www.upwork.com/browse/bench')

driver.find_element(By.ID,"login_username").send_keys(config["EMAIL"])
driver.find_element(By.ID,"login_password_continue").click()
time.sleep(2)
driver.find_element(By.ID,"login_password").send_keys(config["PASSWORD"])
driver.find_element(By.ID,"login_control_continue").click()

# GET CATEGORIES:
time.sleep(3)
driver.execute_script("window.scrollTo(0, 1920)")
time.sleep(2)
category_buttons = driver.find_elements(By.CSS_SELECTOR, ".categories > .mb-5 > button")
categories = [btn.text for btn in category_buttons]

# GET SPECIALITIES
category_dict = dict()

for ctg_btn in category_buttons:
    ctg_btn.click()
    speciality_a = driver.find_elements(By.CSS_SELECTOR,".categories > .mb-5 > div > div > a")
    speciality_dict = dict()
    for a in speciality_a:
        speciality_dict[a.text] = a.get_attribute("href")
    category_dict[ctg_btn.text] = speciality_dict

