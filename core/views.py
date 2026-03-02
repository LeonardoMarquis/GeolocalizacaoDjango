from django.shortcuts import render
from django.views.generic import View
import json

from .utils import search_places, get_client_data

class IndexView(View):
    def get(self, request):
        # Tenta obter a cidade do usuário
        client_data = get_client_data()
        user_city = client_data.get('city') if client_data else None
        
        # Cidade padrão se não conseguir detectar
        if not user_city:
            user_city = "Salvador"
        
        # Pega parâmetros da busca
        keyword = request.GET.get('key', '')
        search_city = request.GET.get('loc', '')
        
        # Se não especificou cidade, usa a do usuário
        if not search_city:
            search_city = user_city
        
        context = {
            'user_city': user_city,
            'search_city': search_city,
            'keyword': keyword,
            'places': [],
            'has_results': False
        }
        
        # Se tiver keyword, faz a busca
        if keyword:
            results = search_places(keyword, search_city)
            places = results.get('places', [])
            
            # Converte para JSON para o mapa
            places_json = json.dumps(places)
            
            context.update({
                'places': places,
                'places_json': places_json,
                'has_results': len(places) > 0
            })
        
        return render(request, 'index.html', context)