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


def grab_placards():  ## NOTE -- this only searches properties that are listed for lease.
    loopnet_links = []
    page_number = "https://www.loopnet.com/search/commercial-real-estate/pierce-county-wa/for-lease/"
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
        url = "https://www.loopnet.com/search/commercial-real-estate/pierce-county-wa/for-lease/{}/".format(i)  # Looks to this URL, increasing in page numbers.
        r = requests.get(url, headers=headers)  # Gets the information from the page
        soup = bs(r.content, features="html.parser")  # Turns to bs object.
        sleep(randint(2,5))    # Sleeps so we dont get banned.
        links = soup.find_all('a', class_="subtitle-beta")  # Grabs the placard links that are NOT the featured placard TODO get the featured placard link
        loop_list=[link['href'] for link in links] # isolates the url from the html
        loopnet_links.append(loop_list) #just puts in the url into the list
    flat_list = [item for sublist in loopnet_links for item in sublist]
    print(len(flat_list))
    print(flat_list)
    return flat_list
flat_list = ['https://www.loopnet.com/Listing/2128-Pacific-Ave-Tacoma-WA/21271211/','https://www.loopnet.com/Listing/1551-Broadway-Tacoma-WA/6879898/']
def building_dict():
    buildings = []
    for link in flat_list:
        site_facts = {}
        url = "{}".format(link)  # Puts the list link in the loop
        r = requests.get(url, headers=headers)
        page_soup = bs(r.content, features="html.parser")
        #Gets the Address_Line through bg_geo_id #
        loc = page_soup.find("h1", class_="breadcrumbs__crumb breadcrumbs__crumb-title")  # Finds the address on page.
        try:  # If location doesn't have address, go to next item)
            loc = loc.get_text()
        except Exception as err:
            continue
        check = loc[-5:].isdigit()  # Checks to see if the postal code is in the address
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
            geocode = cg.address(street=site_facts['Address_Line'], city=site_facts['City'], state=site_facts['State'],
                                 zipcode=site_facts['Postal_Code'])
            try:
                GEOID = geocode[0]['geographies']['Census Tracts'][0]['GEOID']
                site_facts['bg_geo_id'] = GEOID
                print(count, site_facts['Address_Line'], site_facts['City'], GEOID)
            except Exception as err:
                pass
        else:
            site_facts['Address_Line'] = loc
            site_facts["City"] = "N/A"
            site_facts['State'] = "N/A"
            site_facts['Postal_Code'] = "N/A"
            site_facts['bg_geo_id'] = "N/A"
        # Gets the CS_ID and URL #
        id_array = url.split('/')  # Split url to get trailing digits for Primary Key
        site_facts['CS_ID'] = "LN-" + id_array[-2]
        site_facts['url'] = url  # Adds the url to the dictonary

        # The titles in order are "Space", "Size", "Term", "Rate", "Space_Use", "Condition", "Avalable"
        units = page_soup.find_all("ul", class_="available-spaces__accordion-data no-margin js-as-column-width")
        units_txt = []
        for item in units:
            unit_temp = item.get_text("|",strip=True)
            units_txt.append(unit_temp)

        # Price

        # Square Feet (size)

        # Space

        # Condition

        # Avalable

        # Term

        # Upload_Date

        # Currently_Listed

        # Sale_Lease


        buildings.append(site_facts)

        sleep(randint(2,5))
        print(buildings)


#grab_placards()
building_dict()
