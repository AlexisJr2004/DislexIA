from django.shortcuts import render
from .models import Recurso

def lista_recursos(request):
    recursos = Recurso.objects.filter(activo=True)
    
    context = {
        'page_title': 'Recursos sobre Dislexia',
        'recursos': recursos,
    }
    return render(request, 'documents.html', context)