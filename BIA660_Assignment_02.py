#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 00:03:37 2019

@author: jinghaowang
"""
# import packages
import requests
import re
import csv
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

# Extract and parse content from the website
url = 'https://en.m.wikipedia.org/wiki/List_of_Internet_top-level_domains'
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')

# Use regular expression to extract domains
pattern = re.compile('title=".*?">([.].*?)</a>')
soup = str(soup)
domains_extracted = re.findall(pattern, soup)

# To check if there's unnecessary extraction
print(domains_extracted)

# Eliminate unnecessary extraction
domains_extracted = domains_extracted[:-1]

# Write extracted domains into file
with open('domains_extract_result.csv','w',encoding='utf-8') as csv_file1:
    writer = csv.writer(csv_file1)
    for i in domains_extracted:
        writer.writerow([i])

# Write check result into file
with open('domains_check_result.csv', 'w',encoding='utf-8') as csv_file2:
    writer = csv.writer(csv_file2)
    for i in domains_extracted:
        try:
            response = requests.get("http://example"+i)
            domains_checked = {i:response.status_code}
            print(domains_checked)
        except RequestException:    # RequestException includes all exceptions
            domains_checked = {i:'error'}
            print(domains_checked)
        writer.writerow([domains_checked])
