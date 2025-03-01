
import os
import firebase_admin
from firebase_admin import credentials, messaging

#colmedaysen-firebase-adminsdk



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