import os
import requests
import zipfile
import sys
from selenium import webdriver

def setup_chromedriver():
    """Automatically download and setup ChromeDriver"""
    try:
        # Get Chrome version
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        chrome_version = driver.capabilities['browserVersion']
        driver.quit()
        
        print(f"Detected Chrome version: {chrome_version}")
        
        # Download matching ChromeDriver
        major_version = chrome_version.split('.')[0]
        download_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        
        response = requests.get(download_url)
        chromedriver_version = response.text.strip()
        
        download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_win32.zip"
        
        # Download and extract
        print("Downloading ChromeDriver...")
        response = requests.get(download_url)
        
        with open("chromedriver.zip", "wb") as f:
            f.write(response.content)
        
        with zipfile.ZipFile("chromedriver.zip", "r") as zip_ref:
            zip_ref.extractall("./drivers/")
        
        # Cleanup
        os.remove("chromedriver.zip")
        print("ChromeDriver setup completed successfully")
        
    except Exception as e:
        print(f"Automatic ChromeDriver setup failed: {e}")
        print("Please download ChromeDriver manually from: https://chromedriver.chromium.org/")