from dotenv import dotenv_values
import time
import csv
import win32clipboard

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable

config = dotenv_values()

def initialize_web_driver(debuggerIp):
    # INITIALIZE EDGE BROWSER WEB DRIVER WITH REMOTE DEBUGGER
    options = webdriver.EdgeOptions()
    options.add_experimental_option("debuggerAddress", debuggerIp)
    return webdriver.Edge(options=options)

def login(driver, config):
    driver.get('https://www.upwork.com/browse/bench')

    driver.find_element(By.ID,"login_username").send_keys(config["EMAIL"])
    driver.find_element(By.ID,"login_password_continue").click()
    time.sleep(2)
    driver.find_element(By.ID,"login_password").send_keys(config["PASSWORD"])
    driver.find_element(By.ID,"login_control_continue").click()

def get_categories_and_specialities(driver):
    # GET CATEGORIES:
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, 1920)")
    time.sleep(2)
    category_buttons = driver.find_elements(By.CSS_SELECTOR, ".categories > .mb-5 > button")

    # GET SPECIALITIES
    category_dict = dict()

    for ctg_btn in category_buttons:
        ctg_btn.click()
        speciality_a = driver.find_elements(By.CSS_SELECTOR,".categories > .mb-5 > div > div > a")
        speciality_dict = dict()
        for a in speciality_a:
            speciality_dict[a.text] = a.get_attribute("href")
        category_dict[ctg_btn.text] = speciality_dict
    
    return category_dict

def get_freelancer_data(driver, id):

    freelancer_id = id

    try:
        location = driver.find_element(By.CLASS_NAME, "location").text
    except NoSuchElementException:
        location = None

    try:
        success_rate = driver.find_element(By.CSS_SELECTOR, "div div div h3").text
    except:
        success_rate = None
    
    try:
        badge = driver.find_elements(By.CSS_SELECTOR, ".identity-badges-container > span ~ span")[0].text
    except IndexError or NoSuchElementException:
        badge = None

    try:
        t_earnings = driver.find_element(By.CSS_SELECTOR, "[data-test=earned-amount-formatted]").text
    except NoSuchElementException:
        t_earnings = None

    try:
        t_jobs = driver.find_element(By.XPATH, "//small[text()='Total Jobs']//..//..//div[@class='stat-amount']").text
    except NoSuchElementException:
        t_jobs = None

    try:
        t_hours= driver.find_element(By.XPATH, "//small[text()='Total Hours']//..//..//div[@class='stat-amount']").text
    except NoSuchElementException:
        t_hours = None
    
    try:
        hours_per_week = driver.find_element(By.CSS_SELECTOR, "[data-test=profile-availability] div span").text
    except NoSuchElementException:
        hours_per_week = None
    
    try:
        languages= ""
        for element in driver.find_elements(By.CSS_SELECTOR, "li > [data-test=language]"):
            if element.text !="":
                languages = ",".join([languages, element.text])
        languages = languages[1:] #Remove the comma at the beginning

    except NoSuchElementException:
        languages = None

    try:
        profile_title = driver.find_element(By.CLASS_NAME, "pt-lg-5").text
    except NoSuchElementException:
        profile_title = None

    try:
        hourly_rate = driver.find_element(By.CSS_SELECTOR, "span[data-test=hourly-rate]").text
    except NoSuchElementException:
        hourly_rate = None
    
    try:
        skills = ""
        all_skills = driver.find_elements(By.CSS_SELECTOR, "span.up-skill-badge")
        skill_uls = [ul.text for ul in driver.find_elements(By.CSS_SELECTOR, ".skills-group-list-title + ul") if ul.text != ""]
        for i, skill_categ in enumerate([title.text for title in driver.find_elements(By.CLASS_NAME, "skills-group-list-title") if title.text != "" and "Other skills" not in title.text]):
            skills = skills + "/" + skill_categ
            if skill_uls[i] != "":
                skills = skills + "," + skill_uls[i].replace("\n", ",")

        all_skills = [skill.text for skill in all_skills if skill.text != ""]
        if len(all_skills) != 0:
            skills = skills + "/Other Skills"
            for skill in all_skills:
                if skill not in skills:
                    skills = skills + "," + skill
    except NoSuchElementException:
        skills = None

    profile_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Copy link to clipboard']")
    WebDriverWait(driver, timeout=10).until(element_to_be_clickable(profile_btn))
    profile_btn.click()
    
    win32clipboard.OpenClipboard()
    profile_link = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    return [freelancer_id, location, success_rate, badge, t_earnings, t_jobs, t_hours,
            hours_per_week, languages, profile_title, hourly_rate, skills, profile_link]

def get_jobs_data(driver, freelancer_profile_link):
    driver.get(freelancer_profile_link)


driver = initialize_web_driver("127.0.0.1:9014")
login(driver, config)
category_dict = get_categories_and_specialities(driver)

freelancers_csv = "freelancers.csv"
jobs_csv = "jobs.csv"

# Get Freelancer Data as csv
id_counter = 2025
with open(freelancers_csv, "r+", newline="") as file:
    freelancer_writer = csv.writer(file, delimiter="|")

    for category in list(category_dict.keys())[8:9]:
        for speciality in list(category_dict[category].keys()):
            driver.get(category_dict[category][speciality]) # Opens the link for the list of freelancers for the speciality

            time.sleep(3)
            freelancer_divs = driver.find_elements(By.CLASS_NAME, "freelancer-tile")

            for div in freelancer_divs:
                div.click()
                time.sleep(3)
                freelancer = get_freelancer_data(driver, id_counter)
                id_counter +=1
                freelancer_writer.writerow(freelancer)           
                    
                driver.back()