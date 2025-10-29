import os
import base64
import re
from io import BytesIO
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template

# Importar la librería clave de xhtml2pdf
from xhtml2pdf import pisa

# ---
# HELPER 1: Obtener imagen como Data URI
# (Esta función es perfecta y es la clave de este enfoque)
# ---
def get_image_data_uri(image_path_relative):
    """ Lee una imagen y la devuelve como Data URI Base64 """
    try:
        # La ruta base de los estáticos es 'static' en la raíz
        abs_path = os.path.join(settings.BASE_DIR, 'static', image_path_relative)
        
        if not os.path.exists(abs_path):
             # Buscar en 'static/img/' como fallback (donde está favicon.ico)
            abs_path = os.path.join(settings.BASE_DIR, 'static', 'img', os.path.basename(image_path_relative))
            if not os.path.exists(abs_path):
                 raise FileNotFoundError(f"No se encontró el archivo en 'static/{image_path_relative}' ni en 'static/img/{os.path.basename(image_path_relative)}'")

        ext = os.path.splitext(image_path_relative)[1].lower()
        mime_map = {
            '.png': 'image/png', 
            '.jpg': 'image/jpeg', 
            '.jpeg': 'image/jpeg', 
            '.ico': 'image/vnd.microsoft.icon'
        }
        mime_type = mime_map.get(ext, 'application/octet-stream')

        with open(abs_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded_string}"
            
    except FileNotFoundError as e:
        print(f"ADVERTENCIA (pdf_utils): No se encontró la imagen: {e}")
        if 'firma.png' in image_path_relative:
            print("******************************************************************")
            print("ADVERTENCIA: 'firma.png' no se encuentra en 'static/img/'.")
            print("El PDF se generará sin firma.")
            print("Sube tu firma a 'static/img/firma.png'")
            print("******************************************************************")
        return None
    except Exception as e:
        print(f"Error (pdf_utils) al procesar la imagen {image_path_relative}: {e}")
        return None

# ---
# HELPER 2: Sanitizar nombre de archivo
# (Se mantiene igual, es correcto)
# ---
def sanitize_filename(name):
    """ Elimina caracteres no válidos para nombres de archivo """
    name = name.strip()
    name = re.sub(r'[^\w\-]+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name

# ---
# FUNCIÓN PRINCIPAL: Renderizar PDF con xhtml2pdf
# (Simplificada: ya NO usa link_callback)
# ---
def render_to_pdf(request, template_src, context_dict={}):
    """
    Carga plantilla HTML auto-contenida (CSS y Data URIs)
    y la convierte a PDF usando xhtml2pdf.
    """
    
    # 1. Añadir logo y firma al contexto (usando Data URI)
    try:
        # favicon.ico está en static/img/
        logo_data_uri = get_image_data_uri(os.path.join('img', 'favicon.ico'))
        # Asumimos que firma.png también estará en static/img/
        firma_data_uri = get_image_data_uri(os.path.join('img', 'firma.png')) 
        
        context_dict['logo_data_uri'] = logo_data_uri
        context_dict['firma_data_uri'] = firma_data_uri
        context_dict['request'] = request
        
    except Exception as e:
        print(f"Error (pdf_utils) al cargar imágenes data URI: {e}")
        context_dict['logo_data_uri'] = None
        context_dict['firma_data_uri'] = None

    # 2. Renderizar el HTML de la plantilla
    html_string = ""
    try:
        template = get_template(template_src)
        html_string = template.render(context_dict)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"Error al cargar/renderizar la plantilla HTML: {e}. ¿Creaste el archivo '{template_src}'?", status=500)

    # 3. Generar el PDF en memoria
    pdf_data = None
    result_file = BytesIO()
    
    try:
        # Convertir HTML a PDF
        # ¡YA NO SE PASA link_callback!
        pisa_status = pisa.CreatePDF(
            html_string,                # El HTML renderizado
            dest=result_file            # El buffer de BytesIO
        )

        if pisa_status.err:
            raise Exception(f"Error de pisa: {pisa_status.err}")
        
        pdf_data = result_file.getvalue()

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"Error al generar el PDF con xhtml2pdf: {e}", status=500)
    finally:
        result_file.close()

    # 4. Crear la respuesta HTTP
    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')

        # 5. Establecer nombre de archivo (Tu lógica original - ¡perfecta!)
        try:
            nino = context_dict.get('nino')
            evaluacion = context_dict.get('game_session') # 'game_session' es la Evaluacion

            if nino and evaluacion:
                nino_name_sanitized = sanitize_filename(nino.nombre_completo)
                eval_id = evaluacion.id
                filename = f"Reporte_{nino_name_sanitized}_Eval_{eval_id}.pdf"
            else:
                filename = "Reporte_DislexIA.pdf"
            
            response['Content-Disposition'] = f'inline; filename="{filename}"'

        except Exception as e:
            print(f"Error (pdf_utils) al generar nombre de archivo: {e}")
            response['Content-Disposition'] = 'inline; filename="Reporte_DislexIA_Error.pdf"'
        
        return response

    return HttpResponse('Error desconocido al generar el PDF.', status=500)