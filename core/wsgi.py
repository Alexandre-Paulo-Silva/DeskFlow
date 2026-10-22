import os
from django.core.wsgi import get_wsgi_application

# Define a variável de ambiente padrão que aponta para o arquivo de configurações do projeto Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Inicializa a aplicação WSGI (Web Server Gateway Interface), usada para servir o projeto em servidores web
application = get_wsgi_application()