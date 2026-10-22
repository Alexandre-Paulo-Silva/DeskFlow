#  DeskFlow — Enterprise Helpdesk & Ticketing System

> Um sistema de helpdesk e gerenciamento de chamados corporativos moderno, seguro e de alta performance, desenvolvido com arquitetura de banco de dados híbrida e design system profissional.

---

## Sobre o Projeto

O **DeskFlow** é uma aplicação web full-stack projetada para otimizar o fluxo de suporte técnico e atendimento em ambientes corporativos. O sistema conta com controle de acesso baseado em papéis (RBAC), painel administrativo completo, anexo de arquivos, sistema de comentários dinâmicos e geração automatizada de relatórios executivos em PDF.

---

## Tecnologias Utilizadas

Este projeto foi construído utilizando um conjunto robusto de ferramentas modernas de mercado:

* **Backend & Lógica:** Python 3.x, Django Framework
* **Banco de Dados Relacional (Auth/Admin):** SQLite (Gerenciamento de usuários, sessões e permissões nativas do Django)
* **Banco de Dados NoSQL (Documentos/Tickets):** MongoDB via *MongoEngine ODM* (Armazenamento flexível de chamados e comentários embutidos)
* **Interface & Estilização:** Tailwind CSS & Phosphor Icons (Layout responsivo com suporte a modo escuro/claro e componentes modernos)
* **Manipulação de Arquivos:** Django `FileSystemStorage` para upload de anexos e prints de tela
* **Geração de Documentos:** ReportLab (Geração dinâmica de relatórios gerenciais em PDF com filtros customizados)

---

##  Principais Funcionalidades

###  1. Autenticação e Controle de Acesso (RBAC)
* **Cliente / Solicitante:** Abre chamados, acompanha o status em tempo real, interage via comentários e envia anexos.
* **Técnico / Staff:** Assume chamados, atualiza o andamento do suporte e gerencia o ciclo de vida dos tickets.
* **Administrador (Superuser):** Possui acesso total ao painel administrativo (`/dashboard/`), podendo monitorar métricas globais, excluir tickets corrompidos ou gerenciar usuários cadastrados.

###  2. Gestão Completa de Chamados
* Abertura de tickets categorizados (T.I., Financeiro, RH, Infraestrutura, etc.) com níveis de prioridade (Baixa, Média, Alta, Crítica).
* Sistema de histórico de comentários em tempo real acoplado diretamente aos documentos do MongoDB.
* Suporte a upload de arquivos e imagens para evidências de problemas.

###  3. Relatórios Gerenciais em PDF
* Central exclusiva para administradores filtrarem chamados por *Status* e *Categoria*.
* Geração instantânea de relatórios corporativos em PDF formatados profissionalmente com paginação dinâmica, cabeçalhos estilizados e efeito zebrado nas tabelas via **ReportLab**.

---

##  Como Executar o Projeto Localmente

Siga os passos abaixo para configurar e rodar o projeto na sua máquina:

### 1. Pré-requisitos
* Python instalado (versão 3.10 ou superior)
* Servidor MongoDB rodando localmente (porta padrão `27017`)

### 2. Clonar o repositório e configurar o ambiente virtual
```bash
# Clone o repositório
git clone [https://github.com/Alexandre-Paulo-Silva/DeskFlow.git](https://github.com/Alexandre-Paulo-Silva/DeskFlow.git)
cd deskflow

# Crie e ative o ambiente virtual
python -m venv venv
# No Windows:
venv\Scripts\activate
# No Linux/Mac:
source venv/bin/activate

#dependencias
pip install -r requirements.txt
django>=4.2,<5.0
mongoengine>=0.28.0
reportlab>=4.0.0
pymongo>=4.6.0

