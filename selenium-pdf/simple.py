from selenium import webdriver
from time import sleep

webdriver = webdriver.Chrome()
webdriver.get("https://www.google.com")
sleep(
    5
)  # Optional -> sleep() is used to pause the execution of the script for a specified amount of time in seconds (so we can see the browser window)
