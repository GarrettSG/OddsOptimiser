import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By


# takes html input of string and saves it is a file pth
def save_html(html, path):
    with open(path, 'w') as f:
        f.write(html)


# opens the path file
def open_html(path):
    with open(path, 'r') as f:
        return f.read()

url = 'https://www.az.bet365.com/?_h=TapAPM35FXe3HEYrG6WHGQ%3D%3D&btsffd=1#/AC/B16/C20525425/D48/E1096/F10/'

driver = webdriver.Chrome()

driver.get(url)
time.sleep(8)
page_source = driver.page_source

# save html from FanDuel page into fanduel_page.txt
save_html(page_source, 'bet365.txt')