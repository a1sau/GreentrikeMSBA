import requests
from bs4 import BeautifulSoup as bs
from time import sleep
from random import randint
import re
import csv
from datetime import datetime
import censusgeocode as cg


#Header information
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}


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
    count=0
    Buildings = []
    for list in url_list:
        for item in list:
            count += 1
            site_facts = {}
            url = "{}".format(item)  # Puts the list link in the loop
            r = requests.get(url, headers=headers)
            page_soup = bs(r.content, features="html.parser")
            site_facts['CS_ID'] = 'LN-' + url[-9:-1]
            site_facts['url'] = url  # Adds the url to the dictonary
            loc = page_soup.find("h1", class_="breadcrumbs__crumb breadcrumbs__crumb-title") # Finds the address on page.
            try:    #If location doesn't have address, go to next item)
                loc = loc.get_text()
            except Exception as err:
                continue
            check = loc[-5:].isdigit()  #Checks to see if the postal code is in the address
            if check:
                a1 = loc.split(", ")
                # Get AddressLine
                site_facts['AddressLine'] = a1[0]
                # Get City
                site_facts['City'] = a1[1]
                # Get State
                site_facts['State'] = a1[2][0:2]
                # Get Zip
                site_facts['PostalCode'] = a1[2][-5:]
                geocode = cg.address(street=site_facts['AddressLine'],city=site_facts['City'],state=site_facts['State'],zipcode=site_facts['PostalCode'])
                try:
                    GEOID = geocode[0]['geographies']['Census Tracts'][0]['GEOID']
                    site_facts['GeoCode'] = GEOID
                    print(count, site_facts['AddressLine'], site_facts['City'], GEOID)
                except Exception as err:
                    pass
            else:
                site_facts['AddressLine'] = loc
                site_facts["City"] = "N/A"
                site_facts['State'] = "N/A"
                site_facts['PostalCode'] = "N/A"
            is_column = bool(page_soup.find("div", {
                "class": "property-facts__labels-one-col"}))  # Test to see how the data is formated on the listing page.
            if is_column == True:  # This loop is used when the listing uses columns.
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
                # Get Property Type
                if 'Property Type' in property_info:
                    site_facts['PropertyType'] = property_info['Property Type']
                else:
                    site_facts['PropertyType'] = "N/A"
                # Get price
                if 'Price' in property_info:
                    site_facts['Price'] = property_info['Price']
                else:
                    site_facts['Price'] = "N/A"
                # Get Square Foot
                if 'Building Size' in property_info:
                    site_facts['SquareFeet'] = property_info['Building Size']
                else:
                    site_facts['SquareFeet'] = "N/A"
                # Get Building Class
                if 'Building Class' in property_info:
                    site_facts['BuildingClass'] = property_info['Building Class']
                else:
                    site_facts['BuildingClass'] = "N/A"
                # Get Year Built
                if 'Year Built' in property_info:
                    site_facts['YearBuilt'] = property_info['Year Built']
                elif 'Year Built/Renovated' in property_info:
                    site_facts['YearBuilt'] = property_info['Year Built/Renovated']
                else:
                    site_facts['YearBuilt'] = "N/A"
                # Get Sale Type
                if 'Sale Type' in property_info:
                    site_facts['SaleType'] = property_info['Sale Type']
                else:
                    site_facts['SaleType'] = "N/A"
                Buildings.append(site_facts)    #Append the this loop to the buildings list
                sleep(randint(2, 3))
            if is_column == False:  # This loop is used when the listing is in a table.
                table = page_soup.table
                table_data = table.find_all('td')
                t_list = []
                temp_dict = {}
                for td in table_data:
                    strip_td = (re.sub(r"[\n \r\t]*", "", td.get_text()))
                    t_list.append(strip_td)
                temp_dict = {t_list[i]: t_list[i + 1] for i in
                             range(0, len(t_list), 2)}  # Turns the list into a dictionary
                if 'PropertyType' in temp_dict:
                    site_facts['PropertyType'] = temp_dict['PropertyType']
                else:
                    site_facts['PropertyType'] = "N/A"
                # Get price
                if 'Price' in temp_dict:
                    site_facts['Price'] = temp_dict['Price']
                else:
                    site_facts['Price'] = "N/A"
                # Get Square Foot
                if 'BuildingSize' in temp_dict:
                    site_facts['SquareFeet'] = temp_dict['BuildingSize']
                if 'TotalBuildingSize' in temp_dict:
                    site_facts['SquareFeet'] = temp_dict['TotalBuildingSize']
                if 'UnitSize' in temp_dict:
                    site_facts['SquareFeet'] = temp_dict['UnitSize']
                if 'RentableBuildingArea' in temp_dict:
                    site_facts['SquareFeet'] = temp_dict['RentableBuildingArea']
                else:
                    site_facts['SquareFeet'] = "N/A"
                # Get Building Class
                if 'BuildingClass' in temp_dict:
                    site_facts['BuildingClass'] = temp_dict['BuildingClass']
                else:
                    site_facts['BuildingClass'] = "N/A"
                # Get Year Built
                if 'YearBuilt/Renovated' in temp_dict:
                    site_facts['YearBuilt'] = temp_dict['YearBuilt/Renovated']
                elif 'YearBuilt' in temp_dict:
                    site_facts['YearBuilt'] = temp_dict['YearBuilt']
                else:
                    site_facts['YearBuilt'] = "N/A"
                # Get Sale Type
                if 'SaleType' in temp_dict:
                    site_facts['SaleType'] = temp_dict['SaleType']
                else:
                    site_facts['SaleType'] = "N/A"
                Buildings.append(site_facts)
                sleep(randint(2, 3))
    return Buildings


def buildings_export(property_info):
    export_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
    with open('loopnet_listings_{}.csv'.format(export_time), 'w', newline='\n') as f:
        w = csv.DictWriter(f, property_info[0].keys())
        w.writeheader()
        for i in property_info:
            w.writerow(i)
    f.close()


def main():
    print('Grab placards')
    url_list = grab_placards()
    listing_count = 0
    for list in url_list:
        listing_count += len(list)
    print('Found {} urls'.format(listing_count))
    print('Checking Listings')
    property_info = listing_info(url_list)
    print('Export list to file')
    buildings_export(property_info)

#Todo make function to convert to csv

if __name__ == '__main__':
    main()
