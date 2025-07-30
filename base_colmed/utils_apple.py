
# from django.core.cache import cache
# from jwt import PyJWKClient


# APPLE_ISSUER  = "https://appleid.apple.com"
# APPLE_AUDIENCE = ("org.colmed.aysen.app", "org.colmed.aysen.web")
# JWKS_URL      = "https://appleid.apple.com/auth/keys"
# CACHE_KEY     = "apple.jwks"
# TTL_S         = 60*60*12

# def get_signing_key(token: str):
#     keys = cache.get(CACHE_KEY)
#     client = PyJWKClient(JWKS_URL, cache_keys=True, cache_time=TTL_S, jwks_data=keys)
#     signing_key = client.get_signing_key_from_jwt(token)

#     # guardar JWKS fresco usando la propiedad pública
#     if client.jwks_data:
#         cache.set(CACHE_KEY, client.jwks_data, TTL_S)
#     return signing_key.key

from django.core.cache import cache
from jwt import PyJWKClient

APPLE_ISSUER   = "https://appleid.apple.com"
APPLE_AUDIENCE = ("org.colmed.aysen.app", "org.colmed.aysen.web")
JWKS_URL       = "https://appleid.apple.com/auth/keys"

CACHE_KEY = "apple.jwks"
TTL_S     = 60 * 60 * 12     # 12 h

def get_signing_key(token: str):
    """
    Devuelve la clave pública (RSA) que firma *token*.

    Compatible con PyJWT 2.4 → 2.10.  
    No usa argumentos privados de la librería.
    """
    # 1) Intentar cargar JWKS desde caché externo
    jwks_cached = cache.get(CACHE_KEY)

    # 2) Crear el cliente con caché en memoria
    client = PyJWKClient(JWKS_URL, cache_keys=True)

    # 3) Si había JWKS en caché, inyectarlo (API interna pero estable desde 2.0)
    if jwks_cached:
        client._jwks_data = jwks_cached

    # 4) Obtener la clave que coincide con el 'kid' del JWT
    signing_key = client.get_signing_key_from_jwt(token)

    # 5) Guardar el JWKS actualizado para futuros procesos
    fresh_jwks = getattr(client, "_jwks_data", None)
    if fresh_jwks:
        cache.set(CACHE_KEY, fresh_jwks, TTL_S)

    return signing_key.key