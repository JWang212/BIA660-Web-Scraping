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
links = soup.find_all('td')

# Use regular expression to extract domains seperately
#'title=".+?">([.].+?)</a>'+'<td>([.].*?)</td>'  Can I put 2 patterns in one formulas?
pattern_1 = re.compile('<td>([.].+?)</td>')
pattern_2 = re.compile('title=".+?">([.].+?)</a>')
list_1 = re.findall(pattern_1,str(links))
list_2 = re.findall(pattern_2,str(links))

# To check if there's unnecessary extraction
#print(list_1)
#print(list_2)

# Eliminate unnecessary extraction
del list_1[0:2] 
del list_1[16]

# Combine the two lists
domain_list = list_1 + list_2

# Write domains list into file
with open('domains_list.csv','w',encoding='utf-8') as csv_file1:
    writer = csv.writer(csv_file1)
    for i in domain_list:
        writer.writerow([i])

# Write check result into file
with open('example_domain.csv','w',encoding='utf-8') as csv_file2:
    writer = csv.writer(csv_file2)
    for i in domain_list:
        try:
            response = requests.get("http://example"+i)
            example_domain = {"example"+i:response.status_code}
            print(example_domain)
        except RequestException:    # RequestException includes all exceptions
            example_domain = {"example"+i:"error"}
            print(example_domain)
        writer.writerow([example_domain])
    
