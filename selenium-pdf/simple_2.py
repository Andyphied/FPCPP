from selenium import webdriver
from pathlib import (
    Path,
)  # -> pathlib is a module that provides an object-oriented interface for working with the filesystem
from time import sleep

webdriver = webdriver.Chrome()
html_file = (
    Path.cwd() / "selenium-pdf/test.html"
)  #  -> Path.cwd() returns the current working directory
webdriver.get(html_file.as_uri())  # -> as_uri() returns the file path as a URI
sleep(10)
