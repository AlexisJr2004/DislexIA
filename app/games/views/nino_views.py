from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from app.core.models import Profesional
from app.core.forms.forms_profile import NinoForm

@csrf_exempt
@require_http_methods(["POST"])
def crear_nino_ajax(request):
    """Crear un niño asociado al profesional autenticado vía AJAX.
    Espera campos del NinoForm en POST.
    """
    try:
        # Si el usuario no está autenticado, retornar error
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'Autenticación requerida'}, status=401)

        # Bind form
        form = NinoForm(request.POST, request.FILES)
        if form.is_valid():
            nino = form.save(commit=False)
            # Asignar profesional si es instancia de Profesional
            if isinstance(user, Profesional):
                nino.profesional = user
            nino.save()
            return JsonResponse({
                'success': True, 
                'nino': {
                    'id': nino.id, 
                    'nombres': nino.nombres,
                    'apellidos': nino.apellidos,
                    'nombre_completo': nino.nombre_completo,
                    'edad': nino.edad,
                    'genero': nino.genero
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)