from dotenv import dotenv_values
import time
import csv
import win32clipboard
import pandas as pd
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

# GET FREELANCER PROFILES
with open("freelancers.csv", "w", newline="") as file:
    writer = csv.writer(file, delimiter="|")

    if pd.read_csv("freelancers.csv",delimiter="|",nrows=1).empty:
        writer.writerow(["freelancer_id", "location", "success_rate",
                        "badge", "t_earnings", "t_jobs", "t_hours",
                        "hours_per_week", "languages", "profile_title",
                        "profile_desc", "hourly_rate", "skills", "profile_link"])

    id_counter = 0
    for category in category_dict.keys():
        for speciality in category_dict[category].keys():
            driver.get(category_dict[category][speciality])
            freelancer_divs = driver.find_elements(By.CLASS_NAME, "freelancer-tile")
            time.sleep(3)
            for div in freelancer_divs:
                div.click()
                time.sleep(3)

                freelancer_id = id_counter
                id_counter +=1

                location = driver.find_element(By.CLASS_NAME, "location").text
                success_rate = driver.find_element(By.CSS_SELECTOR, "div div div h3").text
                
                try:
                    badge = driver.find_elements(By.CSS_SELECTOR, ".identity-badges-container > span ~ span")[0].text
                except IndexError:
                    badge = "None"

                t_earnings = driver.find_element(By.CSS_SELECTOR, "[data-test=earned-amount-formatted]").text
                t_jobs = driver.find_element(By.XPATH, "//small[text()='Total Jobs']//..//..//div[@class='stat-amount']").text
                t_hours= driver.find_element(By.XPATH, "//small[text()='Total Hours']//..//..//div[@class='stat-amount']").text
                hours_per_week = driver.find_element(By.CSS_SELECTOR, "[data-test=profile-availability] div span").text

                languages= ""
                for element in driver.find_elements(By.CSS_SELECTOR, "li > [data-test=language]"):
                    if element.text !="":
                        languages = ",".join([languages, element.text])
                languages = languages[1:] #Remove the comma at the beginning

                profile_title = driver.find_element(By.CLASS_NAME, "pt-lg-5").text
                profile_desc = " ".join(driver.find_element(By.CSS_SELECTOR, "span.text-pre-line").text.splitlines())
                hourly_rate = driver.find_element(By.CSS_SELECTOR, "span[data-test=hourly-rate]").text
                
                skills = ""
                for element in driver.find_elements(By.CSS_SELECTOR, "span.up-skill-badge"):
                    if element.text != "":
                        skills = ",".join([skills, element.text])
                skills = skills[1:] #Remove the comma at the beginning

                driver.find_element(By.CSS_SELECTOR, "button[aria-label='Copy link to clipboard']").click()
                win32clipboard.OpenClipboard()
                profile_link = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                writer.writerow([freelancer_id, location, success_rate,
                                badge, t_earnings, t_jobs, t_hours,
                                hours_per_week, languages, profile_title,
                                profile_desc, hourly_rate, skills, profile_link])

                break
            break
        break
