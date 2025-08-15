from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def open_google_and_search(query):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.google.com")
    search_box = driver.find_element("name", "q")
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(5)
    driver.quit()

if __name__ == "__main__":
    open_google_and_search("latest news")
