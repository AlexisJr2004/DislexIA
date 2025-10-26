import asyncio
import os
import base64
import urllib.parse
import re # Importar re para sanitizar nombres
from django.http import HttpResponse
from django.conf import settings
from django.template import Template, Context
from playwright.async_api import async_playwright

async def generate_pdf_async(html_data_uri):
    """ Función asíncrona que lanza Playwright (sin cambios) """
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )
            page = await browser.new_page()
            await page.goto(html_data_uri, wait_until='networkidle')

            pdf_data = await page.pdf(
                format='A4',
                print_background=True,
                margin={ 'top': '2.5cm', 'bottom': '1.5cm', 'left': '1.5cm', 'right': '1.5cm'},
                display_header_footer=True,
                header_template='<span></span>',
                footer_template='<span></span>'
            )
            return pdf_data
        except Exception as e:
            print(f"Error al generar el PDF con Playwright (goto): {e}")
            return None
        finally:
            if browser:
                await browser.close()

def get_image_data_uri(image_path_relative):
    """ Lee una imagen y la devuelve como Data URI Base64 (sin cambios) """
    try:
        abs_path = os.path.join(settings.BASE_DIR, 'static', image_path_relative)
        ext = os.path.splitext(image_path_relative)[1].lower()
        mime_map = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.svg': 'image/svg+xml', '.ico': 'image/vnd.microsoft.icon'}
        mime_type = mime_map.get(ext, 'application/octet-stream')

        with open(abs_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        print(f"ADVERTENCIA: No se encontró el logo en {abs_path}")
        return None
    except Exception as e:
        print(f"Error al procesar el logo: {e}")
        return None

def sanitize_filename(name):
    """ Elimina caracteres no válidos para nombres de archivo """
    # Quita espacios al inicio/final
    name = name.strip()
    # Reemplaza espacios y caracteres no alfanuméricos (excepto guión bajo) con guión bajo
    name = re.sub(r'[^\w\-]+', '_', name)
    # Elimina guiones bajos múltiples
    name = re.sub(r'_+', '_', name)
    return name

def render_to_pdf(request, template_src, context_dict={}):
    """
    Carga plantilla, incrusta logo, codifica HTML, genera PDF
    y establece un nombre de archivo personalizado.
    """
    html_string = ""
    try:
        template_path = os.path.join(settings.BASE_DIR, 'app', 'core', 'templates', template_src)
        logo_path_relative = os.path.join('img', 'favicon.ico')
        logo_data_uri = get_image_data_uri(logo_path_relative)

        with open(template_path, 'r', encoding='utf-8') as f:
            raw_html = f.read()

        template = Template(raw_html)
        context_dict['request'] = request
        context_dict['logo_data_uri'] = logo_data_uri
        context = Context(context_dict)
        html_string = template.render(context)

        html_bytes = html_string.encode('utf-8')
        base64_html = base64.b64encode(html_bytes).decode('utf-8')
        html_data_uri = f'data:text/html;base64,{base64_html}'

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return HttpResponse(f"Error al cargar/renderizar/codificar la plantilla: {e}", status=500)

    pdf_data = asyncio.run(generate_pdf_async(html_data_uri))

    if pdf_data:
        response = HttpResponse(pdf_data, content_type='application/pdf')

        # --- INICIO: Nombre de Archivo Personalizado ---
        try:
            # Extraer datos del contexto
            nino = context_dict.get('nino')
            evaluacion = context_dict.get('game_session') # Recuerda que 'game_session' es el objeto Evaluacion

            if nino and evaluacion:
                # Sanitizar nombre del niño (quitar espacios, etc.)
                nino_name_sanitized = sanitize_filename(nino.nombre_completo)
                eval_id = evaluacion.id
                # Construir el nombre del archivo
                filename = f"Reporte_{nino_name_sanitized}_Eval_{eval_id}.pdf"
            else:
                # Nombre por defecto si falta información
                filename = "Reporte_DislexIA.pdf"

            # Establecer la cabecera Content-Disposition
            # 'inline' sugiere visualizar, 'attachment' fuerza descarga
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            # Si prefieres forzar la descarga siempre, usa:
            # response['Content-Disposition'] = f'attachment; filename="{filename}"'

        except Exception as e:
            print(f"Error al generar nombre de archivo: {e}")
            response['Content-Disposition'] = 'inline; filename="Reporte_DislexIA_Error.pdf"'
        # --- FIN: Nombre de Archivo Personalizado ---

        return response

    return HttpResponse('Error al generar el PDF.', status=500)