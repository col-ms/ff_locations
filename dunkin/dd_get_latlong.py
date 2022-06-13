import pandas as pd
from geopy.extra.rate_limiter import RateLimiter

locator = Nominatim

geocode = RateLimiter(locator.geocode, min_delay_seconds = 1)

