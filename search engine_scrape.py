#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 14:59:50 2019

@author: jinghaowang
"""

''' 660 Project - Search Engine - Scraping '''




import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time     
import csv


'''''''''''''''''''''''''''' Read data and create 2 lists and 1 dictionary '''''''''''''''''''''''''''''''''''

df = pd.read_excel('SP500.xlsx', usecols=[1,2])

full_name = list(df.Company)  # size: 507

ticker = list(df.Symbol)  # size: 507

fullname_ticker_dic = dict(zip(full_name, ticker))  # {key:fullname, value:ticker}



'''''''''''''''''''''''''''' Scrape links and articles from NYTIMES '''''''''''''''''''''''''''''''''''''''''

ticker_link_ny = {}  # {key:ticker, value:link}

link_text_ny = {}  # {key:link, value:text}

link_ny = []  # Create a list to store scraped links and deduplicate later


# Scrape links

m = 0  # Count the number of loop

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

for i in ticker:
    
    #if m < 10:

        try:
            
            print(i)
            
            #m = m + 1
        
            ticker_link_ny[i] = []  # Create list for each value in the ticker_link dictionary
            
            url = 'https://www.nytimes.com/search?query=' + i  
            
            driver.get(url)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            link = soup.find_all('a')
            
            ''' nytimes can recogonize some tickers. If a ticker is recognized, there'll be a link at the top
            which can link to the second page that is specifically for the company, then we can scrape links 
            from the second page, which is more accurate. If a ticker is not recognized, we scrape links 
            from the first page. The difference is that sometimes results obtained by searching ticker are not 
            very accurate. '''
            
            # When ticker recognized, we can match this pattern and find the redirect link.
            pattern = re.compile('"(https://www.nytimes.com/topic/company/.*?)\?searchResultPosition=0"')
            link_redirect_ny = re.findall(pattern, str(link))
            print(link_redirect_ny)
            
            if len(link_redirect_ny) == 0: # len = 0 means ticker is not recognized.
                
                # Because seaching ticker is not accurate in this case, we seach fullname
                # Get fullname by ticker from the fullname_ticker_dic
                fullname = list(fullname_ticker_dic.keys())[list(fullname_ticker_dic.values()).index(i)]
                print(fullname)
                
                url = 'https://www.nytimes.com/search?query=' + fullname
                
                driver.get(url)
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                link = soup.find_all('a')
                
                pattern = re.compile('<a href="(/2019/11/2[56789]/.*?\.html)')
                link_ny_compiled = re.findall(pattern, str(link))
                print(link_ny_compiled)
                
                for link in link_ny_compiled:
                    link = 'https://www.nytimes.com' + link  # Complete the url
                    link_ny.append(link)  # Put url in the list
                    ticker_link_ny[i].append(link)  # Put url in ticker:link dictionary
                
            else: # len != 0 means ticker is recognized.
                
                url = link_redirect_ny[0] 

                driver.get(url)
                    
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                link = soup.find_all('a')
                
                pattern = re.compile('<a href="(/2019/11/2[56789]/.*?\.html)')
                link_ny_compiled = re.findall(pattern,str(link))
                print(link_ny_compiled)
                
                if link_ny_compiled is not None:
                    for link in link_ny_compiled:
                        link = 'https://www.nytimes.com' + link
                        link_ny.append(link)
                        ticker_link_ny[i].append('https://www.nytimes.com' + link)
                
        except Exception:
            print("continue")


# Save ticker:link dictionary as csv file

csv_file1 = "ticker_link_ny.csv"

with open(csv_file1, 'w', newline='') as csvfile:
    fieldnames = ['ticker', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in ticker_link_ny.items():
        writer.writerow({'ticker': i, 'link': j})


# Deduplicate links
link_ny_dedup = list(set(link_ny))


# Scrape articles

m = 0

for i in link_ny_dedup:
    
    print(m)
    
    m = m + 1
    
    url = i
    
    driver.get(url)
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text = soup.find_all('p')
    
    pattern = re.compile('<p class=\".*?\">(.*?)</p>')
    text = re.findall(pattern,str(text))
    
    text = re.sub('<strong.*?</strong>:','',str(text))
    text = re.sub('<a.*?</a>','',str(text))
    text = re.sub('<span.*?</span>','',str(text))
    text = re.sub('<em.*?</em>','',str(text))
    text = re.sub('<img.*?/>','',str(text))
    text = re.sub('<!-- -->','',str(text))
    text = re.sub('Support independent journalism', '', str(text))

    link_text_ny[i] = text  


# Save link:text dictionary as csv file

csv_file2 = "link_text_ny.csv"

with open(csv_file2, 'w', newline='') as csvfile:
    fieldnames = ['link', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in link_text_ny.items():
        writer.writerow({'link': i, 'text': j})
    
    

'''''''''''''''''''''''''''''''Scrape links and articles from Seekingalpha '''''''''''''''''''''''''''''''''

ticker_link_alpha = {}

link_text_alpha = {}

link_alpha = []


# Scrape links

m = 0

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

for i in ticker:
    
    try:
        
        #if m < 5:
            
            m = m + 1
            
            print(m, i)
            
            ticker_link_alpha[i] = []
    
            url = 'https://seekingalpha.com/symbol/' + i
    
            driver.get(url)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            link = soup.find_all('a')
            
            # Only scrape 'news' session; 'analysis' article is too subjective. 
            pattern_news = re.compile('<a href="(/news/.*?)"')
            link_alpha_compiled = re.findall(pattern_news, str(link))
            
            ''' Links on seekingalpha don't have datestamp, instead datestamps are in a tag near to the 
            link tag. So, to only scrape articles published on 25/26/27/28/29, we find the number as to 
            how many 25, 26, 27, 28, 29 there are on the page, and scrape this number of links. It's 
            confirmed that the number of links and datestamps on the page is the same. '''
            
            span = soup.find_all('span') # Datestamp is stored in span tag.
            
            pattern_datetime = re.compile('<span>SA News</span>.*?Nov\. 2[56789]</span>')
            datetime = re.findall(pattern_datetime, str(span))
            
            num_link_needed = len(datetime) # Get the number of 25, 26, 27, 28, 29

            n = 0
                
            for link in link_alpha_compiled:
                
                if n < num_link_needed: # Scrape this number of links
                    
                    link = 'https://seekingalpha.com'+ link
                    link_alpha.append(link)
                    ticker_link_alpha[i].append(link)
                    
                    n = n + 1
                
                    #print(link_alpha)
    
    except Exception:
        print("continue")


# Save ticker:link dictionary as csv file
        
csv_file3 = "ticker_link_alpha.csv"

with open(csv_file3, 'w', newline='') as csvfile:
    fieldnames = ['ticker', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in ticker_link_alpha.items():
        writer.writerow({'ticker': i, 'link': j})
    

# Deduplicate links    
link_alpha_dedup = list(set(link_alpha)) 


# Scrape articles

m = 0

for i in link_alpha_dedup:
    
    try:
        
        m = m + 1
        print(m)
    
        url = i
        
        driver.get(url)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text = soup.find_all('p')
        
        pattern_text = re.compile('<p class=\".*?\">(.*?)</p>')
        text = re.findall(pattern_text,str(text))
        
        text = re.sub('<strong.*?</strong>','',str(text))
        text = re.sub('<a.*?</a>','',str(text))
        text = re.sub('<b.*?</b>','',str(text))
        text = re.sub('<span.*?</span>','',str(text))
        text = re.sub('<em.*?</em>','',str(text))
        text = re.sub('<img.*?/>','',str(text))
        text = re.sub('<!-- -->','',str(text))
            
        link_text_alpha[i] = text
    
    except Exception:
        continue

    
# Save link:text dictionary as csv file
        
csv_file4 = "link_text_alpha.csv"

with open(csv_file4, 'w', newline='') as csvfile:
    fieldnames = ['link', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in link_text_alpha.items():
        writer.writerow({'link': i, 'text': j})



'''''''''''''''''''''''''''''''Scrape links and articles from Bloomberg '''''''''''''''''''''''''''''''''

ticker_link_blbg = {}

link_text_blbg = {}

link_blbg = []

text_blbg = []


# Scrape links

m = 0

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

for i in full_name:
    
    try:
        
        m = m + 1
        
        print(m, i)
            
        ticker_link_blbg[fullname_ticker_dic[i]] = []

        url = 'https://bloomberg.com/search/?query=' + i  
    
        driver.get(url)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link = soup.find_all('a')
        
        pattern = re.compile('<a.*?href=\"(https://www.bloomberg.com/news/articles/2019-11-2[56789].*?)\".*?</a>')
        link_blbg_compiled = re.findall(pattern, str(link))
        
        for link in link_blbg_compiled:
            link = link
            link_blbg.append(link)
            ticker_link_blbg[fullname_ticker_dic[i]].append(link)
    
    except Exception:
        print("continue")


# Save ticker:link dictionary as csv file
        
csv_file5 = "ticker_link_blbg.csv"

with open(csv_file5, 'w', newline='') as csvfile:
    fieldnames = ['ticker', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in ticker_link_blbg.items():
        writer.writerow({'ticker': i, 'link': j})


# Deduplicate links
link_blbg_dedup = list(set(link_blbg))


# Scrape articles

for i in link_blbg_dedup:
    
    try:
        
        print(link_blbg_dedup.index(i))
        
        url = i
        
        driver.get(url)
        
        #time.sleep(3) 
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text = soup.find_all('p')
        
        pattern = re.compile('<p(.*?)</p>')
        text = re.findall(pattern, str(text))

        text = re.sub('<strong.*?</strong>:?','',str(text))
        text = re.sub('<a.*?</a>','',str(text))
        text = re.sub('aria-hidden="true" style="display: none;">', '',str(text))
        text = re.sub('(class=|Escape).*?window.','',str(text))
        text = re.sub('<em.*?</em>','',str(text))
        text = re.sub('<img.*?/>','',str(text))
        text = re.sub('<b.*?</b>','',str(text))
        text = re.sub('<span.*?</span>','',str(text))

        link_text_blbg[i] = text
    
    except Exception:
        print("continue")


# Save link:text dictionary as csv file
        
csv_file6 = "link_text_blbg.csv"

with open(csv_file6, 'w', newline='') as csvfile:
    fieldnames = ['link', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in link_text_blbg.items():
        writer.writerow({'link': i, 'text': j})



'''''''''''''''''''''''''''''''Scrape links and articles from WallStreetJournal '''''''''''''''''''''''''''''''''

ticker_link_wsj = {}

link_text_wsj = {}

link_wsj = []


# Scrape links

m = 0

driver = webdriver.Chrome('/usr/local/bin/chromedriver')

for i in ticker:

    try:
        
        m = m + 1
            
        print(m)
            
        ticker_link_wsj[i] = []
    
        url = 'https://quotes.wsj.com/' + i
        
        driver.get(url)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        link = soup.find_all('a')

        pattern1_link = re.compile('<a href="(https*://www.wsj.com/articles/PR-CO-2019112[56789].*?)" target="_blank">.*?</a>')
        pattern2_link = re.compile('<a href="(https*://www.marketwatch.com/story/.*?-2019-11-2[56789])" target="_blank">.*?</a>')
        link_wsj_compiled1 = re.findall(pattern1_link,str(link))
        link_wsj_compiled2 = re.findall(pattern2_link,str(link))
        link_wsj_compiled = link_wsj_compiled1 +link_wsj_compiled2
        print(link_wsj_compiled)
                
        for link in link_wsj_compiled:
            link_wsj.append(link)
            ticker_link_wsj[i].append(link)
            print(len(ticker_link_wsj[i]))

    except Exception:
        continue
        print ("continue")


# Save ticker:link dictionary as csv file
        
csv_file7 = "ticker_link_wsj.csv"

with open(csv_file7, 'w', newline='') as csvfile:
    fieldnames = ['ticker', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in ticker_link_wsj.items():
        writer.writerow({'ticker': i, 'link': j})


# Deduplicate links
link_wsj_dedup = list(set(link_wsj))


# Scrape articles

m = 0

for i in link_wsj_dedup[220:]:
    
    print(m)

    url = i

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    text = soup.find_all('p')

    pattern = re.compile('<p(.*?)</p>')
    text = re.findall(pattern, str(text))  
    
    text = re.sub('<p class=.*?</p>','',str(text))
    text = re.sub('<span.*?</span>:?','',str(text))
    text = re.sub('<strong.*?</strong>:?','',str(text))

    print(text)

    link_text_wsj[i] = text
    
    m = m + 1


# Save link:text dictionary as csv file

csv_file8 = "link_text_wsj.csv"

with open(csv_file8, 'w', newline='') as csvfile:
    fieldnames = ['link', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in link_text_wsj.items():
        writer.writerow({'link': i, 'text': j})


''''''''''''''''''''''''''''''''''''''''''' Combine all into one '''''''''''''''''''''''''''''''''''''''''''

# Save all dictionaries into one dictionary and save it as a csv file

def merg_dic(x,y):
    for i,j in y.items():
        if i in x.keys():
            x[i] += j
        else:
            x[i] = j

# Combine ticker_link dictionaries

ticker_link_all = {}

merg_dic(ticker_link_all, ticker_link_ny)
merg_dic(ticker_link_all, ticker_link_alpha)
merg_dic(ticker_link_all, ticker_link_blbg)
merg_dic(ticker_link_all, ticker_link_wsj)


# Save ticker_link dictionary as csv file

csv_file9 = "ticker_link_all.csv"

with open(csv_file9, 'w', newline='') as csvfile:
    fieldnames = ['ticker', 'link']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in ticker_link_all.items():
        writer.writerow({'ticker': i, 'link': j})

# Combine link_text dictionaries
    
link_text_all = {}

merg_dic(link_text_all, link_text_ny)
merg_dic(link_text_all, link_text_alpha)
merg_dic(link_text_all, link_text_blbg)
merg_dic(link_text_all, link_text_wsj)    


# Save link_text dictionary as csv file

csv_file10 = "link_text_all.csv"

with open(csv_file10, 'w', newline='') as csvfile:
    fieldnames = ['link', 'text']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for i,j in link_text_all.items():
        writer.writerow({'link': i, 'text': j})
        
        
        

'''
q1:
seekingalpha can't show links
go to other links

q2:
wsj requires subscription
go to library.school

q3:
how to pass robot test
no good way

q4:
how to sort by time
datetime module

q5:
how to create automatic update script
cron
do in a while loop

q6:
how to do search similarity
auto spell checking

additional:
wsj:how to filter irrelavant page
'''





