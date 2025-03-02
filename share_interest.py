from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from decouple import config

# Initialize Chrome Driver with the correct Service object
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Open Naukri.com
driver.get("https://www.naukri.com/")

def login(email, passw):
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
        print("Login failed:", e)

def share_interest_task():
    total_shared_interest = 0
    try:
        # click on early-access button
        early_acc_view_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "spc__view-all"))
        )
        early_acc_view_btn.click()

        time.sleep(1)
        # Wait for the parent container to load
        """
        # tuple_list_container = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CLASS_NAME, "tuple-list-container"))
        # )
        """
        
        # Get all the divs with class 'tlc__tuple' within the container
        tuple_divs = driver.find_elements(By.CLASS_NAME, "tlc__tuple")  
        if len(tuple_divs)> 0:
            # get random between 0 to len(tuple_divs)
            btn1 = tuple_divs[1].find_element(By.CLASS_NAME, "unshared")
            btn1.click()
            total_shared_interest += 1
            time.sleep(1)


            # it will redirect to other page (lets handle it separately)
            # Get all the divs with class 'tlc__tuple' within the container
            article_divs = driver.find_elements(By.CLASS_NAME, "s2jTuple")
            if len(article_divs)>0:
                for article in article_divs:
                    try:
                        article.find_element(By.CLASS_NAME, "share-interest").click()
                        time.sleep(0.2)
                        total_shared_interest += 1
                    except:
                        pass
            return total_shared_interest
        else:
            print("No new jobs available")
            return total_shared_interest
      
    except Exception as e:
        print("Share Interest failed:", e)

def share_interest(max_shared:int=55):
    total_shared_interest = 0
    while total_shared_interest < max_shared:
        try:
            total_shared_interest += share_interest_task()

            # Go back to home and restart the process
            driver.find_element(By.CLASS_NAME, "nI-gNb-header__logo").click()
            time.sleep(0.3)
        except Exception as e:
            print("Share Interest failed:", e)
            break
        
    return total_shared_interest


if __name__ == "__main__":
    """  
    use wisely, it will not make in interest to exlpliot someone.
    """
    print("creds loading...")
    email = config("email")
    passw = config("passw")

    login(email, passw)
    print("Share Interest...")
    total_shared_interest = share_interest(56)
    print("Total Shared Interest:", total_shared_interest)
    driver.quit()
    print("Done")