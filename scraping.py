from dotenv import dotenv_values
import time
import csv
import win32clipboard

import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, presence_of_element_located, title_contains, number_of_windows_to_be

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
    wait.until(element_to_be_clickable(profile_btn))
    profile_btn.click()
    
    win32clipboard.OpenClipboard()
    profile_link = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()

    return [freelancer_id, location, success_rate, badge, t_earnings, t_jobs, t_hours,
            hours_per_week, languages, profile_title, hourly_rate, skills, profile_link]

def get_jobs_data(driver, freelancer_id, freelancer_profile_link, job_idx):
    driver.get(freelancer_profile_link)
    jobs = []

    page_idx = 1
    try:
        comp_jobs_tab_locator = (By.XPATH, "//button[contains(text(),'Completed jobs')]")
        wait.until(presence_of_element_located(comp_jobs_tab_locator))
    except TimeoutException:
        return jobs
    
    completed_jobs_num = int(driver.find_element(*comp_jobs_tab_locator).text.split(" ")[-1].strip("()").replace(",",""))
    total_pages = np.ceil(completed_jobs_num / 10)

    # Store the ID of the original window
    original_window = driver.current_window_handle

    while True:
        time.sleep(2)
        job_links = driver.find_elements(By.CSS_SELECTOR, "#jobs_completed_desktop > div > div > div > div > div > h4 > a")
        wait.until(element_to_be_clickable(job_links[0]))
        for link in job_links:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", link)
                link.click()
            except ElementClickInterceptedException:
                driver.execute_script("arguments[0].scrollIntoView();", link)
                link.click()
            try:
                wait.until(presence_of_element_located((By.XPATH, "//h3[contains(text(),'Job Details')]")))
            except TimeoutException:
                close_button = driver.find_element(By.XPATH, "//button[contains(text(),'Close')]")
                wait.until(element_to_be_clickable(close_button))
                close_button.click()
                continue
            try:
                driver.find_element(By.XPATH, "//p[text()='This job is private']")
            except NoSuchElementException:
                job_id = job_idx

                job_title = driver.find_element(By.CSS_SELECTOR, "h2.up-modal-title").text

                earnings_summary = driver.find_elements(By.CSS_SELECTOR, "div.feedback-summary-col > div > div")
                
                try:
                    hourly_rate = None
                    earnings = None
                    driver.find_element(By.XPATH, "//strong[contains(text(), 'Private earnings')]")
                except:
                    try:
                        if "Fixed" in earnings_summary[1].text:
                            hourly_rate = None
                            earnings = earnings_summary[0].text.split(" ")[0]
                        else:
                            hourly_rate = earnings_summary[1].text.split(" ")[0]
                            earnings = earnings_summary[2].text.split(" ")[0]
                    except IndexError:
                        pass

                try:
                    feedback_for_freelancer = float(driver.find_element(By.XPATH, "//span[contains(text() ,'Overall rating')]/following-sibling::span").text)
                except NoSuchElementException:
                    feedback_for_freelancer = None

                try:
                    feedback_for_client = driver.find_element(By.XPATH, "//h3[contains(text(), 'Job Feedback')]//..//div//strong").text
                except NoSuchElementException:
                    feedback_for_client = None

                # Check we don't have other windows open already
                assert len(driver.window_handles) == 1
                # Click the link which opens in a new window
                full_post_link_locator = (By.PARTIAL_LINK_TEXT, "View entire job post")
                try:
                    wait.until(presence_of_element_located(full_post_link_locator))
                except TimeoutException:
                    close_button = driver.find_element(By.XPATH, "//button[contains(text(),'Close')]")
                    wait.until(element_to_be_clickable(close_button))
                    close_button.click()
                    continue

                driver.find_element(*full_post_link_locator).click()
                # Wait for the new window or tab
                wait.until(number_of_windows_to_be(2))
                # Loop through until we find a new window handle
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break
                # Wait for the new tab to finish loading content
                wait.until(title_contains(job_title))

                job_description = driver.find_element(By.CLASS_NAME, "job-description").text.replace("\n"," ")

                weekly_hours_needed = None
                project_length = None
                experience_level = None

                for feature in driver.find_elements(By.CSS_SELECTOR, "ul[data-test= 'job-features'] > li"):
                    feature_data = feature.text.split("\n")[0]
                    if "hrs/week" in feature.text:
                        weekly_hours_needed = feature_data                        
                    
                    if "Project Length" in feature.text:
                        project_length = feature_data

                    if "looking for" in feature.text:
                        experience_level = feature_data                     

                client_location = driver.find_element(By.CSS_SELECTOR, "li[data-qa = 'client-location']").get_attribute("innerText").split("\n")[0]

                skills_required = ""
                skills_and_categ = driver.find_elements(By.XPATH, "//div[contains(@class, 'group-title')]/parent::div")
                if len(skills_and_categ) > 0:
                    for categ in skills_and_categ:
                        skills_required += "/" + categ.text.replace("\n", ",")
                else:
                    skills = driver.find_elements(By.CLASS_NAME, "up-skill-badge")
                    skills = [a.text for a in skills]
                    skills_required = ",".join(skills)

                profile_btn = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Copy to clipboard']")
                wait.until(element_to_be_clickable(profile_btn))
                profile_btn.click()
                
                try:
                    win32clipboard.OpenClipboard()
                    profile_link = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()
                except:
                    driver.refresh()
                    win32clipboard.OpenClipboard()
                    profile_link = win32clipboard.GetClipboardData()
                    win32clipboard.CloseClipboard()


                jobs.append([job_id, freelancer_id, job_title, job_description, hourly_rate, 
                             weekly_hours_needed, project_length, experience_level, skills_required, 
                             earnings, feedback_for_freelancer, client_location, feedback_for_client, profile_link])

                driver.close()
                driver.switch_to.window(original_window)

            close_button = driver.find_element(By.XPATH, "//button[contains(text(),'Close')]")
            wait.until(element_to_be_clickable(close_button))
            close_button.click()
            if len(jobs) >= 10: break

        if len(jobs) >= 10: break
        
        print(str(page_idx) + "/" + str(total_pages))
        if page_idx < total_pages:
            next_locator = (By.CSS_SELECTOR, ".work-history li.pagination-link > button")
            pagination_buttons = driver.find_elements(*next_locator)
            pagination_texts = [button.text for button in pagination_buttons]
            next_button = pagination_buttons[pagination_texts.index("Next")]
            try:
                wait.until(element_to_be_clickable(next_button))
                next_button.click()
            except (ElementClickInterceptedException):
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                next_button.click()

            page_idx +=1
        else: break
                
    return jobs

driver = initialize_web_driver("127.0.0.1:9014")
wait = WebDriverWait(driver, 10)
login(driver, config)
category_dict = get_categories_and_specialities(driver)

freelancers_csv = "freelancers.csv"
jobs_csv = "jobs.csv"

# Get Freelancer Data as csv
id_counter = 0
with open(freelancers_csv, "r+", newline="") as file:
    freelancer_writer = csv.writer(file, delimiter="|")

    for category in list(category_dict.keys())[11:12]:
        for speciality in list(category_dict[category].keys())[9:]:
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

# Get Jobs Data as csv
with open(jobs_csv, "a", newline="") as file:
    freelancer_profile_df = pd.read_csv("reduced_freelancers.csv", delimiter="|", usecols=["freelancer_id", "profile_link"])
    job_writer = csv.writer(file, delimiter="|")

    for row in tuple(freelancer_profile_df.iterrows())[424:]:
        freelancer = row[1]

        freelancer_id = freelancer["freelancer_id"]
        profile_link = freelancer["profile_link"]
        jobs = get_jobs_data(driver, freelancer_id, profile_link, 0)
        job_writer.writerows(jobs)
        print(f"Finished freelancer: {freelancer_id}")