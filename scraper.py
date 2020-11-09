import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
import re

#Header information
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}

loopnet_links = []
    ### This is what go to the search and pulls every listing url from the search page(s)
for i in range(1,7):      # Number of pages plus one
    url = "https://www.loopnet.com/search/commercial-real-estate/pierce-county-wa/for-sale/{}/".format(i)  # Looks to this URL, increasing in page numbers.
    r = requests.get(url, headers=headers)  # Gets the information from the page
    soup = bs(r.content, features="html.parser")  # Turns to bs object.
    sleep(randint(3,10))    # Sleeps so we dont get banned.
    links = soup.find_all('a', class_="subtitle-beta")  # Grabs the placard links that are NOT the featured placard TODO get the featured placard link
    loop_list=[link['href'] for link in links] # isolates the url from the html
    loopnet_links.append(loop_list) #just puts in the url into the list

property_label = []
property_data = []

    ### Loop over every page in list
for list in loopnet_links:
    for item in list:
        url = "{}".format(item)  #Puts the list link in the loop
        r = requests.get(url, headers=headers)
        page_soup = bs(r.content, features="html.parser")
        temp_label = page_soup.select('.property-facts__labels-item')  # This is the labels of information
        temp_data = page_soup.select('.property-facts__data-item')  # This is the data for the labels
        for item in temp_label: # This loop gets the label information
            text_item = item.get_text()  # This gets just the text from the html
            property_label.append(re.sub(r"[\n\r\t]*", "", text_item))  # This removes tabs, newlines and returns
        for item in temp_data:  #This loop gets the data information
            data_item = item.get_text()  # This gets just the text from the html
            property_data.append(re.sub(r"[\n\r\t]*", "", data_item))  # This removes tabs, newlines and returns
        sleep(randint(2,8)) #Sleeps before going to next page

# TODO combine property labels and data with url they came from 

# TODO export property labels & data

print(property_label) #Sanity check prints
print(property_data)