import requests
from random import randint
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
import geoip2.database

geopify_search_endpoint = 'https://api.geoapify.com/v2/places?categories=tourism.sights&filter=circle:{lon},{lat},5000&limit=10&apiKey={api_key}'

# keyword sera a nossa cidade e o location sera o pais
def geopify_search(keyword = None, location = None):
    headers = {'Authorization': f'Bearer {settings.GEOAPIFY_API_KEY}'}

    if keyword and location:
        params = {
            'term': keyword,
            'location': location
        }
    else:
        params = {
            'term': 'tourism.sights',
            'location': 'world'
        }
    
    r = requests.get(geopify_search_endpoint, headers=headers, params=params)

    return r.json()

def get_client_data():
    g = GeoIP2()
    ip = get_random_ip()

    try:
        return g.city(ip)
    except geoip2.errors.AddressNotFoundError:
        return None

def get_random_ip():
    return '.'.join([str(randint(0, 255)) for x in range(4)])





