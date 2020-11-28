import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
import re
import pandas as pd
# Header info
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}

links_test_one = [['https://www.loopnet.com/Listing/7714-176th-St-Puyallup-WA/19219393/', 'https://www.loopnet.com/Listing/808-N-2nd-St-Tacoma-WA/21423976/'],['https://www.loopnet.com/Listing/3906-S-74th-St-Tacoma-WA/21355235/', 'https://www.loopnet.com/Listing/120-136th-St-S-Tacoma-WA/21333154/']]

Buildings = []
for list in links_test_one:
    for item in list:
        site_facts = {}
        url = "{}".format(item)  # Puts the list link in the loop
        r = requests.get(url, headers=headers)
        page_soup = bs(r.content, features="html.parser")
        site_facts['CS_ID'] = 'LN-' + url[-9:-1]
        site_facts['url'] = url      # Adds the url to the dictonary
        address = page_soup.find("h1", class_="breadcrumbs__crumb breadcrumbs__crumb-title")    # Finds the address on page.
        site_facts['address'] = address.get_text()   # Adds the address to dictonary
        #TODO get the bool teset to work.
        bool_test = bool(page_soup.find("div", {"class": "property-facts__labels-one-col"}))    # Test to see how the data is formated on the listing page.
        if bool_test == True:   # This loop is used when the listing uses columns.
        ### Temp lists to store property information
            property_label = []
            property_data = []
            labels= page_soup.find("div", {"class": "property-facts__labels-one-col"}).find_all('div', recursive=False)  # Selects the child of the correct label column
            datas = page_soup.find("div", {"class": "property-facts__data-one-col"}).find_all('div', recursive=False)    # Selects the child of the correct data column
            #   These loops isolate the text from the html and put them into lists.
            for label in labels:
                property_label.append(re.sub(r"[\n\r\t]*", "", label.get_text()))
            for data in datas:  # This loop gets the data information
                property_data.append(re.sub(r"[\n\r\t]*", "", data.get_text()))  # This removes tabs, newlines and returns
            property_info = dict(zip(property_label, property_data))   # Creates dictionary of lists
        # Get Property Type
            site_facts['Property Type'] = property_info['Property Type']
        # Get price
            site_facts['Price'] = property_info['Price']
        # Get Square Foot
            site_facts['Square Feet'] = property_info['Building Size']
        # Get Building Class
            site_facts['Building Class'] = property_info['Building Class']
        # Get Year Built
            site_facts['Year Built'] = property_info['Year Built']
        # Get Sale Type
            site_facts['Sale Type'] = property_info['Sale Type']
            Buildings.append(site_facts)
            sleep(randint(2,5))
        if bool_test == False:  # This loop is used when the listing is in a table.
            table = page_soup.table
            table_data = table.find_all('td')
            t_list = []
            temp_dict = {}
            for td in table_data:
                strip_td = (re.sub(r"[\n \r \t]*", "", td.get_text()))
                t_list.append(strip_td)
            temp_dict= {t_list[i]: t_list[i + 1] for i in range(0, len(t_list), 2)}  # Turns the list into a dictionary
            site_facts['Property Type'] = temp_dict['PropertyType']
            # Get price
            site_facts['Price'] = temp_dict['Price']
            # Get Square Foot
            site_facts['Square Feet'] = temp_dict['BuildingSize']
            # Get Building Class
            site_facts['Building Class'] = temp_dict['BuildingClass']
            # Get Year Built
            if 'YearBuilt/Renovated' in temp_dict:
                site_facts['Year Built'] = temp_dict['YearBuilt/Renovated']
            else:
                site_facts['Year Built'] = temp_dict['YearBuilt']
            # Get Sale Type
            site_facts['Sale Type'] = temp_dict['SaleType']
            Buildings.append(site_facts)
            sleep(randint(2,5))
for building in Buildings:
    print(building)