#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# !pip install pandas
# !pip install selenium
import pandas as pd
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
import pandas as pd
from bs4 import BeautifulSoup
import requests


def sign_in():
    global driver
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    # driver.maximize_window()
    driver.get("https://www.linkedin.com/login")
    username = driver.find_element(By.ID, "username")
    password = driver.find_element(By.ID, "password")
    username.send_keys("gmail")
    password.send_keys("password")
    password.send_keys(Keys.RETURN)

    # Wait for the home page to load
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input"))
    )
    
    
    return driver

def give_keywords(title,location):
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

global websites
websites = []


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

def scraping(url):
    driver = webdriver.Chrome(executable_path='chromedriver.exe')
    driver.implicitly_wait(5)
    driver.get(url)
    
    prev_height = driver.execute_script("return document.body.scrollHeight")

    # Scroll to the bottom of the page
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for the page to load and elements to be visible
    time.sleep(7)

    # Update the page height
    new_height = driver.execute_script("return document.body.scrollHeight")
    prev_height = new_height


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


    return n

def clean_urls(websites):
    global df
    df = pd.DataFrame({'URLs': websites})
    df = df[df['URLs'] != 'Error occured page']
    # Extract the website domain
    df['Website Domain'] = df['URLs'].apply(lambda link: urlparse(link).netloc)

    # Group by the website domain and count occurrences
    grouped = df.groupby('Website Domain').size().reset_index(name='Occurrence Count')

    # Sort by occurrence count in descending order
    sorted_grouped = grouped.sort_values('Occurrence Count', ascending=False)

    # Get the most occurring website domain
    most_occurred_website = sorted_grouped.iloc[0]['Website Domain']
    occurrence_count = sorted_grouped.iloc[0]['Occurrence Count']
    
    df = df[df['Website Domain'] != 'www.linkedin.com']

    print("Most Occurred Website:", most_occurred_website)
    print("Occurrence Count:", occurrence_count)

with open('job_titles.txt', 'r') as file:
    for line in file:
        title = line.strip()  
        current_url = give_keywords(title, "USA")
        scraping(current_url)
        
clean_urls(websites)
# Save the DataFrame as a CSV file, after saving urls they will be sorted using another code.
df.to_csv('Urls', index=False)

