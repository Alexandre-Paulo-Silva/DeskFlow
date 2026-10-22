import os
from pathlib import Path
import mongoengine

# Define o caminho base do projeto na raiz
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta para criptografia do Django
SECRET_KEY = 'django-insecure-chave-secreta-mude-em-producao'

# Modo de depuração ativado para desenvolvimento
DEBUG = True

# Permite conexões de qualquer host
ALLOWED_HOSTS = ['*']

# Apps instalados no projeto, incluindo o app de chamados (tickets)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tickets',
]

# Camadas de middleware para segurança, sessões e autenticação
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuração do roteador de URLs principal
ROOT_URLCONF = 'core.urls'

# Configuração do mecanismo de templates HTML
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Configuração da aplicação WSGI
WSGI_APPLICATION = 'core.wsgi.application'

# Banco padrão do Django apenas para autenticação/sessões (SQLite ou leve)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- CONEXÃO MONGODB LOCAL (MongoEngine) ---
mongoengine.connect(
    db='sistema_chamados_db',
    host='localhost',
    port=27017
)

# Configurações de idioma e fuso horário
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Caminho dos arquivos estáticos e tipo de campo automático padrão
STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURAÇÕES DE AUTENTICAÇÃO ---
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'ticket_list'
LOGOUT_REDIRECT_URL = 'login'

# --- CONFIGURAÇÃO DE UPLOAD DE ARQUIVOS (MEDIA) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'