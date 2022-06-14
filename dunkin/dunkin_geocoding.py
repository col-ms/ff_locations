# loading required libraries
import pandas as pd
from geopy.geocoders import Nominatim

# reading in data
df = pd.read_csv("dunkin/dunkin_stores.csv")

# cleaning columns and prepping for string concat below
df = df.rename(columns = {"Unnamed: 0": 'row_id'})
df[["address_line_1", "address_line_2", "city", "state", "zip", "phone"]] = \
df[["address_line_1", "address_line_2", "city", "state", "zip", "phone"]].astype('string')

# function to turn columns into cohesive address column for geocoding
def create_location(addy_1, addy_2, city, state, zip):
        if pd.notna(addy_2):
            return addy_1 + " " + addy_2 + ", " + city + ", " + state + ", " + zip
        else:
            return addy_1 + ", " + city + ", " + state + ", " + zip

# creating location column to hold condensed address
df['location'] = [create_location(address_1, address_2, city, state, postal) for \
    address_1, address_2, city, state, postal in \
    zip(df.address_line_1, df.address_line_2, df.city, df.state, df.zip)]

df.location = df.location.astype('string')

# initializing geolocator object
geolocator = Nominatim(user_agent = 'myApp')

# retrieving lat/long for valid addresses
lat, long = [], []
i = 1

for address in df.location:
    print(i, " of ", len(df.location), end = '\r')
    i += 1
    try:
        location = geolocator.geocode(address)
        
        lat.append(location.latitude)
        long.append(location.longitude)
    except:
        lat.append("N/A")
        long.append("N/A")

# attaching lat/long to dataframe and dropping now redundant location column
df['loc_lat'] = lat
df['loc_long'] = long
df = df.drop(columns = "location")

# saving updated csv
df.to_csv('dunkin/dunkin_stores.csv', index = False)