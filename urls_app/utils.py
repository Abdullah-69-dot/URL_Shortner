import string
import secrets
from django.apps import apps

def generate_short_code(length=6):
    """
    Generates a random base62 short code.
    Base62 includes [a-z, A-Z, 0-9].
    """
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def get_unique_short_code():
    """
    Generates a short code and ensures it doesn't already exist in the database.
    Retries until a unique code is found.
    """
    URL = apps.get_model('urls_app', 'URL')
    while True:
        code = generate_short_code()
        if not URL.objects.filter(short_code=code).exists():
            return code
