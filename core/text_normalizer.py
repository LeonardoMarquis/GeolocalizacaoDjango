import unicodedata
import re


def remove_acentos(texto):
    if not texto:
        return texto
    
    texto_normalizado = unicodedata.normalize('NFKD', texto)
    texto_sem_acentos = ''.join([c for c in texto_normalizado if not unicodedata.combining(c)])
    return texto_sem_acentos

def normalizar_texto(texto):
    if not texto:
        return ''
    
    texto = remove_acentos(texto)
    texto = texto.lower()
    texto = texto.strip()
    
    return texto

def normalizar_categoria(texto):
    if not texto:
        return ''
    
    texto = normalizar_texto(texto)

    mapa_categorias = {
        'pizza': 'pizza',
        'pizzaria': 'pizza',
    'pizzas': 'pizza',
        'restaurante': 'restaurante',
        'restaurant': 'restaurante',
        'bar': 'bar',
        'lanche': 'lanche',
        'lanchonete': 'lanche',
        'fastfood': 'fastfood',
        'fast food': 'fastfood',
        'comida': 'comida',
        'japa': 'japonesa',
        'japonesa': 'japonesa',
        'japanese': 'japonesa',
        'italiana': 'italiana',
        'italian': 'italiana',
        'mexicana': 'mexicana',
        'mexican': 'mexicana',
        'brasileira': 'brasileira',
        'brazilian': 'brasileira',
        'chinesa': 'chinesa',
        'chinese': 'chinesa',
        'arabe': 'arabe',
        'arab': 'arabe',
        'hamburguer': 'hamburguer',
        'hamburger': 'hamburguer',
        'burger': 'hamburguer'
    }

    for palavra_chave, categoria in mapa_categorias.items():
        if palavra_chave in texto:
            return categoria
    
    return texto

def normalizar_cidade(texto):
    if not texto:
        return ''
    
    texto = normalizar_texto(texto)
    
    mapa_cidades = {
        'sao paulo': 'São Paulo',
        'sp': 'São Paulo',
        'sao paulo sp': 'São Paulo',
        'rio': 'Rio de Janeiro',
        'rio de janeiro': 'Rio de Janeiro',
        'rj': 'Rio de Janeiro',
        'salvador': 'Salvador',
        'ssa': 'Salvador',
        'brasilia': 'Brasília',
        'bsb': 'Brasília',
        'belo horizonte': 'Belo Horizonte',
        'bh': 'Belo Horizonte'
    }

    for chave, cidade in mapa_cidades.items():
        if chave in texto:
            return cidade
        
    return texto.title()

def extrair_palavras_chave(texto):
    if not texto:
        return []
    
    stop_words = ['de', 'da', 'do', 'em', 'para', 'com', 'uma', 'um', 'na', 'no']
    palavras = texto.split()
    
    palavras_filtradas = []
    for palavra in palavras:
        if palavra not in stop_words and len(palavra) > 2:
            palavras_filtradas.append(palavra)
    
    return palavras_filtradas