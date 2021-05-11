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
    print(f"Found {t_listings} placards across {pages -1} pages.\nStarting to Collect URL's of for lease properties.")
        ### This is what go to the search and pulls every listing url from the search page(s)
    for i in range(1,pages):      # loops equal to the number of pages in the search
        url = "https://www.loopnet.com/search/commercial-real-estate/pierce-county-wa/for-lease/{}/".format(i)  # Looks to this URL, increasing in page numbers.
        r = requests.get(url, headers=headers)  # Gets the information from the page
        soup = bs(r.content, features="html.parser")  # Turns to bs object.
        sleep(randint(2,5))    # Sleeps so we dont get banned.
        links = soup.find_all('a', class_="subtitle-beta")  # Grabs the placard links that are NOT the featured placard TODO get the featured placard link
        loop_list=[link['href'] for link in links] # isolates the url from the html
        loopnet_links.append(loop_list) #just puts in the url into the list
    url_list = [item for sublist in loopnet_links for item in sublist]
    return url_list

def building_dict(url_list):
    buildings = []
    progress = 0
    for link in url_list:
        url = "{}".format(link)  # Puts the list link in the loop
        r = requests.get(url, headers=headers)
        page_soup = bs(r.content, features="html.parser")
        # The titles in order are "Space", "Size", "Term", "Rate", "Space_Use", "Condition", "Available"
        units = page_soup.find_all("ul", class_="available-spaces__accordion-data no-margin js-as-column-width")
        progress += 1
        counter = 1 # Used to ensure unique CS_ID
        print(progress, url)
        for item in units:
            site_facts = {}
            unit_temp = item.get_text("|", strip=True)
            units_txt = unit_temp.split("|")
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
                if units_txt[-4].endswith("/"):
                    site_facts['Property_Type'] = units_txt[-4] + units_txt[-3]
                else:
                    site_facts['Property_Type'] = units_txt[-3]
                geocode = cg.address(street=site_facts['Address_Line'], city=site_facts['City'], state=site_facts['State'], zipcode=site_facts['Postal_Code'])
                try:
                    GEOID = geocode[0]['geographies']['2020 Census Blocks'][0]['GEOID'][0:12]
                    site_facts['bg_geo_id'] = GEOID
                    print(site_facts['Address_Line'], site_facts['City'], GEOID)
                except Exception as err:
                    site_facts['bg_geo_id'] = None
                    pass
            else:
                site_facts['Address_Line'] = loc
                site_facts["City"] = "N/A"
                site_facts['State'] = "N/A"
                site_facts['Postal_Code'] = "N/A"
                site_facts['bg_geo_id'] = None
                if units_txt[-4].endswith("/"):
                    site_facts['Property_Type'] = units_txt[-4] + units_txt[-3]
                else:
                    site_facts['Property_Type'] = units_txt[-3]
                site_facts['bg_geo_id'] = "N/A"
            # Gets the CS_ID and URL #
            id_array = url.split('/')  # Split url to get trailing digits for Primary Key
            site_facts['CS_ID'] = "LN-" + id_array[-2] + "-" + str(counter)
            site_facts['url'] = url  # Adds the url to the dictonary
            # Price
            #site_facts['Price_month']
            try:
                monthp_index = units_txt.index("/MO") - 1  # Finds the element that matches "/MO" then goes one back to the numeric price
                month_price = units_txt[monthp_index].replace(',', '')
                if '.' in month_price:
                    m_p = month_price.split('.')
                    site_facts['Price_month'] = int(m_p[0].strip('$'))
                else:
                    site_facts['Price_month'] = int(month_price.strip('$'))
            except ValueError as err:
                site_facts['Price_month'] = None
            # Price Per Year
            try:
                yearp_index = units_txt.index("/YR") - 1 #Finds the element that matches "/YR" then goes one back to the numeric price
                year_price = units_txt[yearp_index].replace(',','')
                site_facts['Price_year'] = int(year_price.strip('$'))
            except ValueError as err:
                site_facts['Price_year'] = None
            # Square Feet (size)
            if units_txt[1].endswith("-"):
                ft_int = units_txt[1].replace(',','')
                site_facts['SquareFeet'] = int(ft_int.strip("-"))
                max_ft = units_txt[2].replace(',','')
                site_facts['Expansion_SqrFt'] = int(max_ft.strip(' SF'))
            else:
                ft_int = units_txt[1].replace(',','')
                site_facts['SquareFeet'] = int(ft_int.strip(' SF'))
                site_facts['Expansion_SqrFt'] = None
            # Space
            site_facts['Space'] = units_txt[0]
            # Condition
            if units_txt[-2] == '-':
                site_facts['Condition'] = 'Not Listed'
            else:
                site_facts['Condition'] = units_txt[-2]
            # Avalable
            site_facts['Available'] = units_txt[-1]
            # Term
            # Look to Expansion sqrft
            if site_facts['Expansion_SqrFt'] == None:
                site_facts['Term'] = units_txt[2]
            else:
                site_facts['Term'] = units_txt[3]
            # Upload_Date
            site_facts['Upload_Date'] = datetime.now().strftime("%Y-%m-%d")
            # Currently_Listed
            site_facts["Currently_Listed"] = True
            # Sale_Lease
            site_facts['Sale_Lease'] = "Lease"
            #Append to buildings
            buildings.append(site_facts)
            #Increase Counter
            counter += 1
        sleep(randint(5,10))
    return buildings

def update_lease_listings():
    # Given a list of urls:
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0'}
    off_market = []
    for i in listings: # go to each link
        r_page = requests.get(i[1], headers=headers)  # Gets the information from the page
        s = bs(r_page.content, features="html.parser")  # Turns to bs object.
        if s.find('div', class_="off-market-banner"): # find if listing is still active
            off_market.append(i[0])
        sleep(randint(3,8))
        # find if listing is still active
        # find if information has been changed (price)
        # return CS_ID, if information has been changed, what new values are, and if listing is active
    return None
#Function to take in list of urls that are on the database, compare with things just listed and gives new records so we dont grab new information.
def listing_checker(database_list,grab_placards_list):
    new_listings = []
    for i in grab_placards_list:
        if i not in database_list:
            new_listings.append(i)
    return new_listings

def lease_buildings_csv_export(property_info):
    export_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%p")
    with open('loopnet_listings_lease_{}.csv'.format(export_time), 'w', newline='\n') as f:
        w = csv.DictWriter(f, property_info[0].keys())
        w.writeheader()
        for i in property_info:
            w.writerow(i)
    f.close()

def lease_export(property_info):
    listings = []
    for i in property_info:
        # TODO Match this format to the columns in the database for easy etl.

        row = (i['Address_Line'],i['City'],i['State'],i['Postal_Code'],i['Property_Type'],i['bg_geo_id'],
               i['CS_ID'],i['url'],None, i['SquareFeet'], None, None,
               None, None, i['Upload_Date'], i['Currently_Listed'], i['Sale_Lease'], None, i['Price_month'],
               i['Price_year'],i['Expansion_SqrFt'],i['Space'],i['Condition'],i['Available'],i['Term'])
        listings.append(row)
    return listings


def main():
    print('Grab placards')
    url_list = grab_placards()
    print('Checking Listings')
    property_info = building_dict(url_list)
    print('Export list to file')
    lease_buildings_csv_export(property_info)
    #lease_export(property_info)
    #update_lease_listings()

if __name__ == '__main__':
    main()
