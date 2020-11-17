import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
import re
import csv

#Header information
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}
def grab_placards():
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
    return loopnet_links

def listing_info(url_list):
    Buildings = []
    for list in url_list:
        for item in list:
            site_facts = {}
            url = "{}".format(item)  # Puts the list link in the loop
            r = requests.get(url, headers=headers)
            page_soup = bs(r.content, features="html.parser")
            site_facts['CS_ID'] = 'LN-' + url[-9:-1]
            site_facts['url'] = url  # Adds the url to the dictonary
            address = page_soup.find("h1",
                                     class_="breadcrumbs__crumb breadcrumbs__crumb-title")  # Finds the address on page.
            site_facts['address'] = address.get_text()  # Adds the address to dictonary
            # TODO get the bool teset to work.
            bool_test = bool(page_soup.find("div", {
                "class": "property-facts__labels-one-col"}))  # Test to see how the data is formated on the listing page.
            if bool_test == True:  # This loop is used when the listing uses columns.
                ### Temp lists to store property information
                property_label = []
                property_data = []
                labels = page_soup.find("div", {"class": "property-facts__labels-one-col"}).find_all('div',
                                                                                                     recursive=False)  # Selects the child of the correct label column
                datas = page_soup.find("div", {"class": "property-facts__data-one-col"}).find_all('div',
                                                                                                  recursive=False)  # Selects the child of the correct data column
                #   These loops isolate the text from the html and put them into lists.
                for label in labels:
                    property_label.append(re.sub(r"[\n\r\t]*", "", label.get_text()))
                for data in datas:  # This loop gets the data information
                    property_data.append(
                        re.sub(r"[\n\r\t]*", "", data.get_text()))  # This removes tabs, newlines and returns
                property_info = dict(zip(property_label, property_data))  # Creates dictionary of lists
                site_facts['Property_info'] = property_info
                Buildings.append(site_facts)
                sleep(randint(2, 5))
            if bool_test == False:  # This loop is used when the listing is in a table.
                table = page_soup.table
                table_data = table.find_all('td')
                t_list = []
                for td in table_data:
                    strip_td = (re.sub(r"[\n \r \t]*", "", td.get_text()))
                    t_list.append(strip_td)
                site_facts['Property_info'] = {t_list[i]: t_list[i + 1] for i in
                                               range(0, len(t_list), 2)}  # Turns the list into a dictionary
                Buildings.append(site_facts)
                sleep(randint(2, 5))
    return Buildings

def buildings_export(property_info):
    with open('loopnet_listings.csv', 'w', newline='\n') as f:
        w = csv.DictWriter(f, property_info[0].keys())
        w.writeheader()
        for i in property_info:
            w.writerow(i)
    f.close()

def main():
    url_list = grab_placards()
    property_info = listing_info(url_list)
    buildings_export(property_info)


    #Todo make function to convert to csv

if __name__ == '__main__':
    main()
