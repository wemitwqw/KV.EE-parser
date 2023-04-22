from bs4 import BeautifulSoup
from selenium import webdriver
import lxml
import re
import csv  

def main():
    baseUrl = input('Input base url of the search here: ')
    # baseUrl = 'https://www.kv.ee/search?orderby=cd&view=default&deal_type=1&county=1&parish=1061&city[0]=1001&city[1]=5701&city[2]=1003&city[3]=1004&city[4]=1006&city[5]=1007&city[6]=1008&city[7]=1010&city[8]=1011&city[9]=5700&price_min=140000&price_max=160000&year_built_min=2022&year_built_max=2023'

    data = scanAllPages(baseUrl)

    header = ['address', 'fullPrice', 'sqmPrice', 'rooms']
    with open('parseResult.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in data:
            writer.writerow([row['address'], row['prices']['full'], row['prices']['sqm'], row['rooms']])

def scanAllPages(baseUrl):
    data = []
    pattern = r'[\d]+'
    dr = webdriver.Chrome()

    totalListings = getNumberOfListings(dr, baseUrl, pattern)
    totalPages = getTotalPages(totalListings)
    choiceOfPages = int(input(f'Total number of listings: {totalListings}, total pages: {totalPages}. Enter the number of pages to scan: '))
    for i in range(0, choiceOfPages):
        scanPage(dr, baseUrl, i, pattern, data)

    dr.close()
    return data

def getTotalPages(numberOfListings):
    numberOfListings = int(numberOfListings)
    totalPages = round(numberOfListings / 50)
    if totalPages < numberOfListings / 50:
        totalPages += 1
    return totalPages

def getNumberOfListings(dr, url, pattern):
    dr.get(url)
    bs = BeautifulSoup(dr.page_source, 'lxml')

    totalListings = bs.select_one('.sorter').select_one('span.large.stronger').text
    numbers = []
    if re.search(pattern, totalListings) is not None:
        for catch in re.finditer(pattern, totalListings):
            numbers.append(catch[0])
    totalListings = ''.join(str(i) for i in numbers)
    return totalListings

def scanPage(dr, url, i, pattern, data):
    print(f'Scanning page: {i+1}')
    url = url + '&start=' + str(i*50)

    dr.get(url)
    bs = BeautifulSoup(dr.page_source, 'lxml')

    listings = bs.select_one('div[class="results results-default"]').select('article[class="default object-type-apartment"]')

    for listing in listings:
        data.append(getOneListingData(listing, pattern))

def getOneListingData(listing, pattern):
    oneListingDict = {}
    oneListingDict['address'] = getOneListingDescription(listing)
    oneListingDict['prices'] = getOneListingPrice(listing, pattern)
    oneListingDict['rooms'] = getOneListingRooms(listing)
    # oneListingDict['media'] = getOneListingMedia(listing)
    
    return oneListingDict

def getOneListingDescription(listing):
    description = listing.select_one('div[class=description]').text
    description = description.split('    ')
    if (description[0] == ''):
        description = description[1].split('   ')[1]
        return description    
    description = description[0].split('  ')
    return description[1].strip()

def getOneListingRooms(listing):
    rooms = listing.select_one('div[class=rooms]').get_text()
    try:
        rooms = int(rooms)
    except ValueError:
        print ('Invalid room count')
    return rooms

def getOneListingPrice(listing, pattern):
    pricesUnformatted = listing.select_one('div[class=price]').get_text()
    pricesUnformatted = pricesUnformatted.split('¬')

    pricesFormatted = []
    for price in pricesUnformatted:
        price = re.sub(r"\s+", "", price, flags=re.UNICODE)
        for catch in re.finditer(pattern, price):
            pricesFormatted.append(catch[0])

    pricesDict = {}
    pricesDict['full'] = pricesFormatted[0]
    pricesDict['sqm'] = pricesFormatted[1]
    return pricesDict

# def getOneListingMedia(listing):
#     linksDivs = listing.select('div[class=swiper-slide]')
#     media = []
#     for link in linksDivs:
#         media.append(link.select_one('img').attrs['data-src'])
#     return media

if __name__ == '__main__':
    main()