from flask import Blueprint, redirect, request, session, url_for, flash, render_template_string, jsonify, Response, send_from_directory
import base64
import requests
from requests_oauthlib import OAuth2Session
import time
import uuid
import logging
import os
from datetime import datetime
 
from dotenv import load_dotenv
load_dotenv()
 
# Agregar después de las importaciones
 
print("==== DEBUG VARIABLES DE ENTORNO ====")
print(f"CLIENT_ID: {os.environ.get('CLIENT_ID')}")
print(f"REDIRECT_URI: {os.environ.get('REDIRECT_URI')}")
print(f"TENANT_ID: {os.environ.get('TENANT_ID')}")
 
print("===================================")
 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
 
# Esto se TIENE que BORRAR cuando tiremos a producción
# Sirve para permitir acceso desde cualquier URL sin que sea https
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
 
onedrive_bp = Blueprint("onedrive", __name__)

# Middleware para evitar interferencia con sistema de login principal
@onedrive_bp.before_request
def bypass_main_auth():
    """
    Evita que el sistema principal de autenticación interfiera con OneDrive
    """
    # Lista de rutas que NO deben ser interceptadas por el sistema principal
    onedrive_routes = [
        'callback', 'login_ms', 'check_auth_status', 
        'upload_ticket_image', 'proxy_image', 'debug_env'
    ]
    
    # Si es una ruta de OneDrive, marcar en sesión para bypass
    if request.endpoint and any(route in request.endpoint for route in onedrive_routes):
        session['_onedrive_auth_flow'] = True
        logger.info(f"OneDrive flow activado para: {request.endpoint}")

@onedrive_bp.after_request 
def cleanup_onedrive_flow(response):
    """
    Limpia el marcador de flujo OneDrive después de la respuesta
    """
    if '_onedrive_auth_flow' in session:
        session.pop('_onedrive_auth_flow', None)
    return response
 
# Variables de entorno de One Drive
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
TENANT_ID = os.environ.get('TENANT_ID')
 
# Determinar REDIRECT_URI dinámicamente basado en el entorno
REDIRECT_URI = os.environ.get('REDIRECT_URI', "http://localhost:5000/tickets/callback")
 
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
AUTH_URL = f"{AUTHORITY}/oauth2/v2.0/authorize"
TOKEN_URL = f"{AUTHORITY}/oauth2/v2.0/token"
 
print("==== DEBUG URLs GENERADAS ====")
print(f"AUTHORITY: {AUTHORITY}")
print(f"AUTH_URL: {AUTH_URL}")
print(f"TOKEN_URL: {TOKEN_URL}")
print("==============================")
 
SCOPES = ["Files.ReadWrite.All", "offline_access", "User.Read"]
 
@onedrive_bp.route("/login_ms")
def login_ms():
    """
    Inicia el flujo de autenticación con Microsoft.
    """
    # Guardar la URL de retorno en la sesión con mayor persistencia
    return_to = request.args.get('return_to')
    if return_to:
        session['ms_return_to'] = return_to
        session['ms_auth_source'] = 'tickets'  # Marcar que viene de tickets
        logger.info(f"URL de retorno guardada: {return_to}")
    else:
        # Si no se proporciona, intenta usar el referer
        referer = request.referrer
        if referer and '/tickets/' in referer:
            session['ms_return_to'] = referer
            session['ms_auth_source'] = 'tickets'
            logger.info(f"URL de retorno desde referer: {referer}")
        else:
            # URL por defecto para tickets
            session['ms_return_to'] = url_for("tickets.technical_service.list_tickets")
            session['ms_auth_source'] = 'tickets'
            logger.info("URL de retorno por defecto establecida")
   
    # Generar estado único para esta sesión
    import secrets
    state = secrets.token_urlsafe(32)
    session["ms_oauth_state"] = state
    session["ms_auth_timestamp"] = datetime.now().isoformat()
    
    # Usar las variables directamente del módulo en lugar de environment
    oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI, scope=SCOPES)
    auth_url, oauth_state = oauth.authorization_url(AUTH_URL, state=state)
    
    logger.info(f"Redirigiendo a Microsoft con estado: {state}")
    return redirect(auth_url)
 
# Webhook que recibe las notificaciones
@onedrive_bp.route("/callback")
def callback_ms():
    """
    Ruta de callback que recibe el código de autorización de Microsoft,
    solicita el token de acceso y lo almacena en la sesión.
    """
    logger.info("=== INICIO CALLBACK ONEDRIVE ===")
    logger.info(f"URL completa: {request.url}")
    logger.info(f"Args: {request.args}")
    logger.info(f"Sesión actual: {dict(session)}")
   
    if request.args.get("error"):
        error = request.args.get("error")
        error_description = request.args.get("error_description", "No details provided")
        logger.error(f"OAuth error: {error} - {error_description}")
        flash(f"Error de autenticación: {error_description}", "danger")
        
        # Redirigir a la URL de origen o lista de tickets
        return_to = session.get('ms_return_to', url_for("tickets.technical_service.list_tickets"))
        return redirect(return_to)
   
    received_state = request.args.get('state', '')
    stored_state = session.get('ms_oauth_state', '')
    logger.info(f"Estado recibido: {received_state}")
    logger.info(f"Estado guardado: {stored_state}")
   
    if not received_state or received_state != stored_state:
        logger.warning("Estado no coincide o está vacío")
        flash("Error de seguridad en la autenticación. Intenta de nuevo.", "warning")
        return_to = session.get('ms_return_to', url_for("tickets.technical_service.list_tickets"))
        return redirect(return_to)
   
    try:
        logger.info("Intentando obtener token de acceso...")
        
        # Crear OAuth session sin state (ya validado)
        oauth = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI)
        token = oauth.fetch_token(
            TOKEN_URL,
            client_secret=CLIENT_SECRET,
            authorization_response=request.url
        )
       
        logger.info("Token obtenido correctamente")
        logger.info(f"Token info: access_token={'*' * 10}, expires_in={token.get('expires_in')}")
        
        # Guardar token en sesión
        session["ms_token"] = token
        session["ms_authenticated"] = True
        session["ms_auth_time"] = datetime.now().isoformat()
       
        # Limpiar variables temporales de autenticación
        session.pop('ms_oauth_state', None)
        session.pop('ms_auth_timestamp', None)
       
        # Obtener la URL de retorno
        return_to = session.get('ms_return_to')
        auth_source = session.get('ms_auth_source', 'unknown')
        
        logger.info(f"URL de retorno: {return_to}")
        logger.info(f"Fuente de autenticación: {auth_source}")
       
        # Validar URL de retorno
        if not return_to:
            return_to = url_for('tickets.technical_service.list_tickets')
            logger.info("No había URL de retorno, usando lista de tickets")
        elif not return_to.startswith('/tickets/'):
            # Si no es una URL de tickets, redirigir a tickets
            return_to = url_for('tickets.technical_service.list_tickets')
            logger.info("URL de retorno no es de tickets, redirigiendo a lista")
        
        # Limpiar variables de retorno
        session.pop('ms_return_to', None)
        session.pop('ms_auth_source', None)
       
        flash("✅ Conexión con OneDrive establecida correctamente", "success")
        logger.info(f"Redirigiendo a: {return_to}")
        
        return redirect(return_to)
        
    except Exception as e:
        logger.error(f"Error al obtener token: {str(e)}", exc_info=True)
        flash(f"Error al conectar con OneDrive: {str(e)}", "danger")
        
        # Limpiar variables de autenticación en caso de error
        for key in ['ms_oauth_state', 'ms_auth_timestamp', 'ms_return_to', 'ms_auth_source']:
            session.pop(key, None)
        
        return redirect(url_for("tickets.technical_service.list_tickets"))
 
@onedrive_bp.route("/upload_ms", methods=["GET", "POST"])
def upload_ms():
    """
    Si se accede vía GET muestra un formulario de subida;
    si es POST, se procesa la imagen y se sube.
    """
    if "ms_token" not in session:
        flash("Debés iniciar sesión para continuar", "warning")
        return redirect(url_for("tickets.onedrive.login_ms"))
   
    access_token = session["ms_token"]["access_token"]
 
    if request.method == "POST":
        file = request.files.get("image")
        if not file:
            flash("No seleccionaste un archivo", "warning")
            return redirect(url_for("tickets.onedrive.upload_ms"))
 
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": file.content_type
        }
        filename = file.filename
        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{filename}:/content"
 
        response = requests.put(upload_url, headers=headers, data=file.stream)
        if response.status_code in [200, 201]:
            flash("Imagen subida exitosamente a OneDrive", "success")
        else:
            flash(f"Error al subir imagen: {response.text}", "danger")
        return redirect(url_for("tickets.onedrive.upload_ms"))
 
    form_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Subir Imagen a OneDrive</title>
    </head>
    <body>
        <h1>Subir imagen a OneDrive</h1>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*" required>
            <button type="submit">Subir</button>
        </form>
        <p><a href="{{ url_for('tickets.onedrive.login_ms') }}">Reiniciar autenticación</a></p>
    </body>
    </html>
    {% if not ms_authenticated %}
    <div class="alert alert-warning mt-2 mb-3">
        <p><i class="fas fa-exclamation-triangle me-2"></i> Para subir imágenes, primero debes
           <a href="{{ url_for('tickets.onedrive.login_ms', return_to=request.path) }}" class="btn btn-primary btn-sm ms-2">
               <i class="fab fa-microsoft me-1"></i> Iniciar sesión con OneDrive
           </a>
        </p>
    </div>
    {% else %}
    <div class="alert alert-success mt-2 mb-3">
        <p><i class="fas fa-check-circle me-2"></i> Conectado a OneDrive. Puedes subir imágenes.</p>
    </div>
    {% endif %}
    """
    return render_template_string(form_html)
 
@onedrive_bp.route("/upload_ticket_image", methods=["POST"])
def upload_ticket_image():
    """
    API endpoint para subir imágenes de tickets a OneDrive.
    Se usa con el token de .env
    """
    print("=== UPLOAD_TICKET_IMAGE CALLED ===")
    print(f"Request method: {request.method}")
    print(f"Form data: {request.form}")
    print(f"Files: {request.files}")
   
    if "ms_token" not in session:
        print("Error: No authentication token in session")
        return jsonify({"success": False, "error": "No autenticado"}), 401
   
    access_token = session["ms_token"]["access_token"]
    ticket_id = request.form.get("ticket_id")
   
    print(f"Processing upload for ticket ID: {ticket_id}")
   
    if not ticket_id:
        print("Error: No ticket ID provided")
        return jsonify({"success": False, "error": "ID de ticket no proporcionado"}), 400
   
    folder_path = f"WeekPilot/Tickets/{ticket_id}"
   
    folder_exists, folder_error = ensure_folder_exists(access_token, folder_path)
    if not folder_exists:
        print(f"Error ensuring folder exists: {folder_error}")
        return jsonify({"success": False, "error": f"Error creating folder: {folder_error}"}), 500
   
    files = request.files.getlist("images")
    print(f"Number of files to upload: {len(files)}")
   
    uploaded_images = []
   
    for index, file in enumerate(files):
        if file:
            print(f"Processing file {index+1}: {file.filename}")
            filename = f"{uuid.uuid4()}_{file.filename}"
           
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": file.content_type
            }
           
            # ESTA ES LA URL QUE SE USA PARA AÑADIR A LA CARPETA CON EL PATH
            upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}/{filename}:/content"
           
            print(f"Uploading to: {upload_url}")
           
            try:
                response = requests.put(upload_url, headers=headers, data=file.stream)
                print(f"Upload response: {response.status_code}")
               
                if response.status_code in [200, 201]:
                    file_data = response.json()
                    file_id = file_data.get("id")
                   
                    print(f"File uploaded, ID: {file_id}")
                   
                    share_response = requests.post(
                        f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/createLink",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json"
                        },
                        json={"type": "view", "scope": "anonymous"}
                    )
                   
                    print(f"Share response: {share_response.status_code}")
                   
                    if share_response.status_code == 200:
                        share_data = share_response.json()
                        web_url = share_data.get("link", {}).get("webUrl")
                       
                        print(f"Share URL: {web_url}")
                       
                        uploaded_images.append({
                            "id": file_id,
                            "name": filename,
                            "url": web_url
                        })
                    else:
                        error_text = share_response.text
                        print(f"Error sharing file: {error_text}")
                else:
                    error_text = response.text
                    print(f"Error uploading file: {error_text}")
                    return jsonify({"success": False, "error": f"Error uploading file: {error_text}"}), 500
            except Exception as e:
                print(f"Exception uploading file: {str(e)}")
                return jsonify({"success": False, "error": f"Connection error: {str(e)}"}), 500
   
    print(f"Upload complete. Uploaded images: {len(uploaded_images)}")
    return jsonify({"success": True, "images": uploaded_images})
 
def ensure_folder_exists(access_token, folder_path):
    folders = folder_path.split('/')
    current_path = ""
   
    for folder in folders:
        if not folder:
            continue
           
        if current_path:
            current_path += f"/{folder}"
        else:
            current_path = folder
           
        check_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{current_path}"
        check_response = requests.get(
            check_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
       
        if check_response.status_code == 404:
            folder_create = requests.post(
                "https://graph.microsoft.com/v1.0/me/drive/root/children",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": folder,
                    "folder": {},
                    "@microsoft.graph.conflictBehavior": "rename"
                }
            )
           
            if folder_create.status_code not in [200, 201]:
                return False, folder_create.text
               
    return True, current_path
 
def refresh_token():
    """
    Actualiza el token de acceso si ha expirado, lo que exige volver a loguearse
    """
    if "ms_token" not in session:
        return False
   
    token = session["ms_token"]
    now = int(time.time())
   
    # Si el token expira en menos de 5 minutos, refrescarlo
    if token.get("expires_at", 0) - now < 300:
        try:
            oauth = OAuth2Session(CLIENT_ID, token=token)
            refreshed_token = oauth.refresh_token(
                TOKEN_URL,
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                refresh_token=token.get("refresh_token")
            )
            session["ms_token"] = refreshed_token
            return True
        except Exception as e:
            logger.error(f"Error al refrescar token: {e}")
            return False
   
    return True
 
@onedrive_bp.route("/check_auth_status")
def check_auth_status():
    """
    Endpoint para verificar el estado de autenticación con Microsoft.
    """
    auth_info = {
        "authenticated": False,
        "token_exists": "ms_token" in session,
        "auth_timestamp": session.get("ms_auth_time"),
        "debug_session_keys": list(session.keys())
    }
    
    if "ms_token" not in session:
        auth_info["error"] = "No MS token in session"
        return jsonify(auth_info)
   
    # Verificar que el token sea válido
    token_valid = refresh_token()
   
    if not token_valid:
        auth_info["error"] = "Token invalid or expired"
        return jsonify(auth_info)
   
    auth_info["authenticated"] = True
    auth_info["token_type"] = session["ms_token"].get("token_type", "unknown")
    auth_info["expires_in"] = session["ms_token"].get("expires_in", 0)
    
    return jsonify(auth_info)
 
def get_ticket_images(ticket_id):
    """
    Recupera todas las imágenes almacenadas para un ticket específico desde OneDrive.
   
    Args:
        ticket_id: ID del ticket para buscar sus imágenes
       
    Returns:
        list: Lista de diccionarios con información de cada imagen (id, name, url)
        None: Si hay un error o no hay token de autenticación
    """
    if "ms_token" not in session:
        logger.warning("No hay token de Microsoft disponible")
        return None
   
    if not refresh_token():
        logger.warning("Token inválido o no se pudo refrescar")
        return None
   
    access_token = session["ms_token"]["access_token"]
    folder_path = f"WeekPilot/Tickets/{ticket_id}"
   
    folder_exists, _ = ensure_folder_exists(access_token, folder_path)
    if not folder_exists:
        logger.warning(f"La carpeta del ticket {ticket_id} no existe")
        return []
   
    # URL DE LA PAGINA
    list_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{folder_path}:/children"
   
    try:
        response = requests.get(
            list_url,
            headers={"Authorization": f"Bearer {access_token}"}
        )
       
        if response.status_code != 200:
            logger.error(f"Error al consultar archivos: {response.status_code} - {response.text}")
            return []
       
        data = response.json()
        files = []
       
        for item in data.get("value", []):
            if "file" in item:  
                file_id = item.get("id")
                file_name = item.get("name")
               
                proxy_url = url_for('tickets.onedrive.proxy_image', file_id=file_id, _external=True)
               
                files.append({
                    "id": file_id,
                    "name": file_name,
                    "url": proxy_url
                })
       
        logger.info(f"Encontradas {len(files)} imágenes para el ticket {ticket_id}")
        return files
   
    except Exception as e:
        logger.error(f"Error recuperando imágenes de ticket {ticket_id}: {str(e)}")
        return []
 
@onedrive_bp.route('/proxy_image/<file_id>')
def proxy_image(file_id):
    """
    Actúa como proxy para entregar imágenes de OneDrive evitando problemas CORS
    """
    if "ms_token" not in session:
        return redirect(url_for('tickets.static', filename='img/not-authenticated.png'))
   
    if not refresh_token():
        return redirect(url_for('tickets.static', filename='img/token-expired.png'))
   
    access_token = session["ms_token"]["access_token"]
   
    # ACCEDE A LA CARPETA
    content_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
   
    try:
        response = requests.get(
            content_url,
            headers={"Authorization": f"Bearer {access_token}"},
            stream=True
        )
       
        if response.status_code != 200:
            logger.error(f"Error al obtener imagen {file_id}: {response.status_code}")
            return redirect(url_for('tickets.static', filename='img/error.png'))
       
        content_type = response.headers.get('content-type', 'image/jpeg')
       
        flask_response = Response(
            response=response.content,
            status=200,
            mimetype=content_type
        )
       
        flask_response.headers['Cache-Control'] = 'public, max-age=86400'
       
        return flask_response
       
    except Exception as e:
        logger.error(f"Error al obtener imagen {file_id}: {str(e)}")
        return redirect(url_for('tickets.static', filename='img/error.png'))
 
 
# PARA BORRAR (A CONFIRMACIÓN SI LO DEJAMOS O NO)
def delete_onedrive_images(image_ids):
    """
    Elimina imágenes de OneDrive por su ID
   
    Args:
        image_ids (list): Lista de IDs de imágenes a eliminar
       
    Returns:
        tuple: (bool, str) - Éxito y mensaje
    """
    if not image_ids:
        return True, "No hay imágenes para eliminar"
   
    if "ms_token" not in session:
        return False, "No hay sesión activa con Microsoft"
   
    if not refresh_token():
        return False, "El token ha expirado y no se pudo refrescar"
   
    access_token = session["ms_token"]["access_token"]
    success_count = 0
    errors = []
   
    for image_id in image_ids:
        try:
            delete_url = f"https://graph.microsoft.com/v1.0/me/drive/items/{image_id}"
            response = requests.delete(
                delete_url,
                headers={"Authorization": f"Bearer {access_token}"}
            )
           
            if response.status_code in [204, 200]:  # 204 No Content es éxito
                success_count += 1
                logger.info(f"Imagen {image_id} eliminada correctamente")
            else:
                error_msg = f"Error al eliminar imagen {image_id}: {response.status_code}"
                logger.error(error_msg)
                errors.append(error_msg)
        except Exception as e:
            error_msg = f"Excepción al eliminar imagen {image_id}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
   
    if errors:
        return False, f"Se eliminaron {success_count} de {len(image_ids)} imágenes. Errores: {', '.join(errors)}"
    else:
        return True, f"Se eliminaron {success_count} imágenes correctamente"
 
@onedrive_bp.route("/debug_session")
def debug_session():
    """
    Endpoint para depurar el estado de la sesión (solo para desarrollo)
    """
    import time
   
    session_data = {
        "ms_token_exists": "ms_token" in session,
        "return_to": session.get("return_to", "No definido"),
        "oauth_state": session.get("oauth_state", "No definido"),
    }
   
    if "ms_token" in session:
        token = session["ms_token"]
        now = int(time.time())
        expires_at = token.get("expires_at", 0)
        session_data["token_expires_in"] = expires_at - now
        session_data["token_valid"] = expires_at > now
   
    return jsonify(session_data)
 
 
@onedrive_bp.route("/debug_env")
def debug_env():
    """
    Endpoint para verificar que las variables de entorno se estén leyendo correctamente
    """
    debug_info = {
        "CLIENT_ID": os.environ.get('CLIENT_ID'),
        "CLIENT_SECRET": os.environ.get('CLIENT_SECRET')[:10] + "..." if os.environ.get('CLIENT_SECRET') else None,
        "REDIRECT_URI": os.environ.get('REDIRECT_URI'),
        "Current CLIENT_ID in module": CLIENT_ID,
        "Current REDIRECT_URI in module": REDIRECT_URI,
        ".env file exists": os.path.exists('.env'),
        "Working directory": os.getcwd()
    }
   
    return jsonify(debug_info)

@onedrive_bp.route("/test_auth_flow")
def test_auth_flow():
    """
    Endpoint para probar el flujo completo de autenticación
    """
    return f"""
    <html>
    <head>
        <title>Test OneDrive Auth Flow</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .container {{ max-width: 800px; }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .success {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }}
            .error {{ background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }}
            .btn {{ padding: 10px 20px; margin: 5px; text-decoration: none; border-radius: 5px; color: white; }}
            .btn-primary {{ background: #007bff; }}
            .btn-success {{ background: #28a745; }}
            .info {{ background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔒 Test OneDrive Authentication Flow</h1>
            
            <div class="info">
                <h3>Prueba el flujo completo de autenticación con OneDrive</h3>
                <p>Este endpoint te permite probar y debuggear el proceso de autenticación paso a paso.</p>
            </div>
            
            <h2>Estado Actual</h2>
            <div id="status-info">Cargando...</div>
            
            <h2>Acciones</h2>
            <a href="/tickets/login_ms?return_to=/tickets/test_auth_flow" class="btn btn-primary">
                🚀 Iniciar Autenticación OneDrive
            </a>
            
            <a href="/tickets/check_auth_status" class="btn btn-success">
                ✅ Verificar Estado de Autenticación
            </a>
            
            <h2>URLs Importantes</h2>
            <ul>
                <li><strong>Login:</strong> <code>/tickets/login_ms</code></li>
                <li><strong>Callback:</strong> <code>/tickets/callback</code></li>
                <li><strong>Estado:</strong> <code>/tickets/check_auth_status</code></li>
                <li><strong>Variables:</strong> <code>/tickets/debug_env</code></li>
            </ul>
            
            <h2>Información de Sesión</h2>
            <pre id="session-info">Cargando...</pre>
        </div>
        
        <script>
            // Cargar estado de autenticación
            fetch('/tickets/check_auth_status')
                .then(response => response.json())
                .then(data => {{
                    const statusDiv = document.getElementById('status-info');
                    if (data.authenticated) {{
                        statusDiv.innerHTML = '<div class="status success">✅ Autenticado correctamente con OneDrive</div>';
                    }} else {{
                        statusDiv.innerHTML = '<div class="status warning">⚠️ No autenticado: ' + (data.error || 'Token no encontrado') + '</div>';
                    }}
                    
                    document.getElementById('session-info').textContent = JSON.stringify(data, null, 2);
                }})
                .catch(error => {{
                    document.getElementById('status-info').innerHTML = '<div class="status error">❌ Error al verificar estado: ' + error + '</div>';
                }});
        </script>
    </body>
    </html>
    """
