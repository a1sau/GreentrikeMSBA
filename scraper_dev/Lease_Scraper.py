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
flat_list = ['https://www.loopnet.com/Listing/1551-Broadway-Tacoma-WA/6879898/', 'https://www.loopnet.com/Listing/2128-Pacific-Ave-Tacoma-WA/21271211/', 'https://www.loopnet.com/Listing/11110-25th-Ave-E-Tacoma-WA/22201592/', 'https://www.loopnet.com/Listing/201-W-Main-St-Puyallup-WA/22192376/', 'https://www.loopnet.com/Listing/7715-Pacific-Hwy-E-Milton-WA/22173557/', 'https://www.loopnet.com/Listing/10107-S-Tacoma-Way-Tacoma-WA/22165149/', 'https://www.loopnet.com/Listing/3611-S-56th-St-Tacoma-WA/22004578/', 'https://www.loopnet.com/Listing/212-Todd-Rd-NE-Puyallup-WA/21987873/', 'https://www.loopnet.com/Listing/13704-24th-St-E-Sumner-WA/21966193/', 'https://www.loopnet.com/Listing/621-Pacific-Ave-Tacoma-WA/21941980/', 'https://www.loopnet.com/Listing/5442-S-Tacoma-Way-Tacoma-WA/21931786/', 'https://www.loopnet.com/Listing/2802-S-Meridian-Puyallup-WA/21931557/', 'https://www.loopnet.com/Listing/1746-1748-Pacific-Ave-Tacoma-WA/21906992/', 'https://www.loopnet.com/Listing/5448-S-Tacoma-Way-Tacoma-WA/21798407/', 'https://www.loopnet.com/Listing/3560-3562-Bridgeport-Way-University-Place-WA/21796670/', 'https://www.loopnet.com/Listing/8016-Durango-St-SW-Lakewood-WA/21716234/', 'https://www.loopnet.com/Listing/5121-Pacific-Hwy-E-Fife-WA/21599627/', 'https://www.loopnet.com/Listing/6302-112th-St-E-Puyallup-WA/21599371/', 'https://www.loopnet.com/Listing/13701-24th-St-E-Sumner-WA/21456814/', 'https://www.loopnet.com/Listing/8412-Myers-Rd-E-Bonney-Lake-WA/21394245/', 'https://www.loopnet.com/Listing/3906-S-74th-St-Tacoma-WA/21365027/', 'https://www.loopnet.com/Listing/20620-State-Route-410-E-Bonney-Lake-WA/21360914/', 'https://www.loopnet.com/Listing/420-N-Meridian-Puyallup-WA/21303284/', 'https://www.loopnet.com/Listing/7530-28th-St-W-University-Place-WA/21237806/', 'https://www.loopnet.com/Listing/8114-112th-Street-Ct-E-Puyallup-WA/21190153/', 'https://www.loopnet.com/Listing/1901-1913-S-72nd-St-Tacoma-WA/21190034/', 'https://www.loopnet.com/Listing/8511-Canyon-Rd-E-Summit-WA/21168304/', 'https://www.loopnet.com/Listing/7350-Cirque-Dr-W-University-Place-WA/21167289/', 'https://www.loopnet.com/Listing/2309-S-Tacoma-Way-Tacoma-WA/21167073/', 'https://www.loopnet.com/Listing/614-Harrison-St-Sumner-WA/21039750/', 'https://www.loopnet.com/Listing/2200-109th-St-S-Tacoma-WA/21028987/', 'https://www.loopnet.com/Listing/3608-S-74th-St-Tacoma-WA/21017622/', 'https://www.loopnet.com/Listing/7642-Pacific-Ave-Tacoma-WA/20861738/', 'https://www.loopnet.com/Listing/405-Valley-Ave-Puyallup-WA/20833460/', 'https://www.loopnet.com/Listing/13507-Meridian-Ave-E-Puyallup-WA/20710439/', 'https://www.loopnet.com/Listing/3118-6th-Ave-Tacoma-WA/20521111/', 'https://www.loopnet.com/Listing/2205-70th-Ave-E-Fife-WA/20471842/', 'https://www.loopnet.com/Listing/14801-Spring-St-SW-Lakewood-WA/20396561/', 'https://www.loopnet.com/Listing/2402-2412-S-C-St-Tacoma-WA/20204390/', 'https://www.loopnet.com/Listing/2416-S-C-St-Tacoma-WA/20204354/', 'https://www.loopnet.com/Listing/13613-Meridian-E-Puyallup-WA/20189179/', 'https://www.loopnet.com/Listing/910-Valley-Ave-NW-Puyallup-WA/20175093/', 'https://www.loopnet.com/Listing/10106-36th-St-E-Edgewood-WA/19964904/', 'https://www.loopnet.com/Listing/535-Dock-St-Tacoma-WA/19789988/', 'https://www.loopnet.com/Listing/2415-70th-Ave-W-University-Place-WA/19320875/', 'https://www.loopnet.com/Listing/10408-Pacific-Ave-Tacoma-WA/19320414/', 'https://www.loopnet.com/Listing/22320-92nd-Ave-E-Graham-WA/19315835/', 'https://www.loopnet.com/Listing/2115-S-56th-St-Tacoma-WA/18906455/', 'https://www.loopnet.com/Listing/5015-Tacoma-Mall-Blvd-Tacoma-WA/18895926/', 'https://www.loopnet.com/Listing/2001-48th-Ave-Ct-E-Fife-WA/18746662/', 'https://www.loopnet.com/Listing/1011-E-Main-Ave-Puyallup-WA/18740599/', 'https://www.loopnet.com/Listing/21621-Mountain-Hwy-Spanaway-WA/18628610/', 'https://www.loopnet.com/Listing/1824-112th-St-E-Tacoma-WA/18511822/', 'https://www.loopnet.com/Listing/2316-S-State-St-Tacoma-WA/18288601/', 'https://www.loopnet.com/Listing/8811-S-Tacoma-Way-Tacoma-WA/18263544/', 'https://www.loopnet.com/Listing/17615-85th-Avenue-Ct-E-Puyallup-WA/18139265/', 'https://www.loopnet.com/Listing/9810-40th-Ave-SW-Lakewood-WA/18011571/', 'https://www.loopnet.com/Listing/101-S-10th-St-Tacoma-WA/17926654/', 'https://www.loopnet.com/Listing/310-N-Meridian-Puyallup-WA/17772790/', 'https://www.loopnet.com/Listing/2748-Milton-Way-Milton-WA/17642689/', 'https://www.loopnet.com/Listing/3110-Ruston-Way-Tacoma-WA/17629167/', 'https://www.loopnet.com/Listing/9704-40th-Ave-SW-Lakewood-WA/17387934/', 'https://www.loopnet.com/Listing/10023-128th-St-E-Puyallup-WA/17212584/', 'https://www.loopnet.com/Listing/507-31st-Ave-Puyallup-WA/17172198/', 'https://www.loopnet.com/Listing/938-Broadway-Tacoma-WA/17154653/', 'https://www.loopnet.com/Listing/1407-Valentine-Ave-SE-Sumner-WA/17072690/', 'https://www.loopnet.com/Listing/121-123-132nd-St-S-Parkland-WA/16976280/', 'https://www.loopnet.com/Listing/7304-Lakewood-Dr-W-Lakewood-WA/16939750/', 'https://www.loopnet.com/Listing/109-111-W-Meeker-Ave-Puyallup-WA/16685073/', 'https://www.loopnet.com/Listing/16515-Meridian-E-Puyallup-WA/16373925/', 'https://www.loopnet.com/Listing/2101-S-Tacoma-Way-Tacoma-WA/15670323/', 'https://www.loopnet.com/Listing/4802-S-Center-St-Tacoma-WA/15568479/', 'https://www.loopnet.com/Listing/1111-1117-Tacoma-Ave-S-Tacoma-WA/15347071/', 'https://www.loopnet.com/Listing/909-A-St-Tacoma-WA/15029641/', 'https://www.loopnet.com/Listing/5219-N-Shirley-St-Ruston-WA/14902738/', 'https://www.loopnet.com/Listing/5122-Olympic-Dr-NW-Gig-Harbor-WA/14769505/', 'https://www.loopnet.com/Listing/10222-S-Tacoma-Way-Lakewood-WA/14711522/', 'https://www.loopnet.com/Listing/1602-1680-S-Mildred-St-Tacoma-WA/14572077/', 'https://www.loopnet.com/Listing/1117-Broadway-Plz-Tacoma-WA/13878580/', 'https://www.loopnet.com/Listing/14125-Pacific-Ave-S-Tacoma-WA/13363235/', 'https://www.loopnet.com/Listing/2100-2102-E-Main-St-Puyallup-WA/13350686/', 'https://www.loopnet.com/Listing/3650-S-Cedar-St-Tacoma-WA/12936163/', 'https://www.loopnet.com/Listing/7315-27th-St-W-University-Place-WA/12593147/', 'https://www.loopnet.com/Listing/10240-Bridgeport-Way-SW-Lakewood-WA/12489333/', 'https://www.loopnet.com/Listing/21109-21301-SR-410-E-Bonney-Lake-WA/11999230/', 'https://www.loopnet.com/Listing/3800-3842-Bridgeport-Way-W-University-Place-WA/11971613/', 'https://www.loopnet.com/Listing/6113-176th-Ave-E-Puyallup-WA/11776737/', 'https://www.loopnet.com/Listing/1620-45th-St-E-Sumner-WA/11373063/', 'https://www.loopnet.com/Listing/502-S-M-St-Tacoma-WA/9021108/', 'https://www.loopnet.com/Listing/1142-Broadway-Tacoma-WA/8423207/', 'https://www.loopnet.com/Listing/1430-Wilmington-Dr-Dupont-WA/7958994/', 'https://www.loopnet.com/Listing/8218-Pacific-Ave-Tacoma-WA/7759795/', 'https://www.loopnet.com/Listing/1120-Pacific-Ave-Tacoma-WA/4926653/', 'https://www.loopnet.com/Listing/18209-State-Highway-410-E-Bonney-Lake-WA/4510665/', 'https://www.loopnet.com/Listing/1001-Yakima-Ave-Tacoma-WA/4251603/', 'https://www.loopnet.com/Listing/5038-Tacoma-Mall-Blvd-Tacoma-WA/4203313/', 'https://www.loopnet.com/Listing/2115-S-56th-St-Tacoma-WA/4146104/', 'https://www.loopnet.com/Listing/2202-S-Cedar-St-Tacoma-WA/4101115/', 'https://www.loopnet.com/Listing/1145-Broadway-Tacoma-WA/4099813/', 'https://www.loopnet.com/Listing/2121-S-State-St-Tacoma-WA/4051415/', 'https://www.loopnet.com/Listing/4700-Point-Fosdick-Dr-Gig-Harbor-WA/4038399/', 'https://www.loopnet.com/Listing/401-E-25th-St-Tacoma-WA/3950743/', 'https://www.loopnet.com/Listing/15-S-Oregon-Ave-Tacoma-WA/3949712/', 'https://www.loopnet.com/Listing/5016-Bridgeport-Way-W-University-Place-WA/22134496/', 'https://www.loopnet.com/Listing/19000-38th-Ave-Spanaway-WA/22019921/', 'https://www.loopnet.com/Listing/11102-Sunrise-Blvd-E-Puyallup-WA/21967838/', 'https://www.loopnet.com/Listing/19000-38th-Ave-Spanaway-WA/21909466/', 'https://www.loopnet.com/Listing/4201-S-Steele-St-Tacoma-WA/21623608/', 'https://www.loopnet.com/Listing/2310-Mildred-St-W-Tacoma-WA/21540289/', 'https://www.loopnet.com/Listing/10002-Steele-St-Tacoma-WA/21490354/', 'https://www.loopnet.com/Listing/1110-E-Alexander-Ave-Tacoma-WA/21351569/', 'https://www.loopnet.com/Listing/28002-State-Route-410-Buckley-WA/21179466/', 'https://www.loopnet.com/Listing/4041-Ruston-Way-Tacoma-WA/20695829/', 'https://www.loopnet.com/Listing/917-Valley-Ave-NW-Puyallup-WA/19775695/', 'https://www.loopnet.com/Listing/2205-2207-70th-Ave-W-Tacoma-WA/19320593/', 'https://www.loopnet.com/Listing/6010-Main-St-SW-Lakewood-WA/18815349/', 'https://www.loopnet.com/Listing/4202-192nd-St-Spanaway-WA/18403459/', 'https://www.loopnet.com/Listing/4417-192nd-St-E-Tacoma-WA/18403357/', 'https://www.loopnet.com/Listing/2901-Taylor-Way-Tacoma-WA/17924483/', 'https://www.loopnet.com/Listing/2042-Marc-St-Tacoma-WA/17920368/', 'https://www.loopnet.com/Listing/Taylor-Way-E-11th-Street-Tacoma-WA/17710047/', 'https://www.loopnet.com/Listing/11511-Canterwood-Blvd-NW-Gig-Harbor-WA/17534058/', 'https://www.loopnet.com/Listing/4803-5113-Pacific-Hwy-E-Fife-WA/17531601/', 'https://www.loopnet.com/Listing/19400-Meridian-Ave-E-Graham-WA/17234336/', 'https://www.loopnet.com/Listing/3451-84th-St-S-Lakewood-WA/16387442/', 'https://www.loopnet.com/Listing/828-Valentine-Ave-SE-Pacific-WA/16383722/', 'https://www.loopnet.com/Listing/1412-1430-E-Main-Ave-Puyallup-WA/16046491/', 'https://www.loopnet.com/Listing/3123-142nd-Ave-E-Sumner-WA/14506261/', 'https://www.loopnet.com/Listing/12012-47th-Ave-SW-Lakewood-WA/14058023/', 'https://www.loopnet.com/Listing/12012-47th-Ave-SW-Lakewood-WA/14058022/', 'https://www.loopnet.com/Listing/11515-Burnham-Dr-Gig-Harbor-WA/13760017/', 'https://www.loopnet.com/Listing/1710-136th-Ave-E-Sumner-WA/13503737/', 'https://www.loopnet.com/Listing/4701-Point-Fosdick-Dr-NW-Gig-Harbor-WA/12559998/', 'https://www.loopnet.com/Listing/2519-96th-St-Tacoma-WA/12209355/', 'https://www.loopnet.com/Listing/1826-112th-St-E-Tacoma-WA/6883225/', 'https://www.loopnet.com/Listing/Shaw-Rd-E-5th-Ave-SE-Puyallup-WA/6491756/', 'https://www.loopnet.com/Listing/1201-Pacific-Ave-Tacoma-WA/4426028/', 'https://www.loopnet.com/Listing/448-E-18th-St-Tacoma-WA/22076986/', 'https://www.loopnet.com/Listing/11601-Canyon-Rd-E-Puyallup-WA/21582750/', 'https://www.loopnet.com/Listing/3402-S-18th-St-Tacoma-WA/21248022/', 'https://www.loopnet.com/Listing/15803-Pacific-Ave-S-Spanaway-WA/20611542/', 'https://www.loopnet.com/Listing/14702-Woodbrook-Dr-SW-Lakewood-WA/20066097/', 'https://www.loopnet.com/Listing/1525-E-D-St-Tacoma-WA/19513720/', 'https://www.loopnet.com/Listing/1317-1405-E-Main-Ave-Puyallup-WA/18966088/', 'https://www.loopnet.com/Listing/9805-224th-St-Graham-WA/16172386/', 'https://www.loopnet.com/Listing/3304-Rosedale-St-NW-Gig-Harbor-WA/15509779/', 'https://www.loopnet.com/Listing/3003-W-Valley-Hwy-E-Sumner-WA/15451887/', 'https://www.loopnet.com/Listing/3312-Rosedale-St-NW-Gig-Harbor-WA/14984949/', 'https://www.loopnet.com/Listing/11016-Bridgeport-Way-SW-Lakewood-WA/13827279/', 'https://www.loopnet.com/Listing/9599-S-Tacoma-Way-Lakewood-WA/13406839/', 'https://www.loopnet.com/Listing/20717-Mountain-Hwy-E-Spanaway-WA/12713711/', 'https://www.loopnet.com/Listing/10330-10420-59th-Ave-SW-Lakewood-WA/12467066/', 'https://www.loopnet.com/Listing/15719-Pacific-Ave-S-Tacoma-WA/12207653/', 'https://www.loopnet.com/Listing/Harbor-Hill-Dr-NW-Gig-Harbor-WA/11054558/', 'https://www.loopnet.com/Listing/Harbor-Hill-Dr-Gig-Harbor-WA/11054311/', 'https://www.loopnet.com/Listing/Harbor-Hill-Dr-Gig-Harbor-WA/11054308/']

def building_dict():
    buildings = []
    for link in flat_list:
        site_facts = {}
        url = "{}".format(link)  # Puts the list link in the loop
        r = requests.get(url, headers=headers)
        page_soup = bs(r.content, features="html.parser")
        site_facts['CS_ID'] = 'LN-' + url[-9:-1]
        site_facts['url'] = url  # Adds the url to the dictonary
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
                site_facts['GeoCode'] = GEOID
                print(count, site_facts['Address_Line'], site_facts['City'], GEOID)
            except Exception as err:
                pass
        else:
            site_facts['Address_Line'] = loc
            site_facts["City"] = "N/A"
            site_facts['State'] = "N/A"
            site_facts['Postal_Code'] = "N/A"
            # The titles in order are "Space", "Size", "Term", "Rate", "Space_Use", "Condition", "Avaliable"
        space = page_soup.find("span", class_="available-spaces__data-item__value-segment-wrap")
        Prop_space = page_soup.find_all("span", class_="available-spaces__data-item__value")

        buildings.append(site_facts)
        sleep(randint(2,5))
        print(buildings)


#grab_placards()
building_dict()