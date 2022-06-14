import pandas as pd
from geopy.geocoders import Nominatim

df = pd.read_csv("dunkin/dd_store_loc_info.csv")

df = df.rename(columns = {"Unnamed: 0": 'row_id'})

df[["address_line_1", "address_line_2", "city", "state", "zip", "phone"]] = \
df[["address_line_1", "address_line_2", "city", "state", "zip", "phone"]].astype('string')

def create_location(addy_1, addy_2, city, state, zip):
        if pd.notna(addy_2):
            return addy_1 + " " + addy_2 + ", " + city + ", " + state + ", " + zip
        else:
            return addy_1 + ", " + city + ", " + state + ", " + zip

df['location'] = [create_location(address_1, address_2, city, state, postal) for \
    address_1, address_2, city, state, postal in \
    zip(df.address_line_1, df.address_line_2, df.city, df.state, df.zip)]

df.location = df.location.astype('string')

df.to_csv('dunkin/dunkin_stores.csv', index = False)