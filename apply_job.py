from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from datetime import datetime
import os
from decouple import config

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import logging
import traceback
from functools import wraps

from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline

from colorama import Fore, Style, init
# Initialize Colorama (especially important on Windows)
init(autoreset=True)

# define the loggin function as wrapper
def log_exceptions(func):
    """
    Decorator to log any exception that occurs in the decorated function.
    Logs the full traceback.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = f"Exception in {func.__name__}: {e}\n{traceback.format_exc()}"
            logging.error(error_message)
            # raise  # Re-raise the exception if you want the app to crash or handle it elsewhere
    return wrapper

@log_exceptions
def login(driver, email, passw):
    try:
        logb = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[text()='Login']"))
        )
        time.sleep(2)
        logb.click()

        time.sleep(2)
        # Enter Email/Password
        email_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your active Email ID / Username']"))
        )
        time.sleep(2)
        email_field.send_keys(email)

        password_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter your password']")
        password_field.send_keys(passw)
        time.sleep(2)
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5) 
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + "Login failed:")
        pass

@log_exceptions
def search_jobs(job_title:str, exp_yr:str, location:str):
    """  
    job_title: Data Scientist, ML Engineer
    exp_yr: 2 years
    location: Pune, Mumbai
    """
    try:
        #1. search bar button on home page (then it will expand)
        search_bar_btn = driver.find_element(By.CLASS_NAME, "nI-gNb-sb__icon-wrapper").click()
        
        # step 2: enter keyword (JOB Titles)
        keyword_input = driver.find_element(By.CLASS_NAME, "suggestor-input")
        keyword_input.clear()  # Clear any pre-existing text
        keyword_input.send_keys(job_title)

        # step 3: enter experience
        experience_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "experienceDD"))
        )
        experience_input.click()
        # Wait for the dropdown options to load
        experience_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dropdownPrimary"))
        )

        # Select the "2 years" option from the dropdown
        experience_option = driver.find_element(By.XPATH, f"//div[@class='dropdownPrimary']//span[text()='{exp_yr}']")
        experience_option.click()

        # step 4: enter location
        location_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter location']"))
        )
        location_input.clear()
        location_input.send_keys(location)

        # step 5: click on search btn
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "nI-gNb-sb__icon-wrapper"))
        )

        search_button.click()
        return True
        
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + "Search failed:")
        return False

@log_exceptions
def click_next_page(driver):
    try:
        # Wait for the pagination container to load
        pagination_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "styles_pages__v1rAK"))
        )

        # Find all the page number links
        page_links = pagination_container.find_elements(By.TAG_NAME, 'a')

        # Find the link for the next page
        next_page_link = None
        for i in range(len(page_links)-1):
            # Check if the current link is the "selected" one (the current page)
            if "styles_selected" in page_links[i].get_attribute("class"):
                # Get the next page link
                next_page_link = page_links[i + 1]
                break
        
        # If there is a next page link, click it
        if next_page_link:
            next_page_url = next_page_link.get_attribute('href')
            driver.get(next_page_url)  # Navigate to the next page
            print(Style.BRIGHT + Fore.YELLOW + f"Navigating to the next page: {next_page_url}")
        else:
            print(Style.BRIGHT + Fore.CYAN + "No next page available.")
    except Exception as e:
        # print("Error:", e)
        pass

@log_exceptions
def check_unwanted_tab(driver):
    """ 
    this function is used to proactively check the any unwanted tab opened by the browser
    and close it.
    """
    try:
        if len(driver.window_handles)>=2:
            #switch to -1 tab and close it
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()
            original_window = driver.window_handles[0]
            driver.switch_to.window(original_window)
            return True
        else:
            return False
    except Exception as e:
        # print("Error:", e)
        pass

@log_exceptions
def save_and_apply_job(driver, max_pages:int=4):
    """ 
    This function used to iterate over the pages of job listing and apply the job based on the type of apply method.


    # Job Application Type: WithCompanySite NaukriQuickApply NaukriQuesApply
    args:
        driver: webdriver instance = driver 
        max_pages: int = number of pages to scrape
    return: csv_data, qa_data, total_saved
    """ 
    
    csv_data = []
    qa_data = []

    total_saved = 0
    current_page = 0
    goto_next_page = False

    # Capture the window handle of the original tab
    original_window = driver.current_window_handle

    while current_page < max_pages:
        
        print(Style.BRIGHT + Fore.YELLOW + f"Scraping page {Style.BRIGHT + Fore.CYAN} {current_page}")
        if goto_next_page:
            click_next_page(driver)
            time.sleep(0.6)
    
        # step 1: Find all job elements on the page
        job_elements = driver.find_elements(By.XPATH, '//div[@class="srp-jobtuple-wrapper"]')
        total_jobs_on_curr_page = len(job_elements)

        if total_jobs_on_curr_page> 0:
            for win_idx, job_element in enumerate(job_elements):
                check_unwanted_tab(driver)
                time.sleep(0.2)
                try:
                    # job id
                    job_id = job_element.get_attribute('data-job-id')
                    # job title
                    job_tile =  job_element.find_element(By.XPATH, './/a[@class="title "]').get_attribute('title')
                    # company name
                    company_name = job_element.find_element(By.XPATH, './/a[contains(@class, "comp-name")]').get_attribute('title')
                   
                    # click on title which open new tab
                    job_element.find_element(By.XPATH, './/a[@class="title "]').click()
                    time.sleep(0.12)
                    # swith to new window
                    # Wait for the new tab to open (usually needs a little wait to be sure)
                    # WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(win_idx+2))
                    # new_window = [window for window in driver.window_handles if window != original_window][0]
                    new_window = driver.window_handles[-1]
                    driver.switch_to.window(new_window)
                    time.sleep(0.12)
                    
                    # Condition 1: if Apply button redirect to company site (Type: WithCompanySite)
                    apply_button_redirect = driver.find_elements(By.XPATH, '//button[@class="styles_company-site-button__C_2YK company-site-button"]')
                    # condition 2: if Apply button is Quick Apply (Type: NaukriQuickApply)
                    apply_button_easy_apply = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Apply')]"))
                    )

                    # cond1
                    if apply_button_redirect:
                        # save the job and and related to attribute to CSV (for cross verify)
                        save_button = driver.find_element(By.XPATH, '//button[contains(text(), "Save")]')
                        if save_button.text != "Saved":
                            save_button.click()
                            total_saved += 1

                            # update job-data
                            csv_data.append({'JobId': job_id, 
                                             'JobTitle': job_tile, 
                                             'CompanyName': company_name, 'Type': 'WithCompanySite', 'Link': '', 'Package': 0.0,
                                             'DateTime': datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'Status': 'Pending'})
                        # swith back to original window
                        driver.close()
                        original_window = driver.window_handles[0]
                        driver.switch_to.window(original_window)
                        time.sleep(0.8)
                    
                    # cond2
                    if not apply_button_redirect and apply_button_easy_apply:
                        apply_button_easy_apply.click()
                        time.sleep(1.6)
                        apply_message_span = driver.find_elements(By.CLASS_NAME, 'apply-message')
                        
                        # Cond 2.1: NaukriQuickApply
                        if apply_message_span:
                            # apply_message_span = WebDriverWait(driver, 10).until(
                            #             EC.presence_of_element_located((By.CLASS_NAME, "apply-message"))
                            #         )

                            apply_status_text = apply_message_span[-1].text
                            status = "Applied" if "successfully applied" in str(apply_status_text).lower() else "Failed"
                            total_saved += 1

                            # update job-data   
                            csv_data.append({'JobId': job_id, 
                                            'JobTitle': job_tile, 
                                            'CompanyName': company_name, 'Type': 'NaukriQuickApply', 'Link': '', 'Package': 0.0,
                                            'DateTime': datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'Status': status})
                            driver.close()
                            original_window = driver.window_handles[0]
                            driver.switch_to.window(original_window)
                            time.sleep(0.8)
                        # Cond 2.2: NaukriQuesApply
                        else:
                            try:
                                flag_for_question = True

                                while  flag_for_question:
                                    # Get the questions li
                                    question_li = driver.find_elements(By.XPATH, '//li[@class="botItem chatbot_ListItem"]')
                                    # fetch the latest/last one
                                    que = question_li[-1].text
                                    
                                    # get the answer from AI model pipeline
                                    raw_ans_dict = nlp(question=que, context=resume)
                                    ans = raw_ans_dict.get('answer')
                                    score = raw_ans_dict.get('score')
                                    # answer the question
                                    q_ans_txt_area = driver.find_elements(By.XPATH, '//div[@class="textArea"]')
                                    q_ans_txt_area[0].send_keys(ans)
                                    time.sleep(0.09)
                                    # save button
                                    save_btn = driver.find_element(By.XPATH, '//div[@class="send"]')
                                    save_btn.click()
                                    time.sleep(1.2)
                                    # check for next question (by checking if apply-status message is present)
                                    apply_message_span = driver.find_elements(By.CLASS_NAME, 'apply-message')
                                    if apply_message_span:
                                        apply_status_text = apply_message_span[0].text
                                        status = "Applied" if "successfully applied" in str(apply_status_text).lower() else "Failed"
                                        total_saved += 1
                                        # update job-data   
                                        csv_data.append({'JobId': job_id, 
                                                        'JobTitle': job_tile, 
                                                        'CompanyName': company_name, 'Type': 'NaukriQuesApply', 'Link': '', 'Package': 0.0,
                                                        'DateTime': datetime.now().strftime("%d-%m-%Y %H:%M:%S"), 'Status': status})
                                        qa_data.append({'JobId': job_id, 'Question': que, 'Answer': ans, 'Score': score})
                                        flag_for_question = False
                                        driver.close()
                                        original_window = driver.window_handles[0]
                                        driver.switch_to.window(original_window)
                                        time.sleep(0.8)
                            
                            except Exception as e:
                                print(Style.BRIGHT + Fore.RED + "Error:")
                                continue
                    
                except Exception as e:
                    print(Style.BRIGHT + Fore.RED + "Error:")
                    continue
            current_page += 1 
            goto_next_page = True 
             
    return csv_data, qa_data, total_saved

@log_exceptions
def save_data(data: list[dict], file_path: str):
    """  
    data: {}
    """
    new_df = pd.DataFrame()
    try:
        new_df = pd.DataFrame(data)
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + "Error:")
        return False
    try:
        # Check if the file already exists
        if not os.path.exists(file_path):
            # If file doesn't exist, create it and write the header along with the new data
            new_df.to_csv(file_path, mode='w', header=True, index=False)
        else:
            # If file exists, append the new data without writing the header
            new_df.to_csv(file_path, mode='a', header=False, index=False)
        return True
    except Exception as e:
        print(Style.BRIGHT + Fore.RED + "Error:")
        return False
    

if __name__ == "__main__":
    print(Style.BRIGHT + Fore.GREEN + "Job Application Automation Started...")
    # for logging the errors (we will dump the error in the log file) 
    file_name =  f'job_app_errors_{datetime.now().strftime("%d-%m-%Y")}.log'
    # Simple logger setup (you can replace this with your own logger class if needed)
    logging.basicConfig(
        filename= file_name,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Initialize Chrome Driver with the correct Service object
    service = Service(ChromeDriverManager().install())

    # initialize the model
    model_name = "deepset/roberta-base-squad2"
    nlp = pipeline('question-answering', model=model_name, tokenizer=model_name, device=0)
    
    # step 1 - read the resume
    print(Style.BRIGHT + Fore.YELLOW + "Reading the resume...")
    with open("E:\job-app-automate\data\cv_context.txt") as f:
        resume = f.read()

    # initialize the driver
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.naukri.com/")
    
    print(Style.BRIGHT + Fore.YELLOW + "creds loading...")
    email = config("email")
    passw = config("passw")

    login(driver, email, passw)

    # search jobs
    searched = search_jobs("Data Scientist, Machine Learning Engineer","2 years", "Pune, Mumbai")

    if searched:
        job_application_data,qa_data, total_saved = save_and_apply_job(driver, max_pages=2)
        print(Style.BRIGHT + Fore.CYAN + f"Total Jobs Applied: {Style.BRIGHT + Fore.GREEN } {total_saved}")
        # save the job application data
        save_job_data = save_data(job_application_data, "job_application.csv")
        # save the question-answer data
        save_qa_data = save_data(qa_data, "qa_data.csv")
        print(Style.BRIGHT + Fore.GREEN + "Data saved successfully.")
    
    driver.quit()



