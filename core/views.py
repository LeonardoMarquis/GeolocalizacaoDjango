from django.shortcuts import render
from django.views.generic import View

from .utils import geopify_search, get_client_data

class IndexView(View):
    def get(self, request, *args, **kwargs):
        items = []

        city = None

        while not city:
            ret = get_client_data()
            if ret:
                city = ret['city']  # a cidade do usuario que esta acessando

        q = request.GET.get('key', None)
        loc = request.GET.get('loc', None)      # a cidade que o usuario esta pesquinsando as coisas, 
        location = city


        context = {
            'city': city,
            'busca': False
        }

        if loc:
            location = loc
        if q:
            items = geopify_search(q, loc)
            context = {
                'items': items,
                'city': location,
                'busca': True
            }

        return render(request, 'index.html', context)





