import pandas as pd
import requests
from bs4 import BeautifulSoup

page = requests.get("https://locations.dunkindonuts.com/en")
print(page)