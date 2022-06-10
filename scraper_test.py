import requests
import pandas as pd
from bs4 import BeautifulSoup

store_page = requests.get(url = 'https://locations.dunkindonuts.com/en/al/helena/2536-helena-rd/362905')
store_soup = BeautifulSoup(store_page.content, 'html.parser')

# scraping store's address
def get_address_data(soup_obj):

    # initialize storage for address data in function
    address_result = []

    # css tags containing store address information
    address_field_tags = ['.c-address-street-1', 
                        '.c-address-street-2', 
                        '.c-address-city', 
                        '.c-address-state', 
                        '.c-address-postal-code',
                        '#phone-main']

    # collecting fields, substituting N/A if field is not present on page
    for field in address_field_tags:
        if[item.get_text() for item in soup_obj.select(field)] != []:
            valid_item = soup_obj.select(field)[0].get_text()
            address_result.append(valid_item)
        else:
            address_result.append("N/A")

    return address_result

address_data = get_address_data(store_soup)
print(address_data)

phone_data = [item.get_text() for item in\
    store_soup.select("#phone-main")]

if phone_data == None:
    phone_data = 'N/A'

print(phone_data)