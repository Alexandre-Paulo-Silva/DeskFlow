from django.urls import path
from . import views

# Definição das rotas (URLs) do aplicativo 'tickets'
urlpatterns = [
    # Rota raiz: exibe o painel de listagem de chamados (página inicial)
    path('', views.ticket_list, name='ticket_list'),
    
    # Rota para a tela de autenticação (login)
    path('login/', views.login_view, name='login'),
    
    # Rota para o formulário de cadastro de novos usuários
    path('register/', views.register_view, name='register'),
    
    # Rota para encerrar a sessão do usuário (logout)
    path('logout/', views.logout_view, name='logout'),
    
    # Rota para gerenciar o perfil do usuário logado (alterar e-mail/senha)
    path('perfil/', views.profile_view, name='profile'),
    
    # Rota para o painel administrativo (posicionada antes de <str:ticket_id>/ para evitar conflito de roteamento)
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # Rota para a página de criação de um novo chamado/ticket
    path('novo/', views.ticket_create, name='ticket_create'),
    
    # Rota dinâmica para visualizar os detalhes de um chamado específico com base no ID
    path('<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    
    # Rota para a central de relatórios gerenciais e filtros em PDF do Administrador
    path('dashboard/relatorios/', views.admin_relatorios, name='admin_relatorios'),
]