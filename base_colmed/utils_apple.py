
from django.core.cache import cache
from jwt import PyJWKClient


APPLE_ISSUER  = "https://appleid.apple.com"
APPLE_AUDIENCE = ("org.colmed.aysen.app", "org.colmed.aysen.web")
JWKS_URL      = "https://appleid.apple.com/auth/keys"
CACHE_KEY     = "apple.jwks"
TTL_S         = 60*60*12

def get_signing_key(token: str):
    keys = cache.get(CACHE_KEY)
    client = PyJWKClient(JWKS_URL, cache_keys=True, cache_time=TTL_S, jwks_data=keys)
    signing_key = client.get_signing_key_from_jwt(token)

    # guardar JWKS fresco usando la propiedad pública
    if client.jwks_data:
        cache.set(CACHE_KEY, client.jwks_data, TTL_S)
    return signing_key.key