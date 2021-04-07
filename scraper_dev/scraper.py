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


def grab_placards():  ## NOTE -- this only searches properties that are listed for Sale.
    loopnet_links = []
    page_number = "https://www.loopnet.com/search/commercial-real-estate/pierce-county-wa/for-sale/"
    r_page = requests.get(page_number, headers=headers)  # Gets the information from the page
    s = bs(r_page.content, features="html.parser")  # Turns to bs object.
    t_listings = s.find('span', class_="total-results-paging-digits")
    t_listings = t_listings.get_text()
    t_listings = t_listings.strip()
    t_listings = int(t_listings[-3:])
    pages = (t_listings//20) +2## uses the number of listings to determine how many pages are in the results.
    print(f"Found {t_listings} placards across {pages -1} pages.\nStarting to Collect URL's")
        ### This is what go to the search and pulls every listing url from the search page(s)
    for i in range(1,pages):      # loops equal to the number of pages in the search
        url = "https://www.loopnet.com/search/commercial-real-estate/pierce-county-wa/for-sale/{}/".format(i)  # Looks to this URL, increasing in page numbers.
        r = requests.get(url, headers=headers)  # Gets the information from the page
        soup = bs(r.content, features="html.parser")  # Turns to bs object.
        sleep(randint(3,7))    # Sleeps so we dont get banned.
        links = soup.find_all('a', class_="subtitle-beta")  # Grabs the placard links that are NOT the featured placard TODO get the featured placard link
        loop_list=[link['href'] for link in links] # isolates the url from the html
        loopnet_links.append(loop_list) #just puts in the url into the list
    return loopnet_links

def listing_info(url_list):
    count=0
    Buildings = []
    #cg = censusgeocode.CensusGeocode(benchmark='Public_AR_Current', vintage='ACS2018_Current')
    for list in url_list:
        for item in list:
            count += 1
            site_facts = {}
            url = "{}".format(item)  # Puts the list link in the loop
            r = requests.get(url, headers=headers)
            page_soup = bs(r.content, features="html.parser")
            id_array = url.split('/')# Split url to get trailing digits for Primary Key
            site_facts['CS_ID'] = "LN-" + id_array[-2]
            site_facts['url'] = url  # Adds the url to the dictonary
            loc = page_soup.find("h1", class_="breadcrumbs__crumb breadcrumbs__crumb-title") # Finds the address on page.
            try:    #If location doesn't have address, go to next item)
                loc = loc.get_text()
            except Exception as err:
                continue
            check = loc[-5:].isdigit()  #Checks to see if the postal code is in the address  #TODO change this to use .split()
            if check:
                a1 = loc.split(", ")
                # Get AddressLine
                site_facts['Address_Line'] = a1[0]
                # Get City
                site_facts['City'] = a1[1]
                # Get State
                site_facts['State'] = a1[2][0:2]
                # Get Zip
                site_facts['Postal_Code'] = a1[2][-5:]
                geocode = cg.address(street=site_facts['Address_Line'],city=site_facts['City'],state=site_facts['State'],zipcode=site_facts['Postal_Code'])
                try:
                    GEOID = geocode[0]['geographies']['2020 Census Blocks'][0]['GEOID'][0:12]
                    site_facts['bg_geo_id'] = GEOID
                    print(count, site_facts['Address_Line'], site_facts['City'], GEOID)
                except Exception as err:
                    site_facts['bg_geo_id'] = None
                    pass

            else:
                site_facts['Address_Line'] = loc
                site_facts["City"] = "N/A"
                site_facts['State'] = "N/A"
                site_facts['Postal_Code'] = "N/A"
                site_facts['bg_geo_id'] = None

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
                temp_dict1 = dict(zip(property_label, property_data))  # Creates dictionary of lists
                ##  This section grabs info from the dictionary for each listing
                # Get Property Type
                site_facts['Property_Type'] = temp_dict1.get('Property Type', 'N/A')

                # Get price
                site_facts['Price'] = temp_dict1.get('Price', None)
                if site_facts['Price'] == None:
                    pass
                elif '-' in site_facts['Price']:
                    site_facts['Price'] = None
                else:
                    temprice = site_facts['Price']
                    temprice2 = temprice.replace(',', '')
                    temprice3 = temprice2.strip('$')
                    site_facts['Price'] = int(temprice3)

                # Get Square Foot
                site_facts['SquareFeet'] = temp_dict1.get('Building Size', None)
                if site_facts['SquareFeet'] == None:
                    pass
                else:
                    tempft = site_facts['SquareFeet']
                    tempft2 = tempft.replace(',', '')
                    tempft3 = tempft2.strip('SF')
                    site_facts['SquareFeet'] = int(tempft3)

                # Get Building Class
                site_facts['Building_Class'] = temp_dict1.get('Building Class', 'N/A')


                # Get Year Built
                if 'Year Built' in temp_dict1:
                    site_facts['Year_Built'] = temp_dict1['Year Built']
                elif 'Year Built/Renovated' in temp_dict1:
                    site_facts['Year_Built'] = temp_dict1['Year Built/Renovated']
                else:
                    site_facts['Year_Built'] = "N/A"

                # #Get Parking spots
                # if 'Parking' in temp_dict1:
                #     site_facts['Parking_Ratio'] = temp_dict1['Parking']
                # elif 'Parking Ratio' in temp_dict1:
                #     site_facts['Parking_Ratio'] = temp_dict1['Parking Ratio']
                # else:
                #     site_facts['Parking_Ratio'] = 'N/A'

                # Get Sale Type
                site_facts['Sale_Type'] = temp_dict1.get('Sale Type', 'N/A')

                site_facts["Picture_url"] = "N/A"

                site_facts["Upload_Date"] = datetime.now().strftime("%Y-%m-%d")


                ## TODO Connect to AWS   HOw do you add new records?  how do you edit existing records?
                    ##

                ## TODO get links to pictures for each listing.  store url to picture within record.

                ## TODO Add currently listed to dictionary.  How will we store the urls that are not active?
                site_facts["Currently_Listed"] = False

                site_facts["Sale_Leased"] = "Sale"
                Buildings.append(site_facts)    #Append the this loop to the buildings list
                sleep(randint(5, 10))
            if is_column == False:  # This loop is used when the listing is in a table.
                table = page_soup.table
                table_data = table.find_all('td')
                t_list = []
                temp_dict2 = {}
                for td in table_data:
                    strip_td = (re.sub(r"[\n \r\t]*", "", td.get_text()))
                    t_list.append(strip_td)
                temp_dict2 = {t_list[i]: t_list[i + 1] for i in
                             range(0, len(t_list), 2)}  # Turns the list into a dictionary
                # Get Property Type
                site_facts['Property_Type'] = temp_dict2.get('PropertyType', 'N/A')

                # Get price
                site_facts['Price'] = temp_dict2.get('Price', None)
                if site_facts['Price'] == None:
                    pass
                elif '-' in site_facts['Price']:
                    site_facts['Price'] = None
                else:
                    temprice = site_facts['Price']
                    temprice2 = temprice.replace(',', '')
                    temprice3 = temprice2.strip('$')
                    site_facts['Price'] = int(temprice3)

                # Get Square Foot
                if 'BuildingSize' in temp_dict2:
                    site_facts['SquareFeet'] = temp_dict2['BuildingSize']
                if 'TotalBuildingSize' in temp_dict2:
                    site_facts['SquareFeet'] = temp_dict2['TotalBuildingSize']
                if 'UnitSize' in temp_dict2:
                    site_facts['SquareFeet'] = temp_dict2['UnitSize']
                if 'RentableBuildingArea' in temp_dict2:
                    site_facts['SquareFeet'] = temp_dict2['RentableBuildingArea']
                else:
                    site_facts['SquareFeet'] = None
                if site_facts['SquareFeet'] == None:
                    pass
                else:
                    tempft = site_facts['SquareFeet']
                    tempft2 = tempft.replace(',', '')
                    tempft3 = tempft2.strip('SF')
                    site_facts['SquareFeet'] = int(tempft3)
                    
                # Get Building Class
                site_facts['Building_Class'] = temp_dict2.get('BuildingClass', 'N/A')

                # Get Year Built
                if 'YearBuilt/Renovated' in temp_dict2:
                    site_facts['Year_Built'] = temp_dict2['YearBuilt/Renovated']
                elif 'YearBuilt' in temp_dict2:
                    site_facts['Year_Built'] = temp_dict2['YearBuilt']
                else:
                    site_facts['Year_Built'] = "N/A"

                # #Get Parking info
                # if 'Parking' in temp_dict2:
                #     site_facts['Parking_Ratio'] = temp_dict2['Parking']
                # elif 'ParkingRatio' in temp_dict2:
                #     site_facts['Parking_Ratio'] = temp_dict2['ParkingRatio']
                # else:
                #     site_facts['Parking_Ratio'] = 'N/A'

                # Get Sale Type
                site_facts['Sale_Type'] = temp_dict2.get('SaleType', 'N/A')

                site_facts["Picture_url"] = "N/A"

                site_facts["Upload_Date"] = datetime.now().strftime("%Y-%m-%d")

                site_facts["Currently_Listed"] = False

                site_facts["Sale_Leased"] = "Sale"

                Buildings.append(site_facts)# Add the site_Facts to the Buildings List
                sleep(randint(5, 10))
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


if __name__ == '__main__':
    main()
