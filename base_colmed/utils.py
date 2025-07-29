
import os
import firebase_admin
from firebase_admin import credentials, messaging
import jwt, requests, json
from django.core.cache import cache
from jwt import PyJWKClient, InvalidTokenError

#colmedaysen-firebase-adminsdk

APPLE_ISSUER  = "https://appleid.apple.com"
APPLE_AUDIENCE = ("org.colmed.aysen.app", "org.colmed.aysen.web")
JWKS_URL      = "https://appleid.apple.com/auth/keys"
CACHE_KEY     = "apple.jwks"
TTL_S         = 60*60*12


def get_signing_key(token: str):
    keys = cache.get(CACHE_KEY)
    # client = PyJWKClient(JWKS_URL, cache_keys=True, cache_time=TTL_S, jwks_data=keys)
    # signing_key = client.get_signing_key_from_jwt(token)
    # if client._jwks_cache_data:              # guarda la copia si se renovó
    #     cache.set(CACHE_KEY, client._jwks_cache_data, TTL_S)
    # return signing_key.key
    client = PyJWKClient(JWKS_URL, cache_keys=True, cache_time=TTL_S, jwks_data=keys)
    signing_key = client.get_signing_key_from_jwt(token)

    # guardar JWKS fresco usando la propiedad pública
    if client.jwks_data:
        cache.set(CACHE_KEY, client.jwks_data, TTL_S)
    return signing_key.key

# Inicializar Firebase Admin solo una vez
if not firebase_admin._apps:
    # Asumiendo que el archivo "serviceAccountKey.json" está en la raíz del proyecto
    cred_path = os.path.join(os.path.dirname(__file__), '..', 'colmedaysen-firebase-adminsdk.json')
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)


def send_push_notification(tokens, title, body, data_payload=None):
    """
    Envía una notificación push a un dispositivo dado el token FCM.
    
    :param token: Token FCM del dispositivo
    :param title: Título de la notificación
    :param body: Cuerpo del mensaje
    :param data: (Opcional) Diccionario con datos adicionales. En este caso debería ser el id del Evento (de ser necesario)
    """
    # server_key = settings.FCM_SERVER_KEY  # Debes definirlo en settings.py
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': f'key={server_key}'
    # }
    # message = {
    #     "to": token,
    #     "notification": {
    #         "title": title,
    #         "body": body,
    #         "sound": "default"
    #     },
    #     "data": data or {}
    # }
    # response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(message))
    # return response.json()

    # Si se envía más de un token, se usa el mensaje multicast
    if isinstance(tokens, list) and len(tokens) > 1:
        
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            tokens=tokens,
            data=data_payload or {}
        )
        response = messaging.send_multicast(message)
    else:
        
        # Si es un solo token o una lista con un único elemento
        token = tokens if isinstance(tokens, str) else tokens[0]
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
            data=data_payload or {}
        )
        response = messaging.send(message)
    
    return response