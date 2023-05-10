from dotenv import dotenv_values

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

config = dotenv_values()

driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=options)

driver.set_window_position(0, 0)
driver.set_window_size(1920, 1080)

# LOGIN
driver.get('https://www.upwork.com/ab/account-security/login')

driver.find_element(By.ID,'login_username').send_keys(config["EMAIL"])
driver.find_element(By.ID,'login_password_continue').click()
driver.implicitly_wait(5)
driver.find_element(By.ID,"login_password").send_keys(config["PASSWORD"])
driver.find_element(By.ID,'login_control_continue').click()


