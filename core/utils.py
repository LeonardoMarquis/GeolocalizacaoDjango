import requests
from random import randint
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
import geoip2.database

from .text_normalizer import normalizar_categoria, normalizar_cidade, extrair_palavras_chave

# Endpoint para geocodificação (converter cidade em coordenadas)
GEOCODE_URL = 'https://api.geoapify.com/v1/geocode/search'

# Endpoint para buscar lugares
PLACES_URL = 'https://api.geoapify.com/v2/places'

def search_places(keyword, city):

    # busca estabelecimento

    if not keyword or not city:
        return {'places': []}
    
    cidade_normalizada = normalizar_cidade(city)

    # Primeiro: obter coordenadas da cidade
    coords = get_city_coordinates(cidade_normalizada)
    
    if not coords:
        print(f"Não foi possível obter coordenadas para: {cidade_normalizada}")
        return {'places': []}
    
    print(f"Coordenadas de {cidade_normalizada}: {coords}")
    

    categoria_normalizada = normalizar_categoria(keyword)
    palavras_chave = extrair_palavras_chave(keyword)

    categorias_api = get_categorias_api(categoria_normalizada, palavras_chave)

    # Segundo: buscar lugares próximos às coordenadas
    params = {
        'categories': categorias_api,  # Categoria de restaurantes
        'filter': f'circle:{coords["lon"]},{coords["lat"]},10000',  # Raio de 10km
        'limit': 40,
        'apiKey': settings.GEOAPIFY_API_KEY
    }
    
    if categoria_normalizada in ['restaurante', 'comida', '']:
        texto_busca = ' '.join(palavras_chave) if palavras_chave else keyword
        params['text'] = texto_busca


    try:
        response = requests.get(PLACES_URL, params=params)
        response.raise_for_status()
        data = response.json()
        
        places = []
        for feature in data.get('features', []):
            props = feature.get('properties', {})
            geometry = feature.get('geometry', {}).get('coordinates', [])
            
            lon, lat = geometry if len(geometry) == 2 else [None, None]
            
            if props.get('name') and lat and lon:
                # NOVO: Filtra resultados que correspondem à busca
                if nome_corresponde_busca(props.get('name', ''), keyword, palavras_chave):
                    place = {
                        'name': props.get('name'),
                        'lat': lat,
                        'lon': lon,
                        'address': props.get('formatted', 'Endereço não disponível'),
                        'street': props.get('street', ''),
                        'housenumber': props.get('housenumber', ''),
                        'city': props.get('city', cidade_normalizada),
                        'country': props.get('country', 'Brasil'),
                        'categories': props.get('categories', [])
                    }
                    places.append(place)
        
        print(f"Encontrados {len(places)} lugares")
        return {'places': places}
        
    except Exception as e:
        print(f"Erro na busca: {e}")
        return {'places': []}



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


def get_categorias_api(categoria_normalizada, palavras_chave):
    mapa_api = {
        'pizza': 'catering.restaurant.pizza',
        'pizzaria': 'catering.restaurant.pizza',
        'pizzas': 'catering.restaurant.pizza',
        'arrumadinho': 'catering.restaurant',
        'espetinho': 'catering.restaurant',
        'sushi': 'catering.restaurant.sushi, catering.restaurant.japanese',
        'churrasco': 'catering.restaurant.barbecue, catering.restaurant.steakhouse',
        'churrascaria': 'catering.restaurant.barbecue, catering.restaurant.steakhouse',
        'picanha': 'catering.restaurant.barbecue, catering.restaurant.steakhouse',
        'picanharia': 'catering.restaurant.barbecue, catering.restaurant.steakhouse',
        'picanha na brasa': 'catering.restaurant.barbecue, catering.restaurant.steakhouse',
        'shushis': 'catering.restaurant.sushi, catering.restaurant.japanese',
        'restaurante': 'catering.restaurant',
        'lanche': 'catering.fast_food',
        'fastfood': 'catering.fast_food',
        'bar': 'catering.bar',
        'japonesa': 'catering.restaurant.japanese',
        'italiana': 'catering.restaurant.italian',
        'mexicana': 'catering.restaurant.mexican',
        'chinesa': 'catering.restaurant.chinese',
        'hamburguer': 'catering.fast_food'
    }
    
    for chave, categoria in mapa_api.items():
        if chave in categoria_normalizada or any(chave in p for p in palavras_chave):
            return categoria
    
    return 'catering.restaurant'

def nome_corresponde_busca(nome, busca_original, palavras_chave):
    if not nome or not palavras_chave:
        return True
    
    from .text_normalizer import normalizar_texto
    
    nome_normalizado = normalizar_texto(nome)
    busca_min = busca_original.lower()

    termos_categoria = ['churrasco', 'churrascaria', 'sushi', 'japonesa', 'pizzaria', 'pizza', 'bar', 'restaurante']

    if any(termo in busca_min for termo in termos_categoria):
        return True
            # confiou na pesquisa da geoapify
    
    for palavra in palavras_chave:
        if normalizar_texto(palavra) in nome_normalizado:
            return True
    
    return False