import requests
from random import randint
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
import geoip2.database

# Endpoint para geocodificação (converter cidade em coordenadas)
GEOCODE_URL = 'https://api.geoapify.com/v1/geocode/search'

# Endpoint para buscar lugares
PLACES_URL = 'https://api.geoapify.com/v2/places'

def search_places(keyword, city):
    """
    Busca estabelecimentos em uma cidade usando a API do Geoapify
    """
    if not keyword or not city:
        return {'places': []}
    
    # Primeiro: obter coordenadas da cidade
    coords = get_city_coordinates(city)
    
    if not coords:
        print(f"Não foi possível obter coordenadas para: {city}")
        return {'places': []}
    
    print(f"Coordenadas de {city}: {coords}")
    
    # Segundo: buscar lugares próximos às coordenadas
    params = {
        'categories': 'catering.restaurant',  # Categoria de restaurantes
        'filter': f'circle:{coords["lon"]},{coords["lat"]},5000',  # Raio de 5km
        'limit': 20,
        'apiKey': settings.GEOAPIFY_API_KEY
    }
    
    # Se a keyword for específica, adiciona como texto
    if keyword.lower() not in ['restaurante', 'restaurant']:
        params['text'] = keyword
    
    print(f"Parâmetros da busca: {params}")
    
    try:
        response = requests.get(PLACES_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Processa os resultados
        places = []
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            geometry = feature.get('geometry', {}).get('coordinates', [])
            
            # Geoapify retorna [longitude, latitude]
            lon, lat = geometry if len(geometry) == 2 else [None, None]
            
            # Só adiciona se tiver nome e coordenadas
            if props.get('name') and lat and lon:
                place = {
                    'name': props.get('name'),
                    'lat': lat,
                    'lon': lon,
                    'address': props.get('formatted', 'Endereço não disponível'),
                    'street': props.get('street', ''),
                    'housenumber': props.get('housenumber', ''),
                    'city': props.get('city', city),
                    'country': props.get('country', 'Brasil')
                }
                places.append(place)
        
        print(f"Encontrados {len(places)} lugares")
        return {'places': places}
        
    except Exception as e:
        print(f"Erro na busca: {e}")
        return {'places': []}

def get_city_coordinates(city):
    """
    Converte nome da cidade em coordenadas
    """
    # Adiciona Brasil se não estiver especificado
    if 'brasil' not in city.lower() and 'brazil' not in city.lower():
        city = f"{city}, Brasil"
    
    params = {
        'text': city,
        'format': 'json',
        'limit': 1,
        'apiKey': settings.GEOAPIFY_API_KEY
    }
    
    try:
        response = requests.get(GEOCODE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('results'):
            result = data['results'][0]
            return {
                'lat': result.get('lat'),
                'lon': result.get('lon')
            }
    except Exception as e:
        print(f"Erro na geocodificação: {e}")
    
    return None

def get_client_data():
    """
    Obtém dados do cliente baseado no IP
    """
    g = GeoIP2()
    ip = get_random_ip()

    try:
        return g.city(ip)
    except geoip2.errors.AddressNotFoundError:
        return None

def get_random_ip():
    return '.'.join([str(randint(0, 255)) for x in range(4)])