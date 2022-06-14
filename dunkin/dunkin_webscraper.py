# importing used packages
import pandas as pd
import requests
from bs4 import BeautifulSoup

#-------------------------------------#
# Phase One:                          #  
# retrieving states that have at      #
# least one Dunkin Location in them   #
#-------------------------------------#

# url of DD's page hosting all states that have locations in them
base_url = 'https://locations.dunkindonuts.com/en'

# create dict of state names and abbreviations for url processing later
states = {
    'AK':'Alaska',
    'AL':'Alabama',
    'AR':'Arkansas',
    'AZ':'Arizona',
    'CA':'California',
    'CO':'Colorado',
    'CT':'Connecticut',
    'DC':'District of Columbia',
    'DE':'Delaware',
    'FL':'Florida',
    'GA':'Georgia',
    'HI':'Hawaii',
    'IA':'Iowa',
    'ID':'Idaho',
    'IL':'Illinois',
    'IN':'Indiana',
    'KS':'Kansas',
    'KY':'Kentucky',
    'LA':'Louisiana',
    'MA':'Massachusetts',
    'MD':'Maryland',
    'ME':'Maine',
    'MI':'Michigan',
    'MN':'Minnesota',
    'MO':'Missouri',
    'MS':'Mississippi',
    'MT':'Montana',
    'NC':'North Carolina',
    'ND':'North Dakota',
    'NE':'Nebraska',
    'NH':'New Hampshire',
    'NJ':'New Jersey',
    'NM':'New Mexico',
    'NV':'Nevada',
    'NY':'New York',
    'OH':'Ohio',
    'OK':'Oklahoma',
    'OR':'Oregon',
    'PA':'Pennsylvania',
    'RI':'Rhode Island',
    'SC':'South Carolina',
    'SD':'South Dakota',
    'TN':'Tennessee',
    'TX':'Texas',
    'UT':'Utah',
    'VA':'Virginia',
    'VT':'Vermont',
    'WA':'Washington',
    'WI':'Wisconsin',
    'WV':'West Virginia',
    'WY':'Wyoming'
}

# function to return a dict key based on passed value
# used to convert scraped state names to their respective abbreviations
def get_key(val, queriedDict):
    for key, value in queriedDict.items():
        if val == value:
            return key
        # special case due to DD's page nomenclature regarding the District of Columbia
        if val == 'Washington DC': 
            return 'DC'
    return 'Key does not exist'

# retrieving base locations page 
base_location_page = requests.get(url = base_url)
base_location_soup = BeautifulSoup(base_location_page.content, 'html.parser')

# scraping state names
dd_valid_states = [state.get_text() for state in base_location_soup.select('.Directory-listLink')]

# converting from state names to abbreviations
dd_valid_state_abrvs = [get_key(val, states).lower() for val in dd_valid_states]

#-------------------------------------#
# Phase two:                          #
# iterating through each state to get #
# all town names with DD locations    #
#-------------------------------------#

# function to iterate through all states and retrieve towns within that state
def get_dd_town_names(state_abrv_list):
    
    # initialize storage for results
    town_result = [] 

    for state_abrv in state_abrv_list:
        
        # getting each state's page
        state_page = requests.get(url = base_url + '/' + state_abrv) 
        state_soup = BeautifulSoup(state_page.content, 'html.parser')

        # scraping town names from page
        state_towns = [town.get_text().lower() for town in state_soup.select('.Directory-listItem')]

        # formatting town name
        for town_name in state_towns:
            town_result.append(state_abrv + '/' + town_name.replace(" ", "-"))

    return town_result

dd_valid_towns = get_dd_town_names(dd_valid_state_abrvs)

#-------------------------------------#
# Phase three:                        #
# scraping url to retrieve urls tail  #
# for each valid store location       #
#-------------------------------------#

def get_dd_store_url_tails(town_name_list):

    # progress monitor indicator
    i = 1

    # initializing storage for results
    store_url_result = []

    for town_name in town_name_list:

        # getting each town's store list page
        town_page = requests.get(url = base_url + '/' + town_name)
        town_soup = BeautifulSoup(town_page.content, 'html.parser')

        # scraping individual store url tails
        store_list_main = town_soup.find(id = 'main')
        store_teaser_list = store_list_main.find_all(class_ = 'Teaser Teaser--directory')

        for store_teaser in store_teaser_list:
                address_class = store_teaser.find(class_ = 'Teaser-name')
                store_address = list(address_class.attrs.values())[0]

                # strips beginning of url off (../../en)
                store_url_result.append(store_address[8:])
        
        print('completed', i, 'of', len(town_name_list), end = '\r')
        i += 1

    return store_url_result

dd_valid_stores = get_dd_store_url_tails(dd_valid_towns)

#for store_url in dd_valid_stores:
#    print(store_url)

#-------------------------------------#
# Phase four:                         #
# scraping individual store info      #
# using urls gotten in phase three    #
#-------------------------------------#

def get_dd_store_info(dd_store_url_list):

    # progress monitor indicator
    i = 1

    # initialize storage for results
    ind_store_data = []

    for store_url in dd_store_url_list:

        # get store's individual page
        store_page = requests.get(base_url + store_url)
        store_soup = BeautifulSoup(store_page.content, 'html.parser')

        # scraping store's address and phone number
        def get_address_data(soup_obj):

            # initialize storage for address data in function
            address_result = []

            # css tags containing store address and phone information
            address_field_tags = ['.c-address-street-1', 
                                '.c-address-street-2', 
                                '.c-address-city', 
                                '.c-address-state', 
                                '.c-address-postal-code',
                                '#phone-main']

            # collecting fields, substituting N/A if field is not present on page
            for field in address_field_tags:
                if[item.get_text() for item in soup_obj.select(field)] != []:
                    address_result.append( soup_obj.select(field)[0].get_text())
                else:
                    address_result.append("N/A")

            return address_result

        address_data = get_address_data(store_soup)

        # scraping store's operating hours
        hours_data = [item.get_text() for item in\
            store_soup.select('.c-hours-details-row-intervals')]

        # defining function to detect presence of features and return binary indicators
        def get_feat_data(store_soup_obj):

            # list of possible store features, as listed on DD website
            store_feature_list = [
                'Drive Thru',
                'On-the-Go Mobile Ordering',
                "Accepts Dunkin' Cards",
                'K-Cup Pods',
                'Curbside Pick up',
                'Baskin-Robbins'
            ]

            for item in store_soup_obj.select('.Core-features'):
                return [item.get_text().__contains__(feature) for feature in store_feature_list]

        # calling above function to scrape and classify stores' features
        feature_data = get_feat_data(store_soup)

        # some pages do not have a 'features' section, in which case all are assumed false
        if feature_data == None:
            feature_data = [False] * 6

        # merging individual store data to a single list entry and appending to result list
        ind_store_data.append(address_data + hours_data + feature_data)

        print('collected', i, 'of', len(dd_store_url_list), end = '\r')
        i += 1

    return ind_store_data

# calls get store data function
store_data_list_complete = get_dd_store_info(dd_valid_stores)

# list of dataframe column names
df_field_names = [
    'address_line_1', 
    'address_line_2', 
    'city', 
    'state', 
    'zip',
    'phone',
    'mon_hrs',
    'tue_hrs',
    'wed_hrs',
    'thu_hrs',
    'fri_hrs',
    'sat_hrs',
    'sun_hrs',
    'drive-thru',
    'mobile-order',
    'dunkin-card',
    'kcup',
    'curbside-pickup',
    'has-baskin-robbins'
]

# transforms store data list into a pandas dataframe
store_info_df = pd.DataFrame(store_data_list_complete, columns = df_field_names)

# writes csv from pandas dataframe
store_info_df.to_csv('dunkin_stores.csv')

        