from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Lista de rotas (URLs) principais do projeto
urlpatterns = [
    # Rota para o painel administrativo nativo do Django
    path('admin/', admin.site.urls),
    
    # Rota raiz que inclui todas as URLs definidas dentro do aplicativo 'tickets'
    path('', include('tickets.urls')),
]

# Permite visualizar as imagens enviadas durante o desenvolvimento (DEBUG=True)
if settings.DEBUG:
    # Adiciona a rota estática para servir arquivos de mídia (uploads) localmente
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)