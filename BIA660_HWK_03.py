# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 10:51:51 2019

@author: sszz
"""

# Import libraries.
import time
import queue
import re
import os
from urllib.parse import urlparse
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver

# Define a function to deternmine whether URL is absolute.
def is_absolute(url):
    return bool(urlparse(url).netloc)

# Launch Chromedriver.
driver = webdriver.Chrome(executable_path='C:/Users/sszz/Documents/Python Scripts/chromedriver.exe')

# Create a queue in form of FIFO.
q = queue.Queue()
q.put("https://www.stevens.edu")

# Create a list for email addresses.
email_addresses = []

# Creat a list for URL deduplication.
url_list = []
url_list.append("https://www.stevens.edu")

# Crawl all URLs.
# for i in range(5000):
while(not q.empty()):

    # Get URL from the queue. If a url raises exception, remove it from the queue.
    try:
        url = q.get()
        print(url)
        driver.get(url) # Open URL in Chrome.
    except Exception:
        continue
        
    # Set crawl delay to 1 second.
    time.sleep(1)
    
    # Remove characters that can't exist in a file name.
    url_str = str(url)
    url_str = url_str.replace("https://","")
    url_str = url_str.replace("http://","")
    url_str = url_str.replace("?","")
    url_str = url_str.replace("\\","")
    url_str = url_str.replace("*","")
    url_str = url_str.replace("<","")
    url_str = url_str.replace(">","")
    url_str = url_str.replace(":","")
    url_str = url_str.replace("\"","")
    
    # Save directory structure into disk, set exist_ok as 'True' to avoid exception.
    os.makedirs(url_str, exist_ok=True)
    
    # Parse the page
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Extract all email addresses.
    email_addresses += re.findall("\S+@stevens.edu", soup.get_text())
    email_addresses = list(set(email_addresses))
    
    # Extract all URLs from a crawled URL, and deduplicate existed URLs
    links = soup.find_all('a')
    for link in links:
        u = link.get('href')
        if not is_absolute(u):
            u = urljoin(url, u)
            u_if = urlparse(u) # Change the type of u into urlparse for the if test below.
            if "www.stevens.edu" in u_if.netloc: # Avoid external URLs like "www.facebook.com/...www.stevens.edu...".
                if u not in url_list: # Deduplicate
                    url_list.append(u) 
                    q.put(u)

# Write email addresses to file
with open("email.txt", "w+") as f:
    for e in email_addresses:
        f.write(e + "\n")
    
