# !pip install selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import requests
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

global websites
websites = []

def sign_in(email,password):
    global driver
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    # driver.maximize_window()
    driver.get("https://www.linkedin.com/login")
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys(email)  #it has been blocked, you can not use anymore.
    password.send_keys(password)
    password.send_keys(Keys.RETURN)

    # Wait for the home page to load
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
    )
    
    return driver


def give_keywords(title,location):
    import re
    jobs_link = driver.find_element(By.XPATH, '//a[contains(@href, "/jobs/")]')
    jobs_link.click()
    time.sleep(5)
    search_bar = driver.find_element(By.XPATH, '//input[@aria-label="Search by title, skill, or company"]')
    search_bar.clear()
    search_bar.send_keys(title)
    time.sleep(3)
    location_search_bar = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="City, state, or zip code"]')
    location_search_bar.click()
    location_search_bar.clear()
    location_search_bar.send_keys(location)
    time.sleep(3)
    location_search_bar.send_keys(Keys.ENTER)
    time.sleep(5)

    global current_url
    current_url = driver.current_url
    # driver.close()
    

    return current_url



def handle_subtitle_error(driver):
    try:
        subtitle_element = driver.find_element(By.CLASS_NAME, 'main__subtitle')
        if subtitle_element.text == 'Make the most of your professional life':
            # Perform the back-click action if the condition is met
#             websites.append("Error occured page")
            driver.close()
            return True
    except NoSuchElementException:
        pass
    return False

def click_apply_button(url):
    try:
        driver1 = webdriver.Chrome(executable_path='chromedriver.exe')
        driver1.implicitly_wait(5)
        driver1.get(url)
        # Store the current window handle
        current_window_handle = driver1.current_window_handle

        apply_button = driver1.find_elements(By.XPATH, '//button[contains(text(), "Apply")]')
        apply_button[0].click()
        time.sleep(2)

        skip_link = driver1.find_elements(By.XPATH, '//a[contains(text(), "Apply on company website")]')

        if skip_link:
            skip_link[0].click()
            time.sleep(4)

        # Wait for the new window to open
        WebDriverWait(driver1, 10).until(lambda d: len(d.window_handles) > 1)

        # Switch to the new window
        driver1.switch_to.window(driver1.window_handles[-1])

        # Get the URL of the new page
        new_page_url = driver1.current_url

        # Close the new window
        driver1.close()

        # Switch back to the original window
        driver1.switch_to.window(current_window_handle)

        websites.append(new_page_url)
        print(new_page_url)
        
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException, IndexError) as e:
        websites.append("Error occured page")
        print(f"Encountered error: {e}")

        # Handle the subtitle error
        if handle_subtitle_error(driver1):
            return 0

    return websites

def scroll_to_bottom(driver, n):
    prev_height = driver.execute_script("return document.body.scrollHeight")
    click_counter = 0
    
    while True:
        # Scroll to the bottom of the page
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait for the page to load and elements to be visible
        time.sleep(7)

        # Check if the page height has remained the same
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == prev_height:
            # Check if the "See more jobs" button is present
            see_more_button = driver.find_elements(By.CLASS_NAME, 'infinite-scroller__show-more-button')
            if see_more_button:
                try:
                    # Wait for the button to become interactable
                    wait = WebDriverWait(driver, 20)  # Increased timeout duration to 20 seconds
                    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'infinite-scroller__show-more-button')))

                    # Click the "See more jobs" button
                    see_more_button[0].click()
                    # Wait for the additional content to load
                    time.sleep(5)
                    # Update the page height
                    prev_height = driver.execute_script("return document.body.scrollHeight")

                    click_counter += 1
                    if click_counter == n:
                        break
                    continue  # Continue scrolling

                except TimeoutException:
                    # Handle TimeoutException by breaking out of the loop
                    break

        prev_height = new_height

   
    

def scrapping(url):
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    driver.implicitly_wait(5)
    driver.get(url)
    
    scroll_to_bottom(driver, 30) #you may change 30 as well.


    y = driver.find_elements(By.CLASS_NAME, 'results-context-header__job-count')[0].text
    value_str = y.replace(",", "").replace("+", "")
    n = int(value_str)



    title_elements = driver.find_elements(By.CLASS_NAME, 'base-search-card__title')
    for title_element in title_elements:


        actions = ActionChains(driver)
        actions.move_to_element(title_element).click().perform()

        time.sleep(5)

        href = driver.current_url

        click_apply_button(href)


        driver.switch_to.default_content()

        actions = ActionChains(driver)
        actions.move_to_element(title_element).send_keys(Keys.DOWN).perform()

        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, 'base-search-card__title')))


    return len(urls)

def saving_list_as_txt(list):

    list = [item for item in list if item != "Error occurred page"]
    
    # Write  list to a text file
    with open("output.txt", "w") as file:
        for item in list:
            file.write(item + "\n")
            
#sign_in("Your email","Your passport")
#give_keywords("Data","USA")
#scrapping(current_url)
scrapping("https://www.linkedin.com/jobs/search/?currentJobId=3620838694&geoId=103644278&keywords=marketing&location=United%20States&refresh=true") #if you disable sign in function 
saving_list_as_txt(websites)





