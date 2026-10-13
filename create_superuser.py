"""
Automated superuser creation script for Render deployment and local initialization.
Reads DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD
from environment or sets safe defaults for student evaluation.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema_portal.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@cineverse.local')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin12345')

if not User.objects.filter(username=username).exists():
    print(f"Creating default superuser '{username}' for Capstone assessment...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' successfully created!")
else:
    print(f"Superuser '{username}' already exists.")
